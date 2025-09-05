# Purpose: Quick diagnostics for your training CSV
# Usage:
#   python backend/check_dataset.py
#   python backend/check_dataset.py --path data/tle_features_labeled.csv

import os
import sys
import argparse
import pandas as pd

DEFAULT_PATH = os.path.join("data", "tle_features_labeled.csv")

FEATURE_CANDIDATES = {
    "inc_deg":    ["inc_deg", "INCLINATION", "Inclination", "inclination"],
    "ecc":        ["ecc", "ECCENTRICITY", "Eccentricity", "eccentricity"],
    "mm_rev_day": ["mm_rev_day", "MEAN_MOTION", "MeanMotion", "mean_motion", "meanMotion"],
    "bstar":      ["bstar", "BSTAR", "Bstar"],
    "label":      ["label", "OBJECT_TYPE", "object_type"],
}

def pick_column(df, candidates):
    """Return the first column name from candidates that exists in df.columns."""
    for name in candidates:
        if name in df.columns:
            return name
    return None

def main():
    ap = argparse.ArgumentParser(description="Check training dataset CSV.")
    ap.add_argument("--path", type=str, default=DEFAULT_PATH, help="Path to CSV (default: data/tle_features_labeled.csv)")
    args = ap.parse_args()

    csv_path = args.path
    print(f"[i] Looking for CSV at: {os.path.abspath(csv_path)}")
    if not os.path.exists(csv_path):
        print("[X] File not found.")
        print("    - Make sure you ran:  python backend/build_dataset.py")
        print("    - Or pass a custom path:  python backend/check_dataset.py --path <your_csv>")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print("[X] Failed to read CSV:", e)
        sys.exit(2)

    # Defensive: drop any accidental columns created by failed API responses
    bad_cols = [c for c in df.columns if isinstance(c, str) and "Invalid query:" in c]
    if bad_cols:
        print(f"[!] Dropping unexpected columns from failed API response: {bad_cols}")
        df = df.drop(columns=bad_cols)

    # Basic info
    print("\n=== BASIC INFO ===")
    print(f"Rows, Columns: {df.shape}")
    print("Column names:", list(df.columns))

    if df.shape[0] == 0:
        print("\n[!] The CSV has 0 rows. Rebuild dataset with a broader group, e.g.:")
        print('    In build_dataset.py include debris groups (e.g., last-30-days, cosmos-2251-debris, iridium-33-debris)')
        sys.exit(0)

    # Map columns
    col_inc   = pick_column(df, FEATURE_CANDIDATES["inc_deg"])
    col_ecc   = pick_column(df, FEATURE_CANDIDATES["ecc"])
    col_mm    = pick_column(df, FEATURE_CANDIDATES["mm_rev_day"])
    col_bstar = pick_column(df, FEATURE_CANDIDATES["bstar"])
    col_label = pick_column(df, FEATURE_CANDIDATES["label"])

    print("\n=== COLUMN MAPPING ===")
    print("inc_deg   ->", col_inc)
    print("ecc       ->", col_ecc)
    print("mm_rev_day->", col_mm)
    print("bstar     ->", col_bstar)
    print("label     ->", col_label)

    missing = [k for k, v in {
        "inc_deg": col_inc, "ecc": col_ecc, "mm_rev_day": col_mm, "bstar": col_bstar, "label": col_label
    }.items() if v is None]
    if missing:
        print(f"\n[!] Missing required columns (or aliases): {missing}")
        print("    Tip: Re-run build_dataset.py, or share your headers so we can update the mapper.")
        # Still show a preview
        print("\n=== HEAD (first 5 rows) ===")
        print(df.head(5).to_string(index=False))
        sys.exit(0)

    # Coerce numerics & normalize label for quick stats
    for c in [col_inc, col_ecc, col_mm, col_bstar]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df[col_label] = df[col_label].astype(str).str.strip().str.title()

    print("\n=== LABEL COUNTS ===")
    counts = df[col_label].value_counts(dropna=False)
    print(counts)

    # Light advice if severely imbalanced
    if (counts.min() < 10) and (counts.max() > 5 * max(1, counts.min())):
        print("\n[tip] Labels look imbalanced. Consider:")
        print("      - Including more groups in build_dataset.py (debris clusters, etc.)")
        print("      - Using oversampling in train_model.py (RandomOverSampler)")

    print("\n=== NaN COUNTS (key features) ===")
    for c in [col_inc, col_ecc, col_mm, col_bstar]:
        print(f"{c}: {df[c].isna().sum()}")

    # Keep only core classes (if present), report counts
    valid = {"Payload", "Rocket Body", "Debris"}
    subset = df[df[col_label].isin(valid)].copy()
    print("\n=== FILTERED TO [Payload, Rocket Body, Debris] ===")
    print("Rows kept:", len(subset))
    if len(subset) > 0:
        print(subset[col_label].value_counts())

    # Small preview
    print("\n=== SAMPLE ROWS (up to 5) ===")
    cols_to_show = [col_inc, col_ecc, col_mm, col_bstar, col_label]
    print(subset[cols_to_show].head(5).to_string(index=False))

    print("\n[✔] Dataset check complete.")

if __name__ == "__main__":
    main()
