# Ensure project root is on sys.path when running via "python backend/scripts/..."
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_REPO = _THIS.parents[2]  # D:\VS Code\Space Debris Tracker
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# You can also run this script as a module from the repo root:
#   python -m backend.scripts.health_check

import sys
import json
import requests
from requests.exceptions import RequestException, Timeout
from pathlib import Path

# Ensure we can import backend.config whether run from repo root or scripts/
this_file = Path(__file__).resolve()
repo_root = this_file.parents[2]  # .../Space Debris Tracker/
backend_root = repo_root / "backend"
sys.path.insert(0, str(repo_root))   # so 'backend' is importable as a package
sys.path.insert(0, str(backend_root))

try:
    from backend.config import NASA_API_KEY, DONKI_BASE, NEO_BASE, get_config_summary
except Exception as e:
    print(f"[IMPORT] Failed to import backend.config: {e}")
    sys.exit(1)

TIMEOUT = 20

def check_donki():
    url = f"{DONKI_BASE}/notifications"
    try:
        r = requests.get(url, params={"api_key": NASA_API_KEY}, timeout=TIMEOUT)
        ok = r.ok
        data = r.json() if ok else r.text
        count = len(data) if ok and isinstance(data, list) else None
        print(f"[DONKI] {r.status_code} {'OK' if ok else 'ERR'}", f"count={count}" if count is not None else "")
        return ok
    except (RequestException, Timeout) as e:
        print(f"[DONKI] ERR: {e}")
        return False

def check_neo_today():
    url = f"{NEO_BASE}/feed/today"
    try:
        r = requests.get(url, params={"detailed": "false", "api_key": NASA_API_KEY}, timeout=TIMEOUT)
        ok = r.ok
        if ok:
            payload = r.json()
            element_count = payload.get("element_count")
            print(f"[NEO] {r.status_code} OK element_count={element_count}")
        else:
            print(f"[NEO] {r.status_code} ERR {r.text[:300]}")
        return ok
    except (RequestException, Timeout) as e:
        print(f"[NEO] ERR: {e}")
        return False

def main():
    try:
        print(get_config_summary().rstrip())
    except Exception:
        # Config summary is optional; continue
        pass
    ok1 = check_donki()
    ok2 = check_neo_today()
    sys.exit(0 if (ok1 and ok2) else 1)

if __name__ == "__main__":
    main()

