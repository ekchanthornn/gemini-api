import tensorflow as tf
import numpy as np

# --- Data ---
X = np.array([50, 80, 100, 120, 150], dtype=float)
y = np.array([50000, 80000, 100000, 120000, 150000], dtype=float)

# Normalize: scale X and y so training converges reliably
X_mean, X_std = X.mean(), X.std()
y_mean, y_std = y.mean(), y.std()

X_norm = (X - X_mean) / X_std
y_norm = (y - y_mean) / y_std

# --- Model ---
model = tf.keras.Sequential([
    tf.keras.Input(shape=[1]),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer="adam", loss="mse")

# --- Training ---
model.fit(X_norm, y_norm, epochs=500, verbose=0)

# --- Prediction ---
X_pred = np.array([90], dtype=float)
X_pred_norm = (X_pred - X_mean) / X_std
price_norm = model.predict(X_pred_norm, verbose=0)

# Denormalize the output
price = price_norm * y_std + y_mean

print(f"Predicted house price for size 90: ${price[0][0]:,.2f}")