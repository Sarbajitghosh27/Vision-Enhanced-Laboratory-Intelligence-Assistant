"""
scripts/train_fault_classifier.py
Generates synthetic ECE laboratory fault data and trains Random Forest
and XGBoost classifiers to diagnose hardware faults from measurement data.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
import joblib

# Create models directory if not exists
os.makedirs("models", exist_ok=True)

# ── 1. Synthetic Data Generation ──────────────────────────────────────────────
np.random.seed(42)
N_SAMPLES_PER_CLASS = 600

# Classes mapping:
# 0: normal
# 1: open_circuit_flat_line
# 2: reversed_polarity
# 3: bias_error_cutoff
# 4: bias_error_saturation
# 5: load_error_droop
# 6: loading_bypass_error_no_gain
# 7: input_overdrive_clipping

features = []
labels = []

# Loop to generate data vectors: [exp_type, meas_1, meas_2, meas_3, exp_1, exp_2, exp_3]
# exp_type: 0: cro, 1: diode, 2: zener, 3: bjt_amp, 4: opamp

# Class 0: Normal
for exp in range(5):
    for _ in range(N_SAMPLES_PER_CLASS):
        if exp == 0: # cro: Vp, f
            exp_v, exp_f = 2.0, 1000.0
            meas_v = exp_v + np.random.normal(0, 0.05)
            meas_f = exp_f + np.random.normal(0, 10.0)
            features.append([exp, meas_v, meas_f, 0.0, exp_v, exp_f, 0.0])
        elif exp == 1: # diode: Vd, Id
            exp_vd, exp_id = 0.7, 15.0
            meas_vd = exp_vd + np.random.normal(0, 0.02)
            meas_id = exp_id + np.random.normal(0, 0.5)
            features.append([exp, meas_vd, meas_id, 0.0, exp_vd, exp_id, 0.0])
        elif exp == 2: # zener: Vin, Vout
            exp_vin, exp_vout = 10.0, 5.1
            meas_vin = exp_vin + np.random.normal(0, 0.1)
            meas_vout = exp_vout + np.random.normal(0, 0.05)
            features.append([exp, meas_vin, meas_vout, 0.0, exp_vin, exp_vout, 0.0])
        elif exp == 3: # bjt_amp: VCE, Gain
            exp_vce, exp_gain = 6.0, 15.0
            meas_vce = exp_vce + np.random.normal(0, 0.2)
            meas_gain = exp_gain + np.random.normal(0, 0.5)
            features.append([exp, meas_vce, meas_gain, 0.0, exp_vce, exp_gain, 0.0])
        elif exp == 4: # opamp: Gain, Vout
            exp_gain, exp_vout = 10.0, 5.0
            meas_gain = exp_gain + np.random.normal(0, 0.1)
            meas_vout = exp_vout + np.random.normal(0, 0.1)
            features.append([exp, meas_gain, meas_vout, 0.0, exp_gain, exp_vout, 0.0])
        labels.append(0)

# Class 1: Open Circuit / Flat Line
for exp in range(5):
    for _ in range(N_SAMPLES_PER_CLASS // 2):
        # All measurements are zero or close to noise floor
        meas_1 = np.random.uniform(0.0, 0.02)
        meas_2 = np.random.uniform(0.0, 0.02)
        meas_3 = 0.0
        exp_1 = 2.0 if exp == 0 else (0.7 if exp == 1 else (5.1 if exp == 2 else 6.0))
        exp_2 = 1000.0 if exp == 0 else (15.0 if exp == 1 else (10.0 if exp == 2 else 15.0))
        features.append([exp, meas_1, meas_2, meas_3, exp_1, exp_2, 0.0])
        labels.append(1)

# Class 2: Reversed Polarity
for exp in [1, 2]: # diode, zener
    for _ in range(N_SAMPLES_PER_CLASS):
        if exp == 1: # diode
            meas_vd = 0.7 + np.random.normal(0, 0.02) # diode drop across it, but ammeter is zero
            meas_id = np.random.uniform(0.0, 0.01) # leakage
            features.append([exp, meas_vd, meas_id, 0.0, 0.7, 15.0, 0.0])
        else: # zener
            meas_vin = 10.0 + np.random.normal(0, 0.1)
            meas_vout = 0.7 + np.random.normal(0, 0.05) # acts like forward diode drop
            features.append([exp, meas_vin, meas_vout, 0.0, 10.0, 5.1, 0.0])
        labels.append(2)

# Class 3: Bias Error Cutoff
for _ in range(N_SAMPLES_PER_CLASS):
    # VCE ≈ VCC (12V) and Gain is zero
    exp = 3
    meas_vce = 11.8 + np.random.uniform(0.0, 0.2)
    meas_gain = np.random.uniform(0.0, 0.1)
    features.append([exp, meas_vce, meas_gain, 0.0, 6.0, 15.0, 0.0])
    labels.append(3)

# Class 4: Bias Error Saturation
for _ in range(N_SAMPLES_PER_CLASS):
    # VCE ≈ 0.2V (VCE_sat) and Gain is zero
    exp = 3
    meas_vce = 0.2 + np.random.normal(0, 0.02)
    meas_gain = np.random.uniform(0.0, 0.1)
    features.append([exp, meas_vce, meas_gain, 0.0, 6.0, 15.0, 0.0])
    labels.append(4)

# Class 5: Load Error / Droop
for _ in range(N_SAMPLES_PER_CLASS):
    # Zener Vout droops heavily under load
    exp = 2
    meas_vin = 10.0 + np.random.normal(0, 0.1)
    meas_vout = 3.2 + np.random.normal(0, 0.2) # drops below 5.1V
    features.append([exp, meas_vin, meas_vout, 0.0, 10.0, 5.1, 0.0])
    labels.append(5)

# Class 6: Loading/Bypass Error (No gain)
for exp in [3, 4]: # CE amplifier, Op-Amp
    for _ in range(N_SAMPLES_PER_CLASS):
        if exp == 3: # CE amp: bypass capacitor missing -> gain drops to ~1.2
            meas_vce = 6.0 + np.random.normal(0, 0.2)
            meas_gain = 1.2 + np.random.normal(0, 0.1)
            features.append([exp, meas_vce, meas_gain, 0.0, 6.0, 15.0, 0.0])
        else: # op-amp: gain is very low due to loading
            meas_gain = 0.8 + np.random.normal(0, 0.08)
            meas_vout = 0.4 + np.random.normal(0, 0.04)
            features.append([exp, meas_gain, meas_vout, 0.0, 10.0, 5.0, 0.0])
        labels.append(6)

# Class 7: Input Overdrive / Clipping
for exp in [3, 4]: # CE amp, Op-Amp
    for _ in range(N_SAMPLES_PER_CLASS):
        if exp == 3: # CE amp output clipping at Vcc rails
            meas_vce = 6.0 + np.random.normal(0, 0.2)
            meas_gain = 8.5 + np.random.normal(0, 0.5) # reduced average gain
            features.append([exp, meas_vce, meas_gain, 1.0, 6.0, 15.0, 0.0]) # 1.0 indicates clipping flag
        else: # op-amp output clipping
            meas_gain = 6.2 + np.random.normal(0, 0.3)
            meas_vout = 10.5 + np.random.normal(0, 0.1) # hit opamp rail
            features.append([exp, meas_gain, meas_vout, 1.0, 10.0, 5.0, 0.0])
        labels.append(7)

# Convert to DataFrame
cols = ["exp_type", "meas_1", "meas_2", "meas_3", "exp_1", "exp_2", "exp_3"]
X = pd.DataFrame(features, columns=cols)
y = pd.Series(labels)

print(f"Generated Dataset Shape: {X.shape}")
print(f"Class counts:\n{y.value_counts()}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# ── 2. Train Random Forest ────────────────────────────────────────────────────
print("\nTraining Random Forest Classifier...")
rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
print(f"Random Forest Accuracy: {accuracy_score(y_test, y_pred_rf):.4f}")
print(classification_report(y_test, y_pred_rf))

# ── 3. Train MLP Neural Network ───────────────────────────────────────────────
print("\nTraining Deep Neural Network (MLPClassifier)...")
mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=42, early_stopping=True)
mlp.fit(X_train, y_train)
y_pred_mlp = mlp.predict(X_test)
print(f"MLP Neural Network Accuracy: {accuracy_score(y_test, y_pred_mlp):.4f}")
print(classification_report(y_test, y_pred_mlp))

# ── 4. Train XGBoost (Optional Fallback) ──────────────────────────────────────
xgb_model = None
if XGB_AVAILABLE:
    print("\nTraining XGBoost Classifier...")
    try:
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric="mlogloss"
        )
        xgb_model.fit(X_train, y_train)
        y_pred_xgb = xgb_model.predict(X_test)
        print(f"XGBoost Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}")
        print(classification_report(y_test, y_pred_xgb))
    except Exception as e:
        print(f"XGBoost training skipped: {e}")

# ── 5. Save model artifact ───────────────────────────────────────────────────
model_data = {
    "random_forest": rf,
    "neural_network": mlp,
    "xgboost": xgb_model,
    "classes": [
        "Normal operation",
        "Open Circuit / Loose Connection",
        "Reversed Component Polarity",
        "Transistor Bias Cutoff Error",
        "Transistor Bias Saturation Error",
        "Load Impedance Droop",
        "Missing Emitter Bypass Capacitor / Feedback Gain Loss",
        "Input Overdrive / Waveform Saturation Clipping"
    ]
}

joblib.dump(model_data, "models/fault_classifier.joblib")
print("\nModel saved successfully to: models/fault_classifier.joblib")
