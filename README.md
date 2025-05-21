
# 🛰 Space Debris Tracker

**Author:** Fenil Modi  
**Status:** Phase 5 Complete ✅  
**Goal:** Predict and visualize satellite orbits and detect potential collisions using real-world space data.

---

## 📌 Project Description

This project fetches real-time satellite TLE data, predicts current and future orbital positions, detects close approaches, and visualizes orbits using both 2D and animated world maps.

Future goals include 3D orbital visualization and web integration.

---

## 🧠 Features

- ✅ Fetch live satellite TLE data from Celestrak
- ✅ Parse and predict satellite positions using Skyfield
- ✅ Visualize satellites on a 2D Earth map (static + animated)
- ✅ Predict close approaches and alert potential collisions
- ✅ Label satellites in animated plots
- ⏳ 3D orbital plot in development (PyVista)

---

## 📂 Project Structure

```
space-debris-tracker/
│
├── backend/
│   ├── main.py                # Orchestrates the full pipeline
│   ├── tle_fetcher.py         # Downloads and saves latest TLEs
│   ├── orbit_predictor.py     # Parses TLEs and predicts current positions
│   ├── visualizer.py          # 2D + animated Earth map plots
│   ├── collision_checker.py   # Checks for possible collisions
│   └── orbit_plotter.py       # (Coming Soon) 3D orbital visualization
│
├── data/                      # Stores fetched TLE data
│
├── docs/                      # Flowcharts, diagrams, and report assets
│
├── tests/                     # Placeholder for testing scripts
│
└── README.md
```

---

## 🧪 Sample Output

```
[2.5/3] Checking for close approaches...
⚠️  Close approach: GPS BIIR-2 ↔ GPS BIIRM-4 — 6.82 km at 17:24:30
```

---

## 🔧 Technologies Used

- **Python**
- **Skyfield** – for orbital mechanics
- **Cartopy + Matplotlib** – for map rendering
- **NumPy** – vector math
- **PyVista** – (coming) for 3D orbit plots

---

## 🚧 Roadmap

- [x] Phase 1: Project setup and fetcher
- [x] Phase 2: Position predictor
- [x] Phase 3: Static map visualization
- [x] Phase 4: Animated visualization with labels
- [x] Phase 5: Collision detection
- [ ] Phase 6: Flask/FastAPI backend
- [ ] Phase 7: PyVista 3D orbit visualization
- [ ] Phase 8: Report + university submission

---

## 📜 License

MIT (to be confirmed)
