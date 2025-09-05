# backend/train_model.py
# Python 3.10+

import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

DATA_PATH = Path("data") / "tle_features_labeled.csv"
MODEL_DIR = Path("ml_models"); MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "object_classifier.joblib"

if not DATA_PATH.exists():
    print(f"[X] Training data not found at {DATA_PATH.resolve()}")
    sys.exit(1)

df = pd.read_csv(DATA_PATH)
print(f"[i] Loaded {len(df)} rows with {len(df.columns)} columns from {DATA_PATH}")

# --- column auto-mapping ---
ALIASES = {
    "inc_deg":      ["inc_deg", "INCLINATION", "Inclination", "inclination"],
    "ecc":          ["ecc", "ECCENTRICITY", "Eccentricity", "eccentricity"],
    "mm_rev_day":   ["mm_rev_day", "MEAN_MOTION", "MeanMotion", "mean_motion", "meanMotion"],
    "bstar":        ["bstar", "BSTAR", "Bstar"],
    "label":        ["label", "OBJECT_TYPE", "object_type"],
}

def pick(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None

col_inc   = pick(df, ALIASES["inc_deg"])
col_ecc   = pick(df, ALIASES["ecc"])
col_mm    = pick(df, ALIASES["mm_rev_day"])
col_bstar = pick(df, ALIASES["bstar"])
col_label = pick(df, ALIASES["label"])

missing = [n for n, c in [
    ("inc_deg", col_inc), ("ecc", col_ecc), ("mm_rev_day", col_mm),
    ("bstar", col_bstar), ("label", col_label)
] if c is None]
if missing:
    print(f"[X] Could not find required columns: {missing}")
    print("[hint] Re-run build_dataset.py with the CSV-based source, or share your CSV headers so I can map them.")
    sys.exit(2)

# Normalize and coerce numerics
work = df[[col_inc, col_ecc, col_mm, col_bstar, col_label]].copy()
for c in [col_inc, col_ecc, col_mm, col_bstar]:
    work[c] = pd.to_numeric(work[c], errors="coerce")
work[col_label] = work[col_label].astype(str).str.strip().str.title()

# Keep only three main classes
VALID = {"Payload", "Rocket Body", "Debris"}
work = work[work[col_label].isin(VALID)]
print("[i] Kept classes:", sorted(work[col_label].unique()))
print(work[col_label].value_counts())

# Drop rows with missing features
before = len(work)
work = work.dropna(subset=[col_inc, col_ecc, col_mm, col_bstar]).reset_index(drop=True)
after = len(work)
print(f"[i] Dropped {before - after} rows with missing features; remaining: {after}")

if len(work) < 50:
    print(f"[X] Not enough rows to train (have {len(work)}).")
    print("    Fix: build a broader dataset in build_dataset.py (e.g., include debris groups).")
    sys.exit(3)

X = work[[col_inc, col_ecc, col_mm, col_bstar]].to_numpy(dtype=float)
y = work[col_label].to_numpy()

# Class counts (for info)
cls_counts = pd.Series(y).value_counts()
if (cls_counts < 5).any() or cls_counts.nunique() == 1:
    print("[!] Class imbalance or single-class detected:")
    print(cls_counts)
    print("    We'll oversample the training split to help minority classes.")

# Train/test split (stratify if multiple classes)
strat = y if len(np.unique(y)) > 1 else None
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=strat
)

# --- Oversample only the training split --------------------------------------
try:
    from imblearn.over_sampling import RandomOverSampler
except ImportError:
    print("[X] imbalanced-learn is not installed. Please run:  pip install imbalanced-learn")
    sys.exit(4)

ros = RandomOverSampler(random_state=42)
X_tr_bal, y_tr_bal = ros.fit_resample(X_tr, y_tr)
print(f"[i] Oversampled train size: {len(y_tr)} → {len(y_tr_bal)}")
print(pd.Series(y_tr_bal).value_counts())

# --- Train models on oversampled training data -------------------------------
print("\n=== Baseline: Logistic Regression (oversampled train) ===")
logreg = LogisticRegression(max_iter=400, class_weight=None)
logreg.fit(X_tr_bal, y_tr_bal)
print(classification_report(y_te, logreg.predict(X_te), digits=3, zero_division=0))

print("\n=== Random Forest (oversampled train) ===")
rf_bal = RandomForestClassifier(
    n_estimators=600, max_depth=None,
    class_weight=None, n_jobs=-1, random_state=42
)
rf_bal.fit(X_tr_bal, y_tr_bal)
pred_bal = rf_bal.predict(X_te)
print(classification_report(y_te, pred_bal, digits=3, zero_division=0))
print("Confusion matrix:\n", confusion_matrix(y_te, pred_bal))

# Quick CV (macro F1) using original (unbalanced) full set for sanity
if len(np.unique(y)) > 1:
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = cross_val_score(rf_bal, X, y, cv=skf, scoring="f1_macro", n_jobs=-1)
    print(f"3-fold CV F1_macro (RF, oversampled train): {scores.mean():.3f} ± {scores.std():.3f}")

# --- Persist the oversampled RF as production model --------------------------
joblib.dump(
    {
        "model": rf_bal,
        "features": ["inc_deg", "ecc", "mm_rev_day", "bstar"],  # expected input order at inference
        "classes_": rf_bal.classes_,
    },
    MODEL_PATH,
)
print(f"\n[✔] Saved model to {MODEL_PATH.resolve()}")
