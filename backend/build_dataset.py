# build_dataset.py
# Python 3.10+ recommended
# Creates: data/tle_features_labeled.csv  (for training)
#          data/tle_features_all.csv      (for inference / EDA)

import io
import math
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

CELESTRAK_SATCAT = "https://celestrak.org/pub/satcat.csv"

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Orbital constants (km, s) ---
MU_EARTH_KM3_S2 = 398600.4418
R_EARTH_KM = 6378.137
DAY_SEC = 86400.0
TWOPI = 2.0 * math.pi

def _safe_float(text: str, default=float("nan")) -> float:
    try:
        return float(text)
    except Exception:
        return default

def parse_bstar(line1: str) -> float:
    """BSTAR drag term from TLE line 1 (cols 54–61)."""
    mant = line1[53:59].strip()
    expo = line1[59:61].strip()
    if not mant:
        return float("nan")
    m = re.match(r"^([ +-]?)(\d+)$", mant)
    if not m:
        return float("nan")
    sign, digits = m.groups()
    mantissa = float(f"{sign}0.{digits}")
    try:
        exponent = int(expo)
    except Exception:
        return float("nan")
    return mantissa * (10.0 ** exponent)

def parse_epoch(line1: str) -> datetime | None:
    """TLE epoch: columns 19–32 -> datetime (UTC)."""
    try:
        yr = int(line1[18:20])
        doy = float(line1[20:32])
        year_full = 1900 + yr if yr >= 57 else 2000 + yr
        jan1 = datetime(year_full, 1, 1, tzinfo=timezone.utc)
        return jan1 + timedelta(days=doy - 1.0)
    except Exception:
        return None

def mean_motion_to_sma_km(n_rev_per_day: float) -> float:
    """Convert mean motion (rev/day) to semi-major axis a (km)."""
    if not math.isfinite(n_rev_per_day) or n_rev_per_day <= 0:
        return float("nan")
    n_rad_s = n_rev_per_day * TWOPI / DAY_SEC
    return (MU_EARTH_KM3_S2 / (n_rad_s ** 2.0)) ** (1.0 / 3.0)

def fetch_satcat() -> pd.DataFrame:
    print("[*] Downloading CelesTrak SATCAT ...")
    usecols = [
        "NORAD_CAT_ID", "OBJECT_TYPE", "OPS_STATUS_CODE", "COUNTRY",
        "LAUNCH_DATE", "DECAY_DATE", "PERIOD", "INCLINATION",
        "APOAPSIS", "PERIAPSIS"
    ]
    r = requests.get(CELESTRAK_SATCAT, timeout=60)
    r.raise_for_status()
    data = io.StringIO(r.content.decode("utf-8", errors="ignore"))
    satcat = pd.read_csv(data, usecols=lambda c: c in usecols, sep=None, engine="python")
    satcat = satcat.rename(columns={"NORAD_CAT_ID": "norad", "OBJECT_TYPE": "label"})
    # Keep label raw for mapping later
    return satcat

