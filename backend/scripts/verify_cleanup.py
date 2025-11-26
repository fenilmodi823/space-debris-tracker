import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.utils import get_utc_timestamp, calculate_distance_km
from backend.tle_fetcher import fetch_tle

def test_utils():
    print("Testing backend.utils...")
    ts = get_utc_timestamp()
    print(f"  get_utc_timestamp() -> {ts}")
    assert "UTC" in ts
    
    dist = calculate_distance_km([0, 0, 0], [3, 4, 0])
    print(f"  calculate_distance_km([0,0,0], [3,4,0]) -> {dist}")
    assert dist == 5.0
    print("[OK] backend.utils passed")

def test_tle_fetcher():
    print("Testing backend.tle_fetcher...")
    # Mocking requests or just checking import/syntax
    assert callable(fetch_tle)
    print("[OK] backend.tle_fetcher loaded and fetch_tle is callable")

if __name__ == "__main__":
    try:
        test_utils()
        test_tle_fetcher()
        print("\nALL CHECKS PASSED")
    except Exception as e:
        print(f"\nFAILED: {e}")
        sys.exit(1)
