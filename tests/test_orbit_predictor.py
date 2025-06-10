import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend import orbit_predictor


def test_load_tles_skips_malformed():
    sample_path = os.path.join(os.path.dirname(__file__), "sample.tle")
    sats = orbit_predictor.load_tles(sample_path)
    names = [sat.name for sat in sats]
    assert len(sats) == 2
    assert "MALFORMED SAT" not in names
    assert {"ISS (ZARYA)", "STARLINK-30000"} <= set(names)
