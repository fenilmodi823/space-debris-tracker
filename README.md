# 🛰️ Space Debris Tracker

**Author:** Fenil Modi  
**Status:** Phase 8 – Advanced Visualization & Documentation  
**Objective:** Predict satellite orbits, detect potential collisions, and visualize Earth’s orbital environment using real-time data.

---

## 🌍 Project Overview

**Space Debris Tracker** is a Python-based satellite tracking system that:

- Fetches live TLE data from Celestrak  
- Predicts orbital paths using astronomical algorithms  
- Visualizes satellites in 2D and interactive 3D views  
- Tracks close approaches between objects  
- Highlights famous satellites like the **ISS**, **Hubble**, **Starlink**, **Landsat**, and **Sentinel**

Designed as a final-year engineering capstone with goals extending toward education, outreach, and future real-time web integration.

---

## ✨ Features

- ✅ Real-time TLE fetching from [Celestrak](https://celestrak.org)  
- ✅ Load and visualize well-known satellites  
- ✅ Position prediction using Skyfield  
- ✅ 2D static and animated Earth maps (Cartopy + Matplotlib)  
- ✅ Collision detection engine with proximity alerts  
- ✅ 3D Earth visualization using PyVista  
- ✅ Altitude rings (LEO, MEO, GEO) with color-coded shells  
- ⏳ Info overlay panes and UI interactivity (planned)

---

## 📁 Project Structure

space-debris-tracker/
│
├── backend/
│ ├── main.py # Entry point and pipeline runner
│ ├── tle_fetcher.py # Downloads latest TLE data
│ ├── orbit_predictor.py # Loads all satellites + famous ones
│ ├── visualizer.py # 2D Earth map rendering (static + animated)
│ ├── orbit_plotter.py # 3D orbital rendering using PyVista
│ ├── collision_checker.py # Detects close approaches
│
├── data/
│ ├── latest_tle.txt # Fresh TLE data from Celestrak
│ └── famous_tles/ # Backup TLEs for key satellites
│
├── docs/ # Flowcharts, diagrams, final report
│
└── README.md

---

## 🖼️ Sample Output

[2/4] Loaded 31 satellites from TLE
[+] Loaded 5 famous satellites from live sources
[3/4] Checking for close approaches...
✔ No close approaches found within threshold.
[4/4] Rendering orbits in 3D...
✔ Interactive globe launched with labeled trails and shells


---

## 🧪 Technologies Used

- **Python 3**
- **Skyfield** – Accurate orbital mechanics
- **Cartopy** – Geographic projections
- **Matplotlib** – Static and animated 2D visualization
- **PyVista** – Real-time 3D orbit viewer
- **NumPy** – Mathematical computations
- **Requests** – API and TLE fetching

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
| 9     | Overlay UI Panels, Object Info, Filtering    | 🔜 In Progress |
| 10    | Final Report, Submission, Packaging          | 🔜 Upcoming    |

---

## 📚 References

- [Celestrak TLE Data](https://celestrak.org/NORAD/elements/)  
- [LeoLabs Visualization (Inspiration)](https://platform.leolabs.space/visualizations/leo)  
- [Skyfield Documentation](https://rhodesmill.org/skyfield/)  
- [PyVista Documentation](https://docs.pyvista.org/)

---

## 📜 License

MIT License *(to be confirmed at final stage)*

---

> “Making space situational awareness accessible and visual — one orbit at a time.” 🌌
