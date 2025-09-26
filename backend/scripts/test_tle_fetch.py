# Ensure project root is on sys.path when running via "python backend/scripts/..."
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_REPO = _THIS.parents[2]  # D:\VS Code\Space Debris Tracker
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# You can also run this script as a module from the repo root:
#   python -m backend.scripts.test_tle_fetch

import sys
from pathlib import Path

# import path setup
this = Path(__file__).resolve()
repo = this.parents[2]
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "backend"))

from backend.tle_fetcher import fetch_tle, get_latest_tle_path

if __name__ == "__main__":
    path, text = fetch_tle(group="active", cache_minutes=180)
    count = len([ln for ln in text.splitlines() if ln.strip()]) // 3
    print(f"[OK] Fetched {count} TLE objects. Saved at: {path}")
    print(f"[Latest] {get_latest_tle_path('active')}")