# ---------- NEW: Normalize GP CSV columns to our schema ----------
def normalize_gp_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename CelesTrak GP CSV headers to our internal schema."""
    if df.empty:
        return df
    rename_map = {
        "NORAD_CAT_ID": "norad",
        "EPOCH": "epoch_iso",
        "INCLINATION": "inc_deg",
        "ECCENTRICITY": "ecc",
        "MEAN_MOTION": "mm_rev_day",
        "BSTAR": "bstar",
        "RA_OF_ASC_NODE": "raan_deg",
        "ARG_OF_PERICENTER": "argp_deg",
        "MEAN_ANOMALY": "mean_anom_deg",
        "SEMI_MAJOR_AXIS": "sma_km",
        "APOAPSIS": "apogee_alt_km",
        "PERIAPSIS": "perigee_alt_km",
        # Already-normalized columns pass through unchanged
        "norad": "norad",
        "epoch_iso": "epoch_iso",
        "inc_deg": "inc_deg",
        "ecc": "ecc",
        "mm_rev_day": "mm_rev_day",
        "bstar": "bstar",
        "raan_deg": "raan_deg",
        "argp_deg": "argp_deg",
        "mean_anom_deg": "mean_anom_deg",
        "sma_km": "sma_km",
        "apogee_alt_km": "apogee_alt_km",
        "perigee_alt_km": "perigee_alt_km",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    # Ensure numeric core features
    for c in ["inc_deg", "ecc", "mm_rev_day", "bstar"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Ensure norad present & numeric
    if "norad" in df.columns:
        df["norad"] = pd.to_numeric(df["norad"], errors="coerce").astype("Int64")
    return df

# ---------- UPDATED: GP CSV fetch with guard ----------
def fetch_gp_csv(url: str) -> pd.DataFrame:
    print("[*] Downloading CelesTrak GP CSV ...")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    text = r.text.strip()
    if text.startswith("Invalid query:"):
        print(f"[!] Skipping group: {text}")
        return pd.DataFrame()
    df = pd.read_csv(io.StringIO(text))
    return normalize_gp_columns(df)

def main():
    try:
        # --- Collect multiple groups for a balanced dataset ---
        GROUPS = [
            "last-30-days",          # broad mix
            "cosmos-2251-debris",    # debris
            "iridium-33-debris",     # debris
        ]
        dfs = []
        for g in GROUPS:
            url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={g}&FORMAT=csv"
            print(f"[*] Fetching group: {g}")
            df_g = fetch_gp_csv(url)
            if not df_g.empty:
                dfs.append(df_g)

        if not dfs:
            print("[X] No GP data fetched. Check connectivity or groups.")
            sys.exit(1)

        # Combine and drop duplicate NORAD IDs
        tle_df = pd.concat(dfs, ignore_index=True)
        if "norad" not in tle_df.columns:
            print("[X] 'norad' column missing after normalization.")
            sys.exit(2)

        tle_df = tle_df.dropna(subset=["norad"]).drop_duplicates(subset=["norad"]).reset_index(drop=True)
        print(f"[+] Combined dataset: {len(tle_df)} unique objects")

        # Save raw features (for EDA/inference)
        all_path = os.path.join(OUT_DIR, "tle_features_all.csv")
        tle_df.to_csv(all_path, index=False)
        print(f"[+] Wrote {all_path} ({len(tle_df)} rows)")

        # --- SATCAT merge (robust) ---
        satcat = fetch_satcat()

        # Normalize types for join
        satcat["norad"] = pd.to_numeric(satcat["norad"], errors="coerce").astype("Int64")
        print(f"[*] TLE objects before merge: {len(tle_df)}")
        print(f"[*] SATCAT rows: {len(satcat)}")

        merged = tle_df.merge(satcat[["norad", "label"]], on="norad", how="left")

        # Diagnostics BEFORE filtering
        non_null_labels = merged["label"].notna().sum()
        print(f"[*] After merge, rows with a label: {non_null_labels} / {len(merged)}")
        print("    Unique labels (raw):", merged["label"].dropna().astype(str).str.strip().value_counts().head(10).to_dict())

        # Map abbreviations to full names
        merged["label"] = merged["label"].astype("string").str.strip().str.upper()
        abbr_map = {
            "PAY": "Payload",
            "R/B": "Rocket Body",
            "RB":  "Rocket Body",
            "DEB": "Debris",
            "UNK": "Unknown",
        }
        merged["label"] = merged["label"].replace(abbr_map)

        VALID = {"Payload", "Rocket Body", "Debris"}
        before_filter = len(merged)
        merged = merged[merged["label"].isin(VALID)].copy()
        after_filter = len(merged)
        print(f"[*] After filtering to {VALID}: {after_filter} / {before_filter} rows remain")

        # Basic cleaning: drop rows with missing core features
        core_cols = ["inc_deg", "ecc", "mm_rev_day", "bstar"]
        for c in core_cols:
            if c not in merged.columns:
                print(f"[!] Missing expected feature column: {c}")
        merged_clean = merged.dropna(subset=[c for c in core_cols if c in merged.columns]).reset_index(drop=True)
        print(f"[*] After dropping rows with missing features: {len(merged_clean)} rows")

        out_path = os.path.join(OUT_DIR, "tle_features_labeled.csv")
        merged_clean.to_csv(out_path, index=False)
        print(f"[+] Wrote {out_path} ({len(merged_clean)} rows)")

        # Quick class balance summary
        print("\nClass distribution:")
        print(merged_clean["label"].value_counts())

        print("\nDone. Use `tle_features_labeled.csv` for training, and keep `tle_features_all.csv` for inference/EDA.")

    except requests.HTTPError as e:
        print("HTTP error while downloading datasets:", e)
        sys.exit(1)
    except Exception as e:
        print("Unexpected error:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()
