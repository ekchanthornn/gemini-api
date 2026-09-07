"""
Gemini Live API — Real-time Voice Conversation (simple version)
"""

import asyncio
import pyaudio
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# =========================
# Config
# =========================

FORMAT      = pyaudio.paInt16
CHANNELS    = 1
INPUT_RATE  = 16000
OUTPUT_RATE = 24000
CHUNK       = 1024

MODEL = "gemini-3.1-flash-live-preview"

SYSTEM_PROMPT = (
    "You are a helpful, friendly AI voice assistant. "
    "Listen carefully and respond naturally in a conversational tone. "
    "Keep your answers concise and clear."
)

# =========================
# Main
# =========================

async def main():

    pya = pyaudio.PyAudio()

    client = genai.Client(
        http_options={"api_version": "v1beta"},
        api_key=os.getenv("GEMINI_API_KEY")
    )

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=types.Content(
            parts=[types.Part(text=SYSTEM_PROMPT)]
        ),
    )

    # Unlimited queue — never drop audio
    audio_out_q = asyncio.Queue()

    print("Connecting to Gemini Live...")

    async with client.aio.live.connect(model=MODEL, config=config) as session:

        print("✅ Connected!")
        print("🎤 Speak now. Press Ctrl+C to stop.\n")

        # ─── Mic input stream ───
        mic = pya.open(
            format=FORMAT, channels=CHANNELS,
            rate=INPUT_RATE, input=True,
            frames_per_buffer=CHUNK
        )

        # ─── Speaker output stream ───
        speaker = pya.open(
            format=FORMAT, channels=CHANNELS,
            rate=OUTPUT_RATE, output=True
        )

        # ─── Send: Mic → Gemini ───

        async def send_audio():
            while True:
                data = await asyncio.to_thread(mic.read, CHUNK, False)
                blob = types.Blob(data=data, mime_type="audio/pcm")
                await session.send_realtime_input(audio=blob)

        # ─── Receive: Gemini → Queue + print text ───

        async def receive_audio():
            while True:
                async for resp in session.receive():
                    if resp.data:
                        audio_out_q.put_nowait(resp.data)

                    # Print transcriptions
                    try:
                        sc = resp.server_content
                        if sc:
                            it = (getattr(sc, "input_transcription", None)
                                  or getattr(sc, "input_audio_transcription", None))
                            if it and getattr(it, "text", None):
                                print(f"  🗣️  You: {it.text}", end="", flush=True)

                            ot = (getattr(sc, "output_transcription", None)
                                  or getattr(sc, "output_audio_transcription", None))
                            if ot and getattr(ot, "text", None):
                                print(f"  🤖 AI: {ot.text}", end="", flush=True)

                            if getattr(sc, "turn_complete", False):
                                print()
                    except Exception:
                        pass

        # ─── Play: Queue → Speaker ───

        async def play_audio():
            while True:
                chunk = await audio_out_q.get()
                await asyncio.to_thread(speaker.write, chunk)

        # ─── Run all tasks ───

        tasks = [
            asyncio.create_task(send_audio()),
            asyncio.create_task(receive_audio()),
            asyncio.create_task(play_audio()),
        ]

        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            for t in tasks:
                t.cancel()
            mic.stop_stream()
            mic.close()
            speaker.stop_stream()
            speaker.close()
            pya.terminate()
            print("\n\n⏹️  Stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDone.")