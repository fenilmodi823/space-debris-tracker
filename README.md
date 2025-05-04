# 🛰 Space Debris Tracker

**Author:** Fenil Modi  
**Status:** Development | Phase 3 Complete 🚀  
**Goal:** Predict and visualize satellite and debris trajectories, and alert relevant stakeholders about potential collision risks.

---

## 📝 Project Vision

Space debris poses significant risks to operational satellites and space missions.  
This project aims to:

- **Fetch** real-time orbital data (TLEs).
- **Predict** satellite positions using Skyfield and SGP4.
- **Visualize** satellite positions on a world map.
- Future phases: **Detect potential collisions** and build a web interface.

---

## 🔍 Tech Stack

**Language:** Python  
**Libraries/Tools:** 
- Skyfield
- SpiceyPy (future phase)
- Matplotlib + Cartopy (for visualization)
- NumPy
- Pandas

**(Future)** FastAPI or Flask backend | Plotly or CesiumJS for advanced visualization.

---

## 📂 Repository Structure

```plaintext
backend/
    main.py             # Master controller
    config.py           # Constants and file paths
    tle_fetcher.py      # Fetches latest TLE data
    orbit_predictor.py  # Parses TLEs and predicts satellite positions
    visualizer.py       # Plots satellite positions on world map

kernels/                # SPICE kernels (future use)
data/                   # Logs and fetched TLE data
notebooks/              # Experiments and prototype code
docs/                   # Diagrams and documentation
tests/                  # Placeholder for future tests
