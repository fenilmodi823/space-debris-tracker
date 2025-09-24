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
Space Debris Tracker/
|-- LICENSE
|-- README.md
|-- requirements.txt
|-- assets/
|   |-- models/
|   |   |-- earth/
|   |   |   |-- earth.glb
|   |   |   |-- earth.mtl
|   |   |   \-- earth.obj
|   |   \-- satellites/
|   |       |-- Hubble Space Telescope (A).glb
|   |       \-- International Space Station (ISS) (A).glb
|   \-- textures/
|       |-- clouds.png
|       \-- earth_day.jpg
|-- backend/
|   |-- build_dataset.py
|   |-- check_dataset.py
|   |-- collision_checker.py
|   |-- config.py
|   |-- main.py
|   |-- orbit_plotter.py
|   |-- orbit_predictor.py
|   |-- tle_fetcher.py
|   |-- train_model.py
|   |-- utils.py
|   |-- visualizer.py
|   |-- __init__.py
|   \-- __pycache__/
|       |-- collision_checker.cpython-313.pyc
|       |-- orbit_plotter.cpython-313.pyc
|       |-- orbit_predictor.cpython-313.pyc
|       |-- poliastro.cpython-313.pyc
|       |-- tle_fetcher.cpython-313.pyc
|       |-- utils.cpython-313.pyc
|       |-- visualizer.cpython-313.pyc
|       \-- __init__.cpython-313.pyc
|-- data/
|   |-- latest_tle.txt
|   |-- tle_features_all.csv
|   |-- tle_features_labeled.csv
|   \-- famous_tles/
|       \-- famous.txt
|-- docs/
|-- kernels/
|-- ml_models/
|   \-- object_classifier.joblib
|-- models/
|   |-- iss.mtl
|   \-- iss.obj
|-- notebooks/
|-- screenshots/
\-- tests/
    |-- sample.tle
    |-- test_orbit_predictor.py
    \-- test_time_steps.py
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

| Phase | Feature                                      | Status        |
|-------|----------------------------------------------|---------------|
| 1     | Project Setup + TLE Fetcher                  | ✅ Complete    |
| 2     | Position Prediction                          | ✅ Complete    |
| 3     | 2D Static Map                                | ✅ Complete    |
| 4     | Animated Orbit Map                           | ✅ Complete    |
| 5     | Collision Detection                          | ✅ Complete    |
| 6     | Flask / FastAPI Backend                      | ⏳ On Hold     |
| 7     | Interactive 3D Orbit Visualization           | ✅ Complete    |
| 8     | Famous Satellite Tracking (Live)             | ✅ Complete    |
| 9     | Machine Learning Object Classification       | ✅ Complete    |
| 10    | Overlay UI Panels, Object Info, Filtering    | 🔜 In Progress |
| 11    | Final Report, Submission, Packaging          | 🔜 Upcoming    |

---

## 📚 References

- [Celestrak TLE Data](https://celestrak.org/NORAD/elements/)  
- [LeoLabs Visualization (Inspiration)](https://platform.leolabs.space/visualizations/leo)  
- [Skyfield Documentation](https://rhodesmill.org/skyfield/)  
- [PyVista Documentation](https://docs.pyvista.org/)  
- [scikit-learn Documentation](https://scikit-learn.org/stable/)  

---

## 📜 License

MIT License *(to be confirmed at final stage)*

---

> “Making space situational awareness accessible and visual — now with machine learning.” 🌌
