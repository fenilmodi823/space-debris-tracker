# 🛰️ Space Debris Tracker

**Author:** Fenil Modi  
**Status:** Phase 9 – Machine Learning Integration & Finalization  
**Objective:** Predict satellite orbits, detect potential collisions, classify objects using ML, and visualize Earth’s orbital environment in 2D and 3D.

---

## 🌍 Project Overview

**Space Debris Tracker** is a Python-based satellite tracking system that:

- Fetches live orbital data (TLEs) from CelesTrak
- Predicts orbital positions using astronomical algorithms (Skyfield)
- Uses **Machine Learning** to classify objects as Payloads, Rocket Bodies, or Debris
- Visualizes satellites in 2D (Cartopy + Matplotlib) and interactive 3D (PyVista)
- Detects close approaches between objects and issues alerts
- Highlights famous satellites like the **ISS**, **Hubble**, **Starlink**, **Landsat**, and **Sentinel**

Originally designed as a final-year engineering capstone, the project also serves as a foundation for future real-time web integration and educational outreach.

---

## ✨ Features

- ✅ Real-time TLE fetching from [CelesTrak](https://celestrak.org)
- ✅ Machine Learning–based object classification
- ✅ Load and visualize famous satellites (ISS, Hubble, etc.)
- ✅ Position prediction using Skyfield
- ✅ 2D static and animated Earth maps (Cartopy + Matplotlib)
- ✅ Collision detection engine with ML-aware proximity alerts
- ✅ 3D Earth visualization with altitude rings (LEO, MEO, GEO)
- ✅ ML color-coding for Payload, Rocket Body, and Debris
- ⏳ Interactive UI panels and full web deployment (planned)

---

## 📁 Project Structure

```text
space-debris-tracker/
├─ pyproject.toml              # Project metadata & dependencies (Python 3.11)
├─ requirements.txt            # Pinned dependencies
├─ README.md                   # You are here
│
├─ assets/
│  ├─ models/
│  │  ├─ earth/
│  │  │   earth.glb
│  │  │   earth.mtl
│  │  │   earth.obj
│  │  └─ satellites/
│  │      Hubble Space Telescope (A).glb
│  │      International Space Station (ISS) (A).glb
│  └─ textures/
│      clouds.png
│      earth_day.jpg
│
├─ backend/
│  ├─ .env                     # NASA API key, config (not committed to GitHub)
│  ├─ __init__.py              # Makes `backend` a package
│  ├─ main.py                  # Main entry: python -m backend.main
│  ├─ build_dataset.py         # Build CSV dataset from TLEs
│  ├─ check_dataset.py         # Quick sanity checks on CSV
│  ├─ collision_checker.py     # Close-approach detection
│  ├─ config.py                # Central config (paths, thresholds, API base URLs)
│  ├─ nasa_client.py           # NASA API access helpers
│  ├─ orbit_plotter.py         # 3D PyVista orbit visualization
│  ├─ orbit_predictor.py       # Time-step prediction of orbits from TLE
│  ├─ test_utils_temp.py       # Temporary/manual test helpers
│  ├─ tle_fetcher.py           # Fetches and stores TLE files
│  ├─ train_model.py           # Trains ML classifier from features CSV
│  ├─ utils.py                 # Common utilities (time, distance, ML colors, etc.)
│  ├─ visualizer.py            # 2D Cartopy visualizations (static + animated)
│  │
│  ├─ scripts/
│  │  ├─ health_check.py       # Basic project health checks
│  │  ├─ run_health.ps1        # PowerShell runner for health_check
│  │  ├─ test_nasa_client.py   # Test NASA connectivity & responses
│  │  ├─ test_tle_fetch.py     # Quick TLE fetch tests
│  │  ├─ verify_cleanup.py     # Sanity check for generated files
│  │  └─ _init_.py             # (typo; should be __init__.py if used as package)
│  │
│  ├─ utils/
│  │  └─ _init_.py             # (placeholder for future shared utilities)
│  └─ __pycache__/             # Python cache (ignored by git)
│
├─ data/
│  ├─ latest_tle.txt           # Last downloaded TLE snapshot
│  ├─ tle_features_all.csv     # Extracted features for many objects
│  ├─ tle_features_labeled.csv # Labeled feature dataset (for ML training)
│  │
│  ├─ famous_tles/
│  │  └─ famous.txt            # TLEs for selected famous satellites (ISS, Hubble…)
│  └─ tle/
│     └─ active/
│         YYYYMMDD_HHMMSS.tle  # Historical TLE snapshots
│
├─ ml_models/
│  └─ object_classifier.joblib # Trained RandomForest classifier
│
├─ models/
│  ├─ iss.obj
│  └─ iss.mtl                  # Standalone ISS model (legacy)
│
├─ screenshots/
│  └─ orbit_view_*.png         # Saved PyVista 3D orbit screenshots
│
├─ tests/
│  ├─ sample.tle
│  ├─ test_orbit_predictor.py  # Unit tests for orbit time-steps
│  └─ test_time_steps.py       # Additional time-step logic tests
│
└─ tools/
   └─ fix_backend_imports.py   # Helper script for import path cleanup
```

---

## 🖼️ Sample Output

[1/4] Fetching latest TLE data...
[✔] TLE data saved to data/latest_tle.txt

[2/4] Loading famous satellites from CelesTrak...
✔ Total satellites loaded: 5

[3/4] Checking for close approaches...
Close approach: STARLINK-1234 [Debris 88%] ↔ STARLINK-5678 [Payload 92%] — 4.32 km at 12:15:30
✔ Collision analysis complete.

[4/4] Visualizing satellite orbits...
✔ Interactive 3D Earth launched with ML color-coded trails

---

## 🧪 Technologies Used

- **Python 3**
- **Skyfield** – orbital mechanics and TLE parsing
- **scikit-learn + imbalanced-learn** – ML classification
- **pandas / NumPy** – data wrangling & computation
- **Cartopy + Matplotlib** – 2D static & animated maps
- **PyVista** – interactive 3D visualization
- **Requests** – API & data fetching
- **Joblib** – model persistence

---

## 🗺️ Development Roadmap

| Phase | Feature                                   | Status         |
| ----- | ----------------------------------------- | -------------- |
| 1     | Project Setup + TLE Fetcher               | ✅ Complete    |
| 2     | Position Prediction                       | ✅ Complete    |
| 3     | 2D Static Map                             | ✅ Complete    |
| 4     | Animated Orbit Map                        | ✅ Complete    |
| 5     | Collision Detection                       | ✅ Complete    |
| 6     | Flask / FastAPI Backend                   | ⏳ On Hold     |
| 7     | Interactive 3D Orbit Visualization        | ✅ Complete    |
| 8     | Famous Satellite Tracking (Live)          | ✅ Complete    |
| 9     | Machine Learning Object Classification    | ✅ Complete    |
| 10    | Overlay UI Panels, Object Info, Filtering | 🔜 In Progress |
| 11    | Final Report, Submission, Packaging       | 🔜 Upcoming    |

---

## 📚 References

- [Celestrak TLE Data](https://celestrak.org/NORAD/elements/)
- [LeoLabs Visualization (Inspiration)](https://platform.leolabs.space/visualizations/leo)
- [Skyfield Documentation](https://rhodesmill.org/skyfield/)
- [PyVista Documentation](https://docs.pyvista.org/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)

---

## 📜 License

MIT License _(to be confirmed at final stage)_

---

> “Making space situational awareness accessible and visual — now with machine learning.” 🌌
