"""
Lightweight cached client for NASA DONKI & NEO APIs.
- Caches to data/cache/donki/ and data/cache/neo/
- Freshness windows:
    DONKI:  60 minutes (change if needed)
    NEO:    60 minutes (change if needed)
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests

# Import config (already set up in earlier steps)
try:
    from backend.config import NASA_API_KEY, DONKI_BASE, NEO_BASE
except Exception:
    # Fallback if executed oddly (not recommended)
    from backend.config import NASA_API_KEY, DONKI_BASE, NEO_BASE# type: ignore

DATA_DIR = Path("data")
CACHE_ROOT = DATA_DIR / "cache"
DONKI_DIR = CACHE_ROOT / "donki"
NEO_DIR   = CACHE_ROOT / "neo"

DONKI_FRESH_MIN = 60  # minutes
NEO_FRESH_MIN   = 60  # minutes

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def _is_fresh(file: Path, minutes: int) -> bool:
    if not file.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
    return age <= timedelta(minutes=minutes)

def _latest_json_in(dirpath: Path) -> Optional[Path]:
    if not dirpath.exists():
        return None
    files = sorted([p for p in dirpath.glob("*.json") if p.is_file()])
    return files[-1] if files else None

def _save_json(dirpath: Path, payload: Any) -> Path:
    _ensure_dir(dirpath)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = dirpath / f"{ts}.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out

def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def fetch_donki_notifications(use_cache: bool = True) -> Dict[str, Any]:
    """
    Returns {"source":"cache|network", "path":<Path>, "data":<list>}
    """
    _ensure_dir(DONKI_DIR)
    latest = _latest_json_in(DONKI_DIR)

    if use_cache and latest and _is_fresh(latest, DONKI_FRESH_MIN):
        return {"source": "cache", "path": str(latest), "data": _read_json(latest)}

    url = f"{DONKI_BASE}/notifications"
    r = requests.get(url, params={"api_key": NASA_API_KEY}, timeout=30)
    r.raise_for_status()
    data = r.json()
    saved = _save_json(DONKI_DIR, data)
    return {"source": "network", "path": str(saved), "data": data}

def fetch_neo_today(use_cache: bool = True) -> Dict[str, Any]:
    """
    Returns {"source":"cache|network", "path":<Path>, "data":<dict>}
    """
    _ensure_dir(NEO_DIR)
    latest = _latest_json_in(NEO_DIR)

    if use_cache and latest and _is_fresh(latest, NEO_FRESH_MIN):
        return {"source": "cache", "path": str(latest), "data": _read_json(latest)}

    url = f"{NEO_BASE}/feed/today"
    r = requests.get(url, params={"detailed": "false", "api_key": NASA_API_KEY}, timeout=30)
    r.raise_for_status()
    data = r.json()
    saved = _save_json(NEO_DIR, data)
    return {"source": "network", "path": str(saved), "data": data}
