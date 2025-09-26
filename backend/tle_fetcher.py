"""
TLE Fetcher with on-disk cache for CelesTrak.
- Fetches TLEs for a group (e.g., 'active', 'stations', 'starlink', etc.)
- Caches into data/tle/<group>/YYYYMMDD_HHMMSS.tle
- Reuses cache if it's still fresh (configurable minutes)
- Maintains data/latest_tle.txt as a convenience pointer
"""

from __future__ import annotations

import os
import time
import errno
import shutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional

# Import config
try:
    from backend.config import CELESTRAK_TLE_URL
except Exception:
    # fallback if run as a standalone (not recommended)
    from backend.config import CELESTRAK_TLE_URL# type: ignore

DATA_DIR = Path("data")
TLE_ROOT = DATA_DIR / "tle"
LATEST_TLE_POINTER = DATA_DIR / "latest_tle.txt"

DEFAULT_CACHE_MINUTES = 180  # 3 hours

def _ensure_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def _list_cached(group: str) -> list[Path]:
    d = TLE_ROOT / group
    if not d.exists():
        return []
    return sorted([p for p in d.glob("*.tle") if p.is_file()])

def _is_fresh(file: Path, cache_minutes: int) -> bool:
    if not file.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
    return age <= timedelta(minutes=cache_minutes)

def _validate_tle_text(text: str) -> None:
    """
    Basic sanity checks:
    - Total lines should be a multiple of 3 (name, line1, line2).
    - Line 1 should start with '1 ' and line 2 with '2 ' (for each triplet).
    We don't do deep checksum validation here; keep it light.
    """
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 3 or len(lines) % 3 != 0:
        raise ValueError("TLE content length is not a multiple of 3 lines.")

    for i in range(0, len(lines), 3):
        name, l1, l2 = lines[i], lines[i+1], lines[i+2]
        if not (l1.startswith("1 ") and l2.startswith("2 ")):
            raise ValueError(f"TLE lines malformed near object '{name[:40]}'.")

def _write_latest_pointer(target: Path) -> None:
    _ensure_dir(DATA_DIR)
    try:
        with LATEST_TLE_POINTER.open("w", encoding="utf-8") as f:
            f.write(str(target.resolve()))
    except Exception:
        # Non-fatal
        pass

def _count_objects_from_text(text: str) -> int:
    # each object consumes 3 lines (name, L1, L2)
    return len([ln for ln in text.splitlines() if ln.strip()]) // 3

def fetch_tle(group: str = "active",
              cache_minutes: int = DEFAULT_CACHE_MINUTES,
              base_url: Optional[str] = None) -> Tuple[Path, str]:
    """
    Fetch TLEs for the given group with caching.
    Returns (path_to_file, text_content).
    """
    base_url = base_url or CELESTRAK_TLE_URL

    # Ensure cache directory
    group_dir = TLE_ROOT / group
    _ensure_dir(group_dir)

    # 1) Reuse fresh cache if available
    cached = _list_cached(group)
    if cached:
        latest = cached[-1]
        if _is_fresh(latest, cache_minutes):
            text = latest.read_text(encoding="utf-8", errors="ignore")
            return latest, text

    # 2) Fetch from CelesTrak
    params = {}
    # If the configured URL doesn't already include GROUP, use params.
    # Our default CELESTRAK_TLE_URL includes ?GROUP=active&FORMAT=tle,
    # so we only override 'active' when group differs.
    if "GROUP=" not in (base_url or "") or group != "active":
        # CelesTrak gp.php supports GROUP and FORMAT=tle
        params["GROUP"] = group
        params["FORMAT"] = "tle"

    resp = requests.get(base_url, params=params or None, timeout=30)
    resp.raise_for_status()
    text = resp.text

    # 3) Validate and store
    _validate_tle_text(text)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = group_dir / f"{ts}.tle"
    out_path.write_text(text, encoding="utf-8")

    # Update latest pointer (best-effort)
    _write_latest_pointer(out_path)

    return out_path, text

def get_latest_tle_path(group: str = "active") -> Optional[Path]:
    """Return the newest cached TLE path for a group, if any."""
    cached = _list_cached(group)
    return cached[-1] if cached else None

def read_latest_tle(group: str = "active") -> Optional[str]:
    """Return text content of the newest cached TLE for a group, if any."""
    p = get_latest_tle_path(group)
    if p and p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")
    return None

if __name__ == "__main__":
    # Quick manual test
    path, txt = fetch_tle(group="active")
    print(f"[TLE] saved: {path}  objects={_count_objects_from_text(txt)}")
