import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# --- Data ---
X = np.array([50, 80, 100, 120, 150], dtype=float).reshape(-1, 1)  # Must be 2D for sklearn
y = np.array([50000, 80000, 100000, 120000, 150000], dtype=float)

# --- Model ---
# No normalization needed! sklearn handles it internally.
model = LinearRegression()

# --- Training ---
model.fit(X, y)

# --- Evaluation ---
y_pred_train = model.predict(X)
mse = mean_squared_error(y, y_pred_train)
r2  = r2_score(y, y_pred_train)

print(f"Model weight (slope) : {model.coef_[0]:,.2f}")
print(f"Model bias (intercept): {model.intercept_:,.2f}")
print(f"MSE on training data  : {mse:,.2f}")
print(f"R² score              : {r2:.4f}  (1.0 = perfect fit)")

# --- Prediction ---
X_pred = np.array([[90]])   # 2D input required by sklearn
price  = model.predict(X_pred)

print(f"\nPredicted house price for size 90: ${price[0]:,.2f}")
