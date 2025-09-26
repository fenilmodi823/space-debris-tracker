# backend/scripts/test_nasa_client.py

import sys
from pathlib import Path

# Ensure project root is on sys.path
THIS = Path(__file__).resolve()
REPO = THIS.parents[2]  # .../Space Debris Tracker/
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from backend.nasa_client import fetch_donki_notifications, fetch_neo_today

if __name__ == "__main__":
    donki = fetch_donki_notifications()
    neo = fetch_neo_today()
    print("DONKI items:", len(donki["data"]))
    print("NEO element_count:", neo["data"].get("element_count"))
