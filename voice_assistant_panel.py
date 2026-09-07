"""
features/ai_voice_assistant/ui/voice_assistant_panel.py
=========================================================
Real-time AI Voice Assistant using Gemini Live API.
"""
from __future__ import annotations

import asyncio
import logging
import sqlite3
import threading
from datetime import datetime

import pyaudio
try:
    from google import genai
except Exception:
    genai = None
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget,
)

from ui.theme import Colors, Fonts, Spacing
from bridge.clipboard_manager import copy_to_clipboard

log = logging.getLogger(__name__)

CHANNELS         = 1
SEND_SAMPLE_RATE = 16000
RECV_SAMPLE_RATE = 24000
CHUNK_SIZE       = 1024

_DEFAULT_MODEL = "models/gemini-3.1-flash-live-preview"
_DEFAULT_SYSTEM = (
    "You are a helpful, friendly AI voice assistant. "
    "Listen carefully to what the user says and respond naturally in a conversational tone. "
    "Keep your answers concise and clear."
)


def _load_assistant_models():
    _CORRECTIONS = {
        "gemini-3.1-flash-live":         "gemini-3.1-flash-live-preview",
        "gemini-3-flash-live":           "gemini-3.1-flash-live-preview",
        "gemini-2.5-native-audio":       "gemini-2.5-flash-native-audio-preview-12-2025",
        "gemini-2.5-flash-native-audio": "gemini-2.5-flash-native-audio-preview-12-2025",
        "gemini-2.5-flash-preview-native-audio-dialog": "gemini-2.5-flash-native-audio-preview-12-2025",
        "gemini-2.0-flash-live":         "gemini-2.0-flash-live-001",
    }
    _TOP_DEFAULTS = [
        ("* Gemini 3.1 Flash Live  (Recommended)", "models/gemini-3.1-flash-live-preview"),
        ("* Gemini 2.5 Flash Native Audio Dialog",  "models/gemini-2.5-flash-native-audio-preview-12-2025"),
    ]
    try:
        from config import APP_DB
        if not APP_DB.exists():
            return _TOP_DEFAULTS
        con = sqlite3.connect(str(APP_DB))
        cur = con.cursor()
        cur.execute("""
            SELECT m.name, m.api_name
            FROM   models m JOIN categories c ON m.category_id = c.id
            WHERE  m.active = 1 AND c.slug = 'audio'
              AND  (LOWER(m.api_name) LIKE '%live%' OR LOWER(m.api_name) LIKE '%native%')
            ORDER BY
                CASE WHEN LOWER(m.api_name) LIKE '%3.1%' OR LOWER(m.api_name) LIKE '%flash-live%'
                     THEN 0 ELSE 1 END, m.sort_order
        """)
        top_rows = cur.fetchall()
        cur.execute("""
            SELECT m.name, m.api_name
            FROM   models m JOIN categories c ON m.category_id = c.id
            WHERE  m.active = 1
              AND  NOT (c.slug = 'audio' AND (LOWER(m.api_name) LIKE '%live%' OR LOWER(m.api_name) LIKE '%native%'))
            ORDER BY m.sort_order
        """)
        other_rows = cur.fetchall()
        con.close()
        def normalise(rows, star=False):
            seen = set(); out = []
            for name, api_name in rows:
                real = _CORRECTIONS.get(api_name, api_name)
                mid = real if real.startswith("models/") else f"models/{real}"
                if mid not in seen:
                    seen.add(mid)
                    out.append((("* " if star else "") + name, mid))
            return out
        top = normalise(top_rows, star=True)
        other = normalise(other_rows)
        if not top and not other:
            return _TOP_DEFAULTS
        result = list(top)
        if other:
            if top:
                result.append(("----- Other Models -----", None))
            result.extend(other)
        return result
    except Exception as e:
        log.warning("Could not load models: %s", e)
        return _TOP_DEFAULTS


