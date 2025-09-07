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

space-debris-tracker/
│
├── backend/
│ ├── main.py # Entry point and pipeline runner
│ ├── tle_fetcher.py # Downloads latest TLE data
│ ├── orbit_predictor.py # Loads satellites (general + famous)
│ ├── build_dataset.py # Creates ML dataset from TLE + SATCAT
│ ├── train_model.py # Trains classifier (Payload / R/B / Debris)
│ ├── check_dataset.py # Diagnostics for training CSV
│ ├── visualizer.py # 2D maps (static + animated)
│ ├── orbit_plotter.py # 3D orbital rendering with ML colors
│ ├── collision_checker.py # Detects close approaches
│ ├── utils.py # Shared helper functions
│ └── config.py # Centralized configuration
│
├── data/
│ ├── latest_tle.txt # Fresh TLE data from CelesTrak
│ ├── tle_features_all.csv # Raw ML features
│ └── tle_features_labeled.csv # Cleaned dataset with labels
│
├── ml_models/
│ └── object_classifier.joblib # Trained ML model
│
├── docs/ # Flowcharts, diagrams, final report
│
├── requirements.txt # Python dependencies
└── README.md

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
