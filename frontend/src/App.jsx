import React, { useState, useEffect, useMemo } from "react";
import {
  Viewer,
  Entity,
  PointGraphics,
  LabelGraphics,
  PolylineGraphics,
  EllipsoidGraphics,
} from "resium";
import {
  Cartesian3,
  Color,
  CallbackProperty,
  DistanceDisplayCondition,
  JulianDate,
} from "cesium";
import * as satellite from "satellite.js";
import "cesium/Build/Cesium/Widgets/widgets.css";

function App() {
  const [satellites, setSatellites] = useState([]);
  const [selectedSat, setSelectedSat] = useState(null);
  const [trackedEntity, setTrackedEntity] = useState(null);

  const [showLEO, setShowLEO] = useState(true);
  const [showMEO, setShowMEO] = useState(true);
  const [showGEO, setShowGEO] = useState(true);

  // Pre-process satellite records efficiently so we don't recalculate strings
  const satRecords = useMemo(() => {
    return satellites
      .filter((s) => s.line1 && s.line2)
      .map((sat) => ({
        ...sat,
        satrec: satellite.twoline2satrec(sat.line1, sat.line2),
      }));
  }, [satellites]);

  // Static API fetch - data only updates occasionally since motion is dynamically handled client-side
  useEffect(() => {
    const fetchSatellites = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/satellites`);
        if (response.ok) {
          const data = await response.json();
          setSatellites(data);
        }
      } catch (error) {
        console.error("Failed to fetch satellites:", error);
      }
    };

    fetchSatellites();
    // Fetch every 30 seconds since TLE lines don't change that frequently
    const interval = setInterval(fetchSatellites, 30000);
    return () => clearInterval(interval);
  }, []);

  // Hook into native Cesium Viewer Events
  const handleSelectedEntityChanged = (entity) => {
    if (entity && entity.id) {
      const sat = satRecords.find((s) => s.name === entity.id);
      setSelectedSat(sat || null);
      setTrackedEntity(entity);
    } else {
      setSelectedSat(null);
      setTrackedEntity(null);
    }
  };

  const filterBtnStyle = (active) => ({
    padding: "10px",
    background: active ? "#2e7d32" : "#444",
    color: "white",
    border: "1px solid #666",
    borderRadius: "4px",
    cursor: "pointer",
    fontWeight: "bold",
    transition: "0.2s",
    fontFamily: "sans-serif",
  });

  return (
    <>
      {/* UI Overlay - TOP LEFT */}
      <div
        style={{
          position: "absolute",
          top: 20,
          left: 20,
          zIndex: 10,
          backgroundColor: "rgba(10,10,15,0.85)",
          padding: "15px 25px",
          borderRadius: "8px",
          border: "1px solid #333",
          color: "white",
          fontFamily: "sans-serif",
          boxShadow: "0 4px 15px rgba(0,0,0,0.5)",
          pointerEvents: "auto",
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize: "24px",
            fontWeight: "bold",
            color: "#00ffcc",
          }}
        >
          Space Debris Tracker
        </h1>
        <p
          style={{
            margin: "5px 0 0",
            opacity: 0.8,
            fontSize: "14px",
            letterSpacing: "1px",
            textTransform: "uppercase",
          }}
        >
          Cesium WebGL Engine
        </p>
      </div>

      {/* Selected Satellite Info Card - UNDER TITLE */}
      {selectedSat && (
        <div
          style={{
            position: "absolute",
            top: 110,
            left: 20,
            zIndex: 10,
            backgroundColor: "rgba(10,10,15,0.9)",
            padding: "15px 25px",
            borderRadius: "8px",
            color: "white",
            minWidth: "220px",
            borderLeft: "4px solid #00ffcc",
            fontFamily: "sans-serif",
            borderTop: "1px solid #333",
            borderRight: "1px solid #333",
            borderBottom: "1px solid #333",
            boxShadow: "0 4px 15px rgba(0,0,0,0.5)",
            pointerEvents: "auto",
          }}
        >
          <h2 style={{ margin: 0, fontSize: "18px", color: "#fff" }}>
            {selectedSat.name}
          </h2>
          <div
            style={{
              margin: "12px 0",
              fontSize: "12px",
              opacity: 0.7,
              fontFamily: "monospace",
            }}
          >
            NORAD ID: {selectedSat.line1.substring(2, 7).trim()}
            <br />
            Status: Active Tracking
          </div>
          <p style={{ margin: "15px 0 0 0" }}>
            <a
              href={`https://www.n2yo.com/satellite/?s=${selectedSat.line1.substring(2, 7).trim()}`}
              target="_blank"
              rel="noreferrer"
              style={{
                color: "#000",
                backgroundColor: "#00ffcc",
                textDecoration: "none",
                padding: "6px 12px",
                borderRadius: "4px",
                fontWeight: "bold",
                fontSize: "12px",
                display: "inline-block",
                textTransform: "uppercase",
              }}
            >
              Analyze Telemetry
            </a>
          </p>
        </div>
      )}

      {/* Filter UI Panel - TOP RIGHT */}
      <div
        style={{
          position: "absolute",
          top: 20,
          right: 20,
          zIndex: 10,
          backgroundColor: "rgba(10,10,15,0.85)",
          padding: "15px",
          borderRadius: "8px",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          fontFamily: "sans-serif",
          border: "1px solid #333",
          boxShadow: "0 4px 15px rgba(0,0,0,0.5)",
          pointerEvents: "auto",
        }}
      >
        <h3
          style={{
            margin: "0 0 10px 0",
            color: "#fff",
            fontSize: "14px",
            textAlign: "center",
            letterSpacing: "1px",
            textTransform: "uppercase",
          }}
        >
          Orbital Shells
        </h3>
        <button
          style={filterBtnStyle(showLEO)}
          onClick={() => setShowLEO(!showLEO)}
        >
          LEO (&lt; 2000km)
        </button>
        <button
          style={filterBtnStyle(showMEO)}
          onClick={() => setShowMEO(!showMEO)}
        >
          MEO (2000-35786km)
        </button>
        <button
          style={filterBtnStyle(showGEO)}
          onClick={() => setShowGEO(!showGEO)}
        >
          GEO (&gt; 35786km)
        </button>
      </div>

      <Viewer
        full
        timeline={false}
        animation={true}
        baseLayerPicker={true}
        infoBox={false}
        selectionIndicator={false}
        scene3DOnly={true}
        shadows={true}
        onSelectedEntityChanged={handleSelectedEntityChanged}
        trackedEntity={trackedEntity}
      >
        {/* Orbit Structural Shells */}
        {showLEO && (
          <Entity position={Cartesian3.ZERO}>
            <EllipsoidGraphics
              radii={
                new Cartesian3(
                  6371000 + 2000000,
                  6371000 + 2000000,
                  6371000 + 2000000,
                )
              }
              material={Color.CYAN.withAlpha(0.02)}
              outline={true}
              outlineColor={Color.CYAN.withAlpha(0.1)}
            />
          </Entity>
        )}
        {showMEO && (
          <Entity position={Cartesian3.ZERO}>
            <EllipsoidGraphics
              radii={
                new Cartesian3(
                  6371000 + 20000000,
                  6371000 + 20000000,
                  6371000 + 20000000,
                )
              }
              material={Color.ORANGE.withAlpha(0.02)}
              outline={true}
              outlineColor={Color.ORANGE.withAlpha(0.08)}
            />
          </Entity>
        )}
        {showGEO && (
          <Entity position={Cartesian3.ZERO}>
            <EllipsoidGraphics
              radii={
                new Cartesian3(
                  6371000 + 35786000,
                  6371000 + 35786000,
                  6371000 + 35786000,
                )
              }
              material={Color.MAGENTA.withAlpha(0.02)}
              outline={true}
              outlineColor={Color.MAGENTA.withAlpha(0.08)}
            />
          </Entity>
        )}

        {/* Dynamic Navigational Entities */}
        {satRecords.map((sat) => {
          const isSelected = selectedSat && selectedSat.name === sat.name;

          // 1. 60FPS Callback Property for Native Smooth Movement
          const positionProperty = new CallbackProperty((time) => {
            const jsDate = JulianDate.toDate(time);
            const posVel = satellite.propagate(sat.satrec, jsDate);

            if (posVel.position && posVel.position !== true) {
              const gmst = satellite.gstime(jsDate);
              const geodetic = satellite.eciToGeodetic(posVel.position, gmst);
              const lat = satellite.degreesLat(geodetic.latitude);
              const lon = satellite.degreesLong(geodetic.longitude);
              const alt = geodetic.height * 1000; // satellite.js exposes km, Cesium requires meters!

              if (isNaN(lat) || isNaN(lon) || isNaN(alt))
                return Cartesian3.ZERO;
              return Cartesian3.fromDegrees(lon, lat, alt);
            }
            return Cartesian3.ZERO;
          }, false);

          // 2. Trajectory Generation (Only generated & pushed if heavily selected)
          let pathProperty = null;
          if (isSelected) {
            pathProperty = new CallbackProperty((time) => {
              const points = [];
              const period = (2 * Math.PI) / sat.satrec.no; // Total orbital period in minutes

              for (let i = 0; i <= 120; i++) {
                const offset = (i / 120) * period;
                const simDate = new Date(
                  JulianDate.toDate(time).getTime() + offset * 60000,
                );

                const posVel = satellite.propagate(sat.satrec, simDate);
                if (posVel.position && posVel.position !== true) {
                  const gmst = satellite.gstime(simDate);
                  const geodetic = satellite.eciToGeodetic(
                    posVel.position,
                    gmst,
                  );
                  const lat = satellite.degreesLat(geodetic.latitude);
                  const lon = satellite.degreesLong(geodetic.longitude);
                  const alt = geodetic.height * 1000;
                  if (!isNaN(lat) && !isNaN(lon) && !isNaN(alt)) {
                    points.push(Cartesian3.fromDegrees(lon, lat, alt));
                  }
                }
              }
              return points;
            }, false);
          }

          return (
            <Entity
              key={sat.name}
              id={sat.name}
              name={sat.name}
              position={positionProperty}
            >
              <PointGraphics
                pixelSize={isSelected ? 14 : 8}
                color={sat.alert ? Color.RED : Color.LIME}
                outlineColor={Color.WHITE}
                outlineWidth={isSelected ? 2 : 0}
                // GPU Culling Optimization
                distanceDisplayCondition={
                  new DistanceDisplayCondition(0.0, 45000000.0)
                }
              />
              <LabelGraphics
                text={sat.name}
                font="14px sans-serif"
                fillColor={Color.WHITE}
                outlineColor={Color.BLACK}
                outlineWidth={2}
                pixelOffset={{ x: 0, y: -20 }}
                showBackground={true}
                backgroundColor={new Color(0.1, 0.1, 0.1, 0.8)}
                // GPU Text Culling Optimization (fades when camera zooms back too far)
                distanceDisplayCondition={
                  new DistanceDisplayCondition(0.0, 25000000.0)
                }
              />

              {/* Plot Future Trajectory Path exactly matching mathematical period */}
              {isSelected && (
                <PolylineGraphics
                  positions={pathProperty}
                  width={2}
                  material={Color.CYAN.withAlpha(0.6)}
                />
              )}
            </Entity>
          );
        })}
      </Viewer>
    </>
  );
}

export default App;