class _ChatBubble(QFrame):
    def __init__(self, role, text, timestamp, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        is_user = role == "user"
        bg = "#e8f4fd" if is_user else "#f0fdf4"
        border = "#93c5fd" if is_user else "#86efac"
        align = Qt.AlignRight if is_user else Qt.AlignLeft
        self.setStyleSheet(f"QFrame {{ background:{bg}; border:1.5px solid {border}; border-radius:12px; margin:2px 0; }}")
        vl = QVBoxLayout(self)
        vl.setContentsMargins(12, 8, 12, 8)
        vl.setSpacing(4)
        meta = QLabel(("You" if is_user else "AI Assistant") + "  *  " + timestamp)
        meta.setStyleSheet(f"color:{'#1d4ed8' if is_user else '#15803d'}; font-size:10px; font-weight:700; background:transparent; border:none;")
        meta.setAlignment(align)
        vl.addWidget(meta)
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg.setStyleSheet(f"color:{Colors.TEXT_PRIMARY}; font-size:13px; background:transparent; border:none;")
        msg.setAlignment(align)
        vl.addWidget(msg)
        self._text = text

    def text(self):
        return self._text


class VoiceAssistantPanel(QWidget):
    _sig_user_text = Signal(str)
    _sig_ai_text   = Signal(str)
    _sig_connected = Signal()
    _sig_disconn   = Signal(str)
    _sig_error     = Signal(str)
    _sig_status    = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background-color: {Colors.BG_APP};")
        self._thread = None
        self._loop = None
        self._stop_event = None
        self._running = False
        self._sig_user_text.connect(self._on_user_text)
        self._sig_ai_text.connect(self._on_ai_text)
        self._sig_connected.connect(self._on_connected)
        self._sig_disconn.connect(self._on_disconnected)
        self._sig_error.connect(self._on_error)
        self._sig_status.connect(self._set_status)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        root.setSpacing(Spacing.MD)
        root.addWidget(self._build_header())
        root.addWidget(self._build_toolbar())
        self._sys_frame = self._build_system_prompt()
        self._sys_frame.setVisible(False)   # hidden by default — toggle via toolbar button
        root.addWidget(self._sys_frame)
        root.addWidget(self._build_chat_area(), 1)
        root.addWidget(self._build_bottom_bar())

    def _build_header(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w); v.setContentsMargins(0,0,0,0); v.setSpacing(2)
        h = QHBoxLayout(); h.setContentsMargins(0,0,0,0)
        t = QLabel("AI Voice Assistant")
        t.setStyleSheet(f"font-size:{Fonts.SIZE_XL}px; font-weight:700; color:{Colors.TEXT_PRIMARY}; background:transparent;")
        h.addWidget(t); h.addStretch()
        self._status_lbl = QLabel("Ready")
        self._status_lbl.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:11px; background:transparent;")
        h.addWidget(self._status_lbl); v.addLayout(h)
        sub = QLabel("Speak naturally  --  Gemini responds in real-time audio + text")
        sub.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:11px; background:transparent;")
        v.addWidget(sub)
        return w

    def _build_toolbar(self):
        bar = QWidget()
        bar.setStyleSheet(f"background:#ffffff; border:1px solid {Colors.BORDER}; border-radius:10px;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        bl.setSpacing(Spacing.SM)
        bl.addWidget(self._lbl("Model:"))
        self._model_combo = QComboBox()
        self._model_combo.setFixedWidth(320)
        for label, model_id in _load_assistant_models():
            if model_id is None:
                idx = self._model_combo.count()
                self._model_combo.addItem(label)
                item = self._model_combo.model().item(idx)
                item.setEnabled(False)
                item.setForeground(QColor("#aaaaaa"))
            else:
                self._model_combo.addItem(label, model_id)
        self._model_combo.setCurrentIndex(0)
        bl.addWidget(self._model_combo)
        bl.addWidget(self._vline())
        bl.addWidget(self._lbl("Microphone:"))
        self._mic_combo = QComboBox()
        self._mic_combo.setFixedWidth(220)
        self._populate_mics()
        bl.addWidget(self._mic_combo)
        bl.addWidget(self._vline())
        self._echo_chk = QCheckBox("Echo AI voice")
        self._echo_chk.setChecked(True)
        self._echo_chk.setStyleSheet(f"color:{Colors.TEXT_SECONDARY}; font-size:12px; background:transparent;")
        bl.addWidget(self._echo_chk)
        bl.addStretch()
        # System Prompt toggle button
        self._sys_toggle_btn = QPushButton("System Prompt")
        self._sys_toggle_btn.setFixedHeight(32)
        self._sys_toggle_btn.setCursor(Qt.PointingHandCursor)
        self._sys_toggle_btn.setCheckable(True)
        self._sys_toggle_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{Colors.TEXT_SECONDARY}; "
            f"border:1px solid {Colors.BORDER}; border-radius:8px; font-size:12px; padding:4px 14px; }}"
            f"QPushButton:checked {{ background:{Colors.ACCENT}; color:#fff; border-color:{Colors.ACCENT}; }}"
            f"QPushButton:hover {{ border-color:{Colors.ACCENT}; color:{Colors.ACCENT}; }}"
        )
        self._sys_toggle_btn.toggled.connect(self._toggle_sys_prompt)
        bl.addWidget(self._sys_toggle_btn)
        for label, slot, err_color in [
            ("  Copy Chat", self._copy_chat, Colors.ACCENT),
            ("  Clear",     self._clear_chat, Colors.ERROR),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton {{ background:transparent; color:{Colors.TEXT_SECONDARY}; "
                f"border:1px solid {Colors.BORDER}; border-radius:8px; font-size:12px; padding:4px 14px; }}"
                f"QPushButton:hover {{ border-color:{err_color}; color:{err_color}; }}"
            )
            btn.clicked.connect(slot)
            bl.addWidget(btn)
        bl.addWidget(self._vline())
        self._start_btn = QPushButton("  Start")
        self._start_btn.setFixedHeight(34)
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.setStyleSheet(f"""
            QPushButton {{ background-color:{Colors.ACCENT}; color:#ffffff; border:none;
                border-radius:8px; font-size:13px; font-weight:700; padding:4px 20px; }}
            QPushButton:hover {{ background-color:{Colors.ACCENT_HOVER}; }}
        """)
        self._start_btn.clicked.connect(self._toggle)
        bl.addWidget(self._start_btn)
        return bar

    def _toggle_sys_prompt(self, checked: bool):
        """Show/hide the System Prompt row."""
        self._sys_frame.setVisible(checked)

    def _build_system_prompt(self):
        w = QWidget()
        w.setStyleSheet(f"background:#ffffff; border:1px solid {Colors.BORDER}; border-radius:10px;")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        hl.setSpacing(Spacing.SM)
        lbl = QLabel("System Prompt:")
        lbl.setStyleSheet(f"color:{Colors.TEXT_SECONDARY}; font-size:12px; font-weight:600; background:transparent; min-width:100px;")
        hl.addWidget(lbl)
        self._sys_edit = QTextEdit()
        self._sys_edit.setPlainText(_DEFAULT_SYSTEM)
        self._sys_edit.setFixedHeight(52)
        self._sys_edit.setStyleSheet(f"""
            QTextEdit {{ background:{Colors.BG_APP}; color:{Colors.TEXT_PRIMARY};
                border:1px solid {Colors.BORDER}; border-radius:6px; font-size:12px; padding:4px 8px; }}
            QTextEdit:focus {{ border-color:{Colors.ACCENT}; }}
        """)
        hl.addWidget(self._sys_edit)
        reset_btn = QPushButton("Reset")
        reset_btn.setFixedHeight(28)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{Colors.TEXT_MUTED}; "
            f"border:1px solid {Colors.BORDER}; border-radius:6px; font-size:11px; padding:2px 10px; }}"
            f"QPushButton:hover {{ color:{Colors.ACCENT}; border-color:{Colors.ACCENT}; }}"
        )
        reset_btn.clicked.connect(lambda: self._sys_edit.setPlainText(_DEFAULT_SYSTEM))
        hl.addWidget(reset_btn)
        return w

    def _build_chat_area(self):
        container = QFrame()
        container.setStyleSheet(
            f"QFrame {{ background:#ffffff; border:1px solid {Colors.BORDER}; border-radius:10px; }}")
        vl = QVBoxLayout(container); vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)
        hdr = QWidget()
        hdr.setStyleSheet(f"background:{Colors.BG_PANEL}; border-radius:10px 10px 0 0; border-bottom:1px solid {Colors.BORDER};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(16,8,16,8)
        icon_lbl = QLabel("  Conversation")
        icon_lbl.setStyleSheet(f"color:{Colors.TEXT_PRIMARY}; font-size:13px; font-weight:700; background:transparent;")
        hl.addWidget(icon_lbl); hl.addStretch()
        self._turns_lbl = QLabel("")
        self._turns_lbl.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:11px; background:transparent;")
        hl.addWidget(self._turns_lbl)
        vl.addWidget(hdr)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self._chat_widget = QWidget()
        self._chat_widget.setStyleSheet("background:transparent;")
        self._chat_layout = QVBoxLayout(self._chat_widget)
        self._chat_layout.setContentsMargins(12,12,12,12)
        self._chat_layout.setSpacing(8)
        self._placeholder = QLabel("  Press Start and begin speaking\n\nGemini will listen and respond in real-time audio + text.")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:14px; background:transparent;")
        self._chat_layout.addWidget(self._placeholder)
        self._chat_layout.addStretch()
        self._scroll.setWidget(self._chat_widget)
        vl.addWidget(self._scroll)
        self._bubbles = []
        return container

    def _build_bottom_bar(self):
        bar = QWidget(); bar.setStyleSheet("background:transparent;")
        hl = QHBoxLayout(bar); hl.setContentsMargins(0,0,0,0)
        self._blink_dot = QLabel("*")
        self._blink_dot.setFixedWidth(14)
        self._blink_dot.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:10px; background:transparent;")
        hl.addWidget(self._blink_dot)
        self._live_status = QLabel("Stream is off")
        self._live_status.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:11px; background:transparent;")
        hl.addWidget(self._live_status); hl.addStretch()
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink)
        self._blink_state = False
        return bar

    def _populate_mics(self):
        try:
            pya = pyaudio.PyAudio()
            default_idx = pya.get_default_input_device_info().get("index", 0)
            for i in range(pya.get_device_count()):
                info = pya.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    name = info.get("name", f"Device {i}")
                    self._mic_combo.addItem(name[:35], i)
                    if i == default_idx:
                        self._mic_combo.setCurrentIndex(self._mic_combo.count() - 1)
            pya.terminate()
        except Exception as exc:
            log.warning("Could not enumerate mics: %s", exc)
            self._mic_combo.addItem("Default microphone", -1)

    def _toggle(self):
        if self._running: self._stop()
        else:             self._start()

    def _resolve_api_key(self):
        from settings import settings
        # Primary: SQLite DB key store (shared across all features)
        try:
            key = settings.get_api_key("translation", "Gemini")
            if key:
                return key
        except Exception:
            pass
        import os
        return os.environ.get("GEMINI_API_KEY", "")

    def _start(self):
        api_key = self._resolve_api_key()
        if not api_key:
            QMessageBox.warning(self, "Gemini API Key Required",
                "A Gemini API key is needed for the AI Voice Assistant.\n\n"
                "Go to  Providers -> Manage API Keys  and enter your key.")
            return
        selected_model  = self._model_combo.currentData() or _DEFAULT_MODEL
        mic_idx         = self._mic_combo.currentData()
        system_prompt   = self._sys_edit.toPlainText().strip() or _DEFAULT_SYSTEM
        echo            = self._echo_chk.isChecked()
        self._placeholder.setVisible(False)
        self._running = True
        self._start_btn.setText("  Stop")
        self._start_btn.setStyleSheet(
            "QPushButton { background:#ef4444; color:#ffffff; border:none; border-radius:8px; "
            "font-size:13px; font-weight:700; padding:4px 20px; }"
            "QPushButton:hover { background:#dc2626; }"
        )
        self._model_combo.setEnabled(False)
        self._mic_combo.setEnabled(False)
        self._blink_timer.start(600)
        self._set_status("Connecting...", Colors.TEXT_MUTED)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(api_key, selected_model, mic_idx, system_prompt, echo),
            daemon=True,
        )
        self._thread.start()

    def _stop(self):
        if self._loop and self._stop_event:
            self._loop.call_soon_threadsafe(self._stop_event.set)

    def _run_loop(self, api_key, model, mic_idx, system_prompt, echo):
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(
                self._async_main(api_key, model, mic_idx, system_prompt, echo))
        except Exception as exc:
            log.error("VoiceAssistant async error: %s", exc, exc_info=True)
            self._sig_error.emit(str(exc))
        finally:
            try:
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                self._loop.close()
            except Exception:
                pass
            self._loop = None
            self._sig_disconn.emit("Session ended")

    async def _async_main(self, api_key, selected_model, mic_idx, system_prompt, echo):
        from google.genai import types
        self._stop_event = asyncio.Event()
        pya = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        try:
            client = genai.Client(http_options={"api_version": "v1beta"}, api_key=api_key)
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                input_audio_transcription=types.AudioTranscriptionConfig(),
                output_audio_transcription=types.AudioTranscriptionConfig(),
                system_instruction=types.Content(parts=[types.Part(text=system_prompt)]),
            )
            audio_in_q = asyncio.Queue()
            out_q = asyncio.Queue(maxsize=5)
            async with client.aio.live.connect(model=selected_model, config=config) as session:
                self._sig_connected.emit()

                async def listen_mic():
                    info = pya.get_device_info_by_index(mic_idx) if (mic_idx is not None and mic_idx >= 0) else pya.get_default_input_device_info()
                    stream = await asyncio.to_thread(pya.open, format=FORMAT, channels=CHANNELS,
                        rate=SEND_SAMPLE_RATE, input=True,
                        input_device_index=int(info["index"]), frames_per_buffer=CHUNK_SIZE)
                    try:
                        while not self._stop_event.is_set():
                            data = await asyncio.to_thread(stream.read, CHUNK_SIZE, False)
                            if data:
                                try: out_q.put_nowait(data)  # raw PCM bytes
                                except asyncio.QueueFull: pass
                    except asyncio.CancelledError: pass
                    finally:
                        try: stream.stop_stream(); stream.close()
                        except Exception: pass

                async def send_realtime():
                    while not self._stop_event.is_set():
                        try:
                            pcm = await asyncio.wait_for(out_q.get(), timeout=0.3)
                            blob = types.Blob(data=pcm, mime_type="audio/pcm")
                            await session.send_realtime_input(audio=blob)
                        except asyncio.TimeoutError: continue
                        except asyncio.CancelledError: break

                async def receive():
                    # Buffer partial transcription chunks; flush on turn_complete
                    ai_buf: list[str] = []
                    user_buf: list[str] = []
                    while not self._stop_event.is_set():
                        try:
                            async for response in session.receive():
                                if self._stop_event.is_set(): return
                                if response.data and echo:
                                    audio_in_q.put_nowait(response.data)
                                try:
                                    sc = response.server_content
                                    if sc:
                                        # Accumulate input transcript (user speech)
                                        it = (getattr(sc, "input_transcription", None)
                                              or getattr(sc, "input_audio_transcription", None))
                                        if it and getattr(it, "text", None):
                                            user_buf.append(it.text)
                                        # Accumulate output transcript (AI response)
                                        ot = (getattr(sc, "output_transcription", None)
                                              or getattr(sc, "output_audio_transcription", None))
                                        if ot and getattr(ot, "text", None):
                                            ai_buf.append(ot.text)
                                        # model_turn parts fallback
                                        mt = getattr(sc, "model_turn", None)
                                        if mt:
                                            for part in (getattr(mt, "parts", None) or []):
                                                if getattr(part, "text", None) and not response.data:
                                                    ai_buf.append(part.text)
                                        # Flush complete sentence on turn_complete
                                        if getattr(sc, "turn_complete", False):
                                            if user_buf:
                                                self._sig_user_text.emit("".join(user_buf))
                                                user_buf.clear()
                                            if ai_buf:
                                                self._sig_ai_text.emit("".join(ai_buf))
                                                ai_buf.clear()
                                except Exception as e: log.debug("sc parse: %s", e)
                        except asyncio.CancelledError: break
                        except Exception as exc: log.debug("recv err: %s", exc); await asyncio.sleep(0.1)

                async def play_audio():
                    if not echo: return
                    stream = await asyncio.to_thread(pya.open, format=FORMAT, channels=CHANNELS,
                        rate=RECV_SAMPLE_RATE, output=True)
                    try:
                        while not self._stop_event.is_set():
                            try:
                                chunk = await asyncio.wait_for(audio_in_q.get(), timeout=0.3)
                                await asyncio.to_thread(stream.write, chunk)
                            except asyncio.TimeoutError: continue
                            except asyncio.CancelledError: break
                    finally:
                        try: stream.stop_stream(); stream.close()
                        except Exception: pass

                tasks = [asyncio.create_task(listen_mic()), asyncio.create_task(send_realtime()),
                         asyncio.create_task(receive()), asyncio.create_task(play_audio()),
                         asyncio.create_task(self._stop_event.wait())]
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for t in pending: t.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
        finally:
            try: pya.terminate()
            except Exception: pass

    def _on_user_text(self, text):
        text = text.strip()
        if text: self._add_bubble("user", text, datetime.now().strftime("%H:%M:%S"))

    def _on_ai_text(self, text):
        text = text.strip()
        if text: self._add_bubble("assistant", text, datetime.now().strftime("%H:%M:%S"))

    def _add_bubble(self, role, text, ts):
        bubble = _ChatBubble(role, text, ts, self._chat_widget)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, bubble)
        self._bubbles.append((role, text))
        count = sum(1 for r, _ in self._bubbles if r == "user")
        self._turns_lbl.setText(f"{count} turn{'s' if count != 1 else ''}")
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()))

    def _on_connected(self):
        self._set_status("Connected", Colors.SUCCESS)
        self._live_status.setText("Stream is live")
        self._live_status.setStyleSheet(f"color:{Colors.SUCCESS}; font-size:11px; background:transparent;")

    def _on_disconnected(self, reason):
        self._running = False
        self._blink_timer.stop()
        self._blink_dot.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:10px; background:transparent;")
        self._live_status.setText("Stream is off")
        self._live_status.setStyleSheet(f"color:{Colors.TEXT_MUTED}; font-size:11px; background:transparent;")
        self._start_btn.setText("  Start")
        self._start_btn.setStyleSheet(f"""
            QPushButton {{ background:{Colors.ACCENT}; color:#ffffff; border:none;
                border-radius:8px; font-size:13px; font-weight:700; padding:4px 20px; }}
            QPushButton:hover {{ background:{Colors.ACCENT_HOVER}; }}
        """)
        self._model_combo.setEnabled(True)
        self._mic_combo.setEnabled(True)
        self._set_status("Ready", Colors.TEXT_MUTED)

    def _on_error(self, msg):
        self._on_disconnected("error")
        QMessageBox.critical(self, "Voice Assistant Error", msg[:500])

    def _blink(self):
        self._blink_state = not self._blink_state
        color = Colors.SUCCESS if self._blink_state else Colors.TEXT_MUTED
        self._blink_dot.setStyleSheet(f"color:{color}; font-size:10px; background:transparent;")

    def _set_status(self, text, color=""):
        color = color or Colors.TEXT_MUTED
        self._status_lbl.setStyleSheet(f"color:{color}; font-size:11px; background:transparent;")
        self._status_lbl.setText(text)

    def _copy_chat(self):
        if not self._bubbles: return
        lines = [("You: " if r == "user" else "AI: ") + t for r, t in self._bubbles]
        copy_to_clipboard("\n\n".join(lines))

    def _clear_chat(self):
        while self._chat_layout.count() > 1:
            item = self._chat_layout.takeAt(0)
            if item.widget() and item.widget() is not self._placeholder:
                item.widget().deleteLater()
        self._bubbles.clear()
        self._turns_lbl.setText("")
        self._placeholder.setVisible(not self._running)

    def _lbl(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{Colors.TEXT_SECONDARY}; font-size:12px; background:transparent;")
        return lbl

    def _vline(self):
        f = QFrame(); f.setFrameShape(QFrame.VLine)
        f.setStyleSheet(f"color:{Colors.BORDER}; max-width:1px;")
        return f


