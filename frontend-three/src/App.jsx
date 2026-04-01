import React, { useState, useEffect, useRef, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
  OrbitControls,
  Stars,
  useTexture,
  Text,
  Line,
} from "@react-three/drei";
import * as THREE from "three";
import * as satellite from "satellite.js";
import Select from "react-select";

const IRIDIUM_33_TLE = {
  name: "IRIDIUM 33 (2009 COLLISION)",
  line1:
    "1 24946U 97051C   09040.85227702  .00000185  00000-0  45155-4 0  4245",
  line2:
    "2 24946  86.3986 244.4714 0002167 259.0763 101.0069 14.34215865593881",
};
const COSMOS_2251_TLE = {
  name: "COSMOS 2251 (DERELICT)",
  line1:
    "1 22675U 93036A   09041.01815132  .00000067  00000-0  21183-4 0  9154",
  line2:
    "2 22675  74.0483 283.4385 0015509 255.4859 104.4770 14.28313437775569",
};

// Dynamic Earth component updating rotation based on GMST
function DynamicEarth({ offsetMinutes, baseTime }) {
  const groupRef = useRef();
  const [earthTexture, cloudsTexture] = useTexture([
    "/textures/earth_day.jpg",
    "/textures/clouds.png",
  ]);

  useFrame(() => {
    if (groupRef.current) {
      const simulatedDate = new Date(baseTime + offsetMinutes * 60000);
      const gmst = satellite.gstime(simulatedDate);
      groupRef.current.rotation.y = gmst + Math.PI; // Adjust base orientation + GMST rotation
    }
  });

  return (
    <group ref={groupRef}>
      {/* Base Earth */}
      <mesh>
        <sphereGeometry args={[10, 64, 64]} />
        <meshStandardMaterial
          map={earthTexture}
          roughness={0.9}
          metalness={0.15}
        />
      </mesh>
      {/* Clouds Layer */}
      <mesh>
        <sphereGeometry args={[10.1, 64, 64]} />
        <meshStandardMaterial
          map={cloudsTexture}
          transparent={true}
          opacity={0.4}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}

function DensityHeatmap() {
  const groupRef = useRef();

  useFrame(({ clock }) => {
    if (groupRef.current) {
      // Very slow, menacing pulse
      const pulse = 1 + Math.sin(clock.elapsedTime) * 0.05;
      groupRef.current.scale.set(pulse, pulse, pulse);
    }
  });

  return (
    <group ref={groupRef}>
      {/* LEO (High Risk - Red) */}
      <mesh>
        <sphereGeometry args={[11.5, 64, 64]} />
        <meshBasicMaterial
          color="#ff0000"
          transparent
          opacity={0.15}
          side={THREE.DoubleSide}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      {/* MEO (Medium Risk - Yellow) */}
      <mesh>
        <sphereGeometry args={[20.0, 64, 64]} />
        <meshBasicMaterial
          color="#ffaa00"
          transparent
          opacity={0.08}
          side={THREE.DoubleSide}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      {/* GEO (Low Risk - Green) */}
      <mesh>
        <sphereGeometry args={[42.0, 64, 64]} />
        <meshBasicMaterial
          color="#00ffaa"
          transparent
          opacity={0.05}
          side={THREE.DoubleSide}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}

// Kessler Syndrome Swarm rendering 10k items via one draw call (InstancedMesh)
function DebrisSwarm() {
  const meshRef = useRef();
  const count = 10000;

  const object3D = useMemo(() => new THREE.Object3D(), []);

  useEffect(() => {
    if (!meshRef.current) return;

    for (let i = 0; i < count; i++) {
      // Create a spherical shell for LEO (10.3 to 11.5)
      const r = 10.3 + Math.random() * 1.2;
      const theta = Math.random() * 2 * Math.PI; // azimuthal
      const phi = Math.acos(Math.random() * 2 - 1); // polar angle

      // Spherical to Cartesian
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);

      object3D.position.set(x, y, z);

      // Random subtle rotation and scale for debris
      object3D.rotation.set(
        Math.random() * Math.PI,
        Math.random() * Math.PI,
        Math.random() * Math.PI,
      );
      const scale = 0.5 + Math.random() * 1.5;
      object3D.scale.set(scale, scale, scale);

      object3D.updateMatrix();
      meshRef.current.setMatrixAt(i, object3D.matrix);
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
  }, [count, object3D]);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0005;
      meshRef.current.rotation.x += 0.0002;
    }
  });

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <dodecahedronGeometry args={[0.01, 0]} /> {/* Tiny jagged rocks */}
      <meshBasicMaterial color="#aaaaaa" transparent opacity={0.6} />
    </instancedMesh>
  );
}

// Camera locking controller
function CameraController({
  selectedSat,
  offsetMinutes,
  resetTrigger,
  baseTime,
}) {
  const { camera, controls } = useThree();
  const isReturning = useRef(false);
  const prevSat = useRef(null);

  const satrec = useMemo(() => {
    if (!selectedSat) return null;
    return satellite.twoline2satrec(selectedSat.line1, selectedSat.line2);
  }, [selectedSat]);

  useEffect(() => {
    if (selectedSat) {
      // Cancel flight and unlock controls if they click a new satellite
      isReturning.current = false;
      // eslint-disable-next-line react-hooks/immutability
      if (controls) controls.enabled = true;
    } else if (!selectedSat && prevSat.current) {
      // Trigger flight home
      isReturning.current = true;
    }
    prevSat.current = selectedSat;
  }, [selectedSat, controls]);

  useEffect(() => {
    if (resetTrigger > 0) {
      isReturning.current = true;
      // eslint-disable-next-line react-hooks/immutability
      if (controls) controls.enabled = false;
    }
  }, [resetTrigger, controls]);

  useFrame(() => {
    if (!controls) return;

    if (selectedSat && satrec) {
      const simulatedDate = new Date(baseTime + offsetMinutes * 60000);
      const posVel = satellite.propagate(satrec, simulatedDate);
      if (posVel.position && posVel.position !== true) {
        const pos = posVel.position;
        const scale = 10 / 6371.0;
        // Smoothly track the moving satellite
        controls.target.lerp(
          new THREE.Vector3(pos.x * scale, pos.z * scale, -pos.y * scale),
          0.1,
        );
      }
    } else if (isReturning.current) {
      // eslint-disable-next-line react-hooks/immutability
      controls.enabled = false;

      const targetCenter = new THREE.Vector3(0, 0, 0);

      // 1. Smoothly pan the target back to the Earth's core
      controls.target.lerp(targetCenter, 0.05);

      // 2. Push the camera straight backward to a radius of 40 units
      // This preserves the user's current viewing angle so OrbitControls doesn't fight it
      const targetPos = camera.position.clone().normalize().multiplyScalar(40);
      camera.position.lerp(targetPos, 0.05);

      // 3. Unlock once the target is centered and the camera reaches the 40-unit radius
      if (
        controls.target.distanceTo(targetCenter) < 0.5 &&
        camera.position.distanceTo(targetPos) < 0.5
      ) {
        isReturning.current = false;
        controls.enabled = true;
      }
    }
    controls.update();
  });

  return null;
}

// Satellite Mesh Component Handles Own Tracking & Rendering Locally
function SatelliteMesh({
  sat,
  offsetMinutes,
  selectedSat,
  setSelectedSat,
  baseTime,
}) {
  const groupRef = useRef();
  const textRef = useRef();
  const [hovered, setHovered] = useState(false);

  // Memoize parsing the satellite string to avoid performance issues
  const satrec = useMemo(
    () => satellite.twoline2satrec(sat.line1, sat.line2),
    [sat.line1, sat.line2],
  );

  useEffect(() => {
    document.body.style.cursor = hovered ? "pointer" : "auto";
    return () => {
      document.body.style.cursor = "auto";
    };
  }, [hovered]);

  // Orbit path generation
  const isSelected = selectedSat?.name === sat.name;
  const orbitPoints = useMemo(() => {
    if (!isSelected) return [];

    const pts = [];
    const baseTimeCalc = baseTime + offsetMinutes * 60000;
    const period = (2 * Math.PI) / satrec.no; // Exact time for 1 full orbit in minutes

    for (let i = 0; i <= 120; i++) {
      const offset = (i / 120) * period; // Map 120 segments to the full exact period
      const simDate = new Date(baseTimeCalc + offset * 60000);
      const posVel = satellite.propagate(satrec, simDate);

      if (posVel.position && posVel.position !== true) {
        const pos = posVel.position;
        const scale = 10 / 6371.0;
        pts.push(
          new THREE.Vector3(pos.x * scale, pos.z * scale, -pos.y * scale),
        );
      }
    }
    return pts;
  }, [isSelected, satrec, offsetMinutes, baseTime]);

  // Calculate position and distance on every frame (60fps smooth propagation)
  useFrame(({ camera }) => {
    const simulatedDate = new Date(baseTime + offsetMinutes * 60000);
    const positionAndVelocity = satellite.propagate(satrec, simulatedDate);

    // Only update if propagation resolves successfully
    if (positionAndVelocity.position && positionAndVelocity.position !== true) {
      const position = positionAndVelocity.position;
      const scale = 10 / 6371.0;

      // ECI coordinates to Three.js mapping (swap Z and Y, negate orig Y)
      const tx = position.x * scale;
      const ty = position.z * scale;
      const tz = -position.y * scale;

      const currentPos = new THREE.Vector3(tx, ty, tz);

      // Snap the group position to the accurate Cartesian vector
      if (groupRef.current) {
        groupRef.current.position.copy(currentPos);
      }

      const dist = camera.position.distanceTo(currentPos);
      let calculatedOpacity = 1;

      if (dist > 35) {
        calculatedOpacity = 0;
      } else if (dist > 20) {
        // Smooth interpolation between 20 and 35
        calculatedOpacity = 1 - (dist - 20) / 15;
      }

      // Override calculate opacity if the user is hovering OR if it's selected
      const finalOpacity = hovered || isSelected ? 1 : calculatedOpacity;

      if (textRef.current) {
        // Fade both the fill and the outline to prevent ghost borders
        textRef.current.fillOpacity = finalOpacity;
        textRef.current.outlineOpacity = finalOpacity;
        textRef.current.quaternion.copy(camera.quaternion); // Forces text to face the camera
      }
    }
  });

  const size = sat.alert ? 0.08 : 0.05;
  const color = sat.alert ? "red" : "lime";

  return (
    <>
      <group ref={groupRef}>
        <mesh
          // Important: Stop propagation prevents clicks from hitting background elements
          onClick={(e) => {
            e.stopPropagation();
            setSelectedSat(sat);
          }}
          onPointerOver={(e) => {
            e.stopPropagation();
            setHovered(true);
          }}
          onPointerOut={() => setHovered(false)}
        >
          <sphereGeometry args={[size, 16, 16]} />
          <meshBasicMaterial color={color} />
        </mesh>
        <Text
          ref={textRef}
          position={[0, 0.3, 0]}
          fontSize={0.25}
          color="white"
          anchorX="center"
          anchorY="bottom"
          outlineWidth={0.02}
          outlineColor="black"
          scale={hovered || isSelected ? [1.5, 1.5, 1.5] : [1, 1, 1]}
        >
          {sat.name}
        </Text>
      </group>

      {isSelected && orbitPoints.length > 0 && (
        <Line
          points={orbitPoints}
          color="cyan"
          lineWidth={1}
          transparent
          opacity={0.5}
        />
      )}
    </>
  );
}

function calcTelemetry(satrec) {
  const posVel = satellite.propagate(satrec, new Date());
  let velocity = 0;
  if (posVel.velocity && posVel.velocity !== true) {
    const { x, y, z } = posVel.velocity;
    velocity = Math.sqrt(x * x + y * y + z * z);
  }
  const a = satrec.a * 6371.0;
  const e = satrec.ecco;
  const perigee = a * (1 - e) - 6371.0;
  const apogee = a * (1 + e) - 6371.0;

  return {
    velocity: velocity.toFixed(2),
    perigee: perigee.toFixed(1),
    apogee: apogee.toFixed(1),
  };
}

// ML Collision Simulation visual component
function CollisionEvent({ target, offsetMinutes, baseTime }) {
  const groupRef = useRef();
  const rogueRef = useRef();
  const covRef = useRef();
  const satrec = useMemo(
    () => satellite.twoline2satrec(target.line1, target.line2),
    [target],
  );

  useFrame(({ clock }) => {
    // 1. Move the local group vector exactly to the target's current propagation
    const simulatedDate = new Date(baseTime + offsetMinutes * 60000);
    const posVel = satellite.propagate(satrec, simulatedDate);

    if (posVel.position && posVel.position !== true) {
      const pos = posVel.position;
      const scale = 10 / 6371.0;
      const currentPos = new THREE.Vector3(
        pos.x * scale,
        pos.z * scale,
        -pos.y * scale,
      );
      if (groupRef.current) groupRef.current.position.copy(currentPos);
    }

    // 2. Animate incoming rogue satellite directly past the target origin [0,0,0] inside local group space
    if (rogueRef.current) {
      const startVec = new THREE.Vector3(5, 2, -5);
      const endVec = new THREE.Vector3(-5, -2, 4.8);
      const progress = (clock.elapsedTime % 60) / 60; // 60 second professional near-miss sequence
      rogueRef.current.position.lerpVectors(startVec, endVec, progress);
    }

    // 3. Pulsating State Vector Uncertainty Zone
    if (covRef.current) {
      const pulse = 1 + Math.sin(clock.elapsedTime * 4) * 0.1;
      covRef.current.scale.set(pulse, pulse, pulse);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Danger Zone Reference Shell */}
      <mesh>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial color="red" wireframe transparent opacity={0.5} />
      </mesh>

      {/* State Vector Uncertainty Zone */}
      <mesh ref={covRef}>
        <sphereGeometry args={[0.6, 1.2, 0.6]} />
        <meshBasicMaterial color="#ffaa00" transparent opacity={0.3} />
      </mesh>

      {/* High-Velocity Rogue Satellite */}
      <mesh ref={rogueRef}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshBasicMaterial color="#ff8800" />
      </mesh>

      {/* Rogue Trajectory Path */}
      <Line
        points={[
          [5, 2, -5],
          [-5, -2, 4.8],
        ]}
        color="#ff8800"
        lineWidth={2}
        dashed
        dashSize={0.2}
        gapSize={0.1}
        transparent
        opacity={0.25}
      />

      {/* Primary Forward Vector */}
      <Line
        points={[
          [0, 0, 0],
          [0, 0, 3],
        ]}
        color="red"
        lineWidth={3}
      />
    </group>
  );
}

function SunLight({ offsetMinutes, baseTime }) {
  const sunLightRef = useRef();

  useFrame(() => {
    if (sunLightRef.current) {
      const simulatedDate = new Date(baseTime + offsetMinutes * 60000);
      const hours =
        simulatedDate.getUTCHours() + simulatedDate.getUTCMinutes() / 60;
      const angle = (hours / 24) * Math.PI * 2 + Math.PI;
      sunLightRef.current.position.set(
        Math.cos(angle) * 50,
        0,
        Math.sin(angle) * 50,
      );
    }
  });

  return <directionalLight ref={sunLightRef} intensity={2.5} color="#fffcf2" />;
}

const calculateKesslerDensity = (sat) => {
  if (!sat) return 0;
  const satrec = satellite.twoline2satrec(sat.line1, sat.line2);
  const a = satrec.a * 6371.0;
  const e = satrec.ecco;
  const perigee = a * (1 - e) - 6371.0;

  let score = 2.0;
  if (perigee > 700 && perigee < 1200) {
    score = 9.5 - Math.abs(900 - perigee) / 100;
  } else if (perigee < 700) {
    score = (perigee / 700) * 8.0;
  } else {
    score = Math.max(1.0, 8.0 - (perigee - 1200) / 1000);
  }
  return Math.max(0.1, Math.min(10.0, score));
};

function App() {
  const [satellites, setSatellites] = useState([]);
  const [offsetMinutes, setOffsetMinutes] = useState(0);
  const [baseTime, setBaseTime] = useState(() => Date.now());
  const [playbackRate, setPlaybackRate] = useState(0);
  const [selectedSat, setSelectedSat] = useState(null);

  const [showLEO, setShowLEO] = useState(true);
  const [showMEO, setShowMEO] = useState(true);
  const [showGEO, setShowGEO] = useState(true);

  const [showControls, setShowControls] = useState(true);
  const [resetTrigger, setResetTrigger] = useState(0);

  const [isSimulating, setIsSimulating] = useState(false);
  const [demoTarget, setDemoTarget] = useState(null);
  const [_simTelemetry, setSimTelemetry] = useState({ primary: {}, rogue: {} });
  const [simElapsed, setSimElapsed] = useState(0);
  const [telemetry, setTelemetry] = useState(null);
  const [showSwarm, setShowSwarm] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);

  // Live Geodetic Telemetry Loop
  useEffect(() => {
    if (!selectedSat || isSimulating) return;

    const interval = setInterval(() => {
      const simulatedDate = new Date(baseTime + offsetMinutes * 60000);
      const satrec = satellite.twoline2satrec(
        selectedSat.line1,
        selectedSat.line2,
      );
      const posVel = satellite.propagate(satrec, simulatedDate);

      if (posVel.position && posVel.velocity && posVel.position !== true) {
        const position = posVel.position;
        const velocity = posVel.velocity;

        const gmst = satellite.gstime(simulatedDate);
        const positionGd = satellite.eciToGeodetic(position, gmst);

        const lon = satellite.degreesLong(positionGd.longitude);
        const lat = satellite.degreesLat(positionGd.latitude);
        const height = positionGd.height;

        const v = Math.sqrt(
          velocity.x * velocity.x +
            velocity.y * velocity.y +
            velocity.z * velocity.z,
        );
        const inc = satrec.inclo * (180 / Math.PI); // radians to degrees
        const period = (2 * Math.PI) / satrec.no; // minutes

        setTelemetry({
          lon,
          lat,
          height,
          velocity: v,
          inclination: inc,
          period,
        });
      }
    }, 500);

    return () => clearInterval(interval);
  }, [selectedSat, isSimulating, offsetMinutes, baseTime]);

  useEffect(() => {
    let timer;
    if (isSimulating) {
      const start = Date.now();
      timer = setInterval(
        () => setSimElapsed((Date.now() - start) / 1000),
        250,
      );
    }
    return () => clearInterval(timer);
  }, [isSimulating]);

  const loadHistoricalCollision = () => {
    setBaseTime(1234284600000); // Feb 10, 2009, 16:50:00 UTC (6 mins before impact)
    setOffsetMinutes(0);
    setSatellites([IRIDIUM_33_TLE, COSMOS_2251_TLE]);
    setSelectedSat(IRIDIUM_33_TLE);
    setPlaybackRate(0);
  };

  const runSimulation = () => {
    if (satellites.length > 0) {
      const target = satellites[0];
      const satrec = satellite.twoline2satrec(target.line1, target.line2);
      const targetData = calcTelemetry(satrec);

      setIsSimulating(true);
      setDemoTarget(target);
      setSelectedSat(target);
      setPlaybackRate(0);

      setSimTelemetry({
        primary: {
          name: target.name,
          speed: `${targetData.velocity} km/s`,
          perigee: `${targetData.perigee} km`,
          apogee: `${targetData.apogee} km`,
        },
        rogue: {
          name: "UNKNOWN KINEMATIC ANOMALY",
          speed: "12.41 km/s",
          perigee: "382.1 km",
          apogee: "520.4 km",
          angle: "68.2° (Hypervelocity)",
        },
      });
    }
  };

  const exportTelemetryCSV = () => {
    if (!selectedSat) return;

    let csvContent =
      "Time_Offset_Min,UTC_Time,Latitude,Longitude,Altitude_km,Velocity_km_s\n";
    const satrec = satellite.twoline2satrec(
      selectedSat.line1,
      selectedSat.line2,
    );

    for (let t = 0; t <= 90; t++) {
      const stepDate = new Date(baseTime + (offsetMinutes + t) * 60000);
      const posVel = satellite.propagate(satrec, stepDate);

      if (posVel.position && posVel.velocity && posVel.position !== true) {
        const position = posVel.position;
        const velocity = posVel.velocity;

        const gmst = satellite.gstime(stepDate);
        const positionGd = satellite.eciToGeodetic(position, gmst);

        const lon = satellite.degreesLong(positionGd.longitude);
        const lat = satellite.degreesLat(positionGd.latitude);
        const height = positionGd.height;

        const v = Math.sqrt(
          velocity.x * velocity.x +
            velocity.y * velocity.y +
            velocity.z * velocity.z,
        );

        csvContent += `${t},${stepDate.toISOString()},${lat.toFixed(4)},${lon.toFixed(4)},${height.toFixed(4)},${v.toFixed(4)}\n`;
      }
    }

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `${selectedSat.name.replace(/\s+/g, "_")}_telemetry.csv`,
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Time Scrubbing Interval Loop
  useEffect(() => {
    if (playbackRate === 0) return;
    const scrubber = setInterval(() => {
      setOffsetMinutes((prev) => prev + playbackRate);
    }, 1000);
    return () => clearInterval(scrubber);
  }, [playbackRate]);

  // Static API fetch - data only updates occasionally since motion is handled client-side
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
    // Fetch only every 30 seconds since TLE lines don't change that frequently
    const interval = setInterval(fetchSatellites, 30000);
    return () => clearInterval(interval);
  }, []); // Re-renders independent of offsetMinutes changes

  const glassPanelStyle = {
    background: "rgba(10, 10, 15, 0.75)",
    backdropFilter: "blur(16px)",
    WebkitBackdropFilter: "blur(16px)",
    border: "1px solid rgba(0, 255, 204, 0.2)",
    borderRadius: "12px",
    color: "#00ffcc",
    fontFamily: '"JetBrains Mono", monospace',
    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.6)",
    padding: "20px",
    pointerEvents: "auto",
  };

  const customSelectStyles = {
    control: (base) => ({
      ...base,
      background: "transparent",
      borderColor: "rgba(0, 255, 204, 0.5)",
      color: "#00ffcc",
      boxShadow: "none",
      "&:hover": { borderColor: "#00ffcc" },
    }),
    singleValue: (base) => ({ ...base, color: "#00ffcc" }),
    input: (base) => ({ ...base, color: "#00ffcc" }),
    menu: (base) => ({
      ...base,
      background: "rgba(10, 10, 15, 0.95)",
      border: "1px solid #00ffcc",
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isFocused
        ? "rgba(0, 255, 204, 0.2)"
        : "transparent",
      color: "#00ffcc",
      cursor: "pointer",
    }),
  };

  const btnStyle = {
    padding: "8px 16px",
    backgroundColor: "transparent",
    color: "#00ffcc",
    border: "1px solid rgba(0, 255, 204, 0.4)",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "bold",
    transition: "0.2s",
    fontFamily: "monospace",
  };

  const filterBtnStyle = (active) => ({
    padding: "10px",
    backgroundColor: active ? "rgba(0, 255, 204, 0.2)" : "transparent",
    color: active ? "#00ffcc" : "#aaa",
    border: "1px solid rgba(0, 255, 204, 0.4)",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "bold",
    textTransform: "uppercase",
    transition: "0.2s",
    fontFamily: "monospace",
  });

  return (
    <>
      {/* Target 2: Top-Left (Object Selection & Command) */}
      <div
        style={{
          ...glassPanelStyle,
          position: "absolute",
          top: "20px",
          left: "20px",
          zIndex: 100,
          minWidth: "300px",
        }}
      >
        <div
          style={{
            fontSize: "16px",
            fontWeight: "bold",
            letterSpacing: "2px",
            color: "#fff",
            marginBottom: "15px",
            borderBottom: "1px solid rgba(255,255,255,0.2)",
            paddingBottom: "10px",
          }}
        >
          SPACE DEBRIS TRACKING SYSTEM
        </div>
        <Select
          options={satellites.map((s) => ({ value: s, label: s.name }))}
          onChange={(opt) => setSelectedSat(opt.value)}
          styles={customSelectStyles}
          placeholder="SEARCH SAT_ID..."
          value={
            selectedSat ? { value: selectedSat, label: selectedSat.name } : null
          }
        />

        {selectedSat && (
          <a
            href={`https://www.n2yo.com/satellite/?s=${selectedSat.line1.substring(2, 7).trim()}`}
            target="_blank"
            rel="noreferrer"
            style={{
              display: "block",
              marginTop: "12px",
              color: "#00ffcc",
              textDecoration: "none",
              fontSize: "11px",
              border: "1px solid rgba(0, 255, 204, 0.4)",
              padding: "8px",
              textAlign: "center",
              borderRadius: "4px",
              letterSpacing: "1px",
              backgroundColor: "rgba(0, 255, 204, 0.05)",
            }}
          >
            [ OPEN EXTERNAL N2YO TELEMETRY ]
          </a>
        )}

        <button
          onClick={runSimulation}
          style={{
            marginTop: "15px",
            padding: "12px 24px",
            backgroundColor: "rgba(255, 50, 50, 0.1)",
            color: "#ff4444",
            border: "1px solid #ff4444",
            borderRadius: "4px",
            width: "100%",
            cursor: "pointer",
            fontWeight: "bold",
            letterSpacing: "1px",
            textTransform: "uppercase",
            transition: "all 0.3s ease",
          }}
        >
          ⚠️ RUN ML PREDICTION
        </button>
      </div>

      {/* Target 3: Top-Right (View & Tools) */}
      <div
        style={{
          ...glassPanelStyle,
          position: "absolute",
          top: "20px",
          right: "20px",
          zIndex: 100,
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        <h3
          style={{
            margin: "0 0 5px 0",
            color: "#00ffcc",
            fontSize: "12px",
            textAlign: "center",
            letterSpacing: "1px",
            textTransform: "uppercase",
          }}
        >
          FILTERS
        </h3>
        <button
          style={filterBtnStyle(showLEO)}
          onClick={() => setShowLEO(!showLEO)}
          title="Low Earth Orbit"
        >
          LEO
        </button>
        <button
          style={filterBtnStyle(showMEO)}
          onClick={() => setShowMEO(!showMEO)}
          title="Medium Earth Orbit"
        >
          MEO
        </button>
        <button
          style={filterBtnStyle(showGEO)}
          onClick={() => setShowGEO(!showGEO)}
          title="Geosynchronous"
        >
          GEO
        </button>
        <hr
          style={{
            width: "100%",
            borderColor: "rgba(0,255,204,0.2)",
            margin: "5px 0",
          }}
        />
        <button
          onClick={() => setShowControls(!showControls)}
          style={{ ...btnStyle, background: "rgba(0,0,0,0.5)" }}
          title="Toggle UI"
        >
          {showControls ? "◧ UI" : "◨ UI"}
        </button>
        <button
          onClick={() => {
            setResetTrigger((prev) => prev + 1);
            setIsSimulating(false);
            setSelectedSat(null);
            setDemoTarget(null);
          }}
          style={{ ...btnStyle, background: "rgba(0,0,0,0.5)" }}
          title="Reset Camera"
        >
          🌍 RESET
        </button>
        <button
          onClick={() => setShowSwarm(!showSwarm)}
          style={{
            ...btnStyle,
            background: showSwarm
              ? "rgba(255, 100, 50, 0.2)"
              : "rgba(0,0,0,0.5)",
            borderColor: showSwarm ? "#ff6633" : "rgba(0, 255, 204, 0.4)",
            color: showSwarm ? "#ff6633" : "#00ffcc",
          }}
          title="Toggle Debris Swarm"
        >
          {showSwarm ? "[X] HIDE KESSLER SWARM" : "[ ] SHOW KESSLER SWARM"}
        </button>
        <button
          onClick={loadHistoricalCollision}
          style={{
            ...btnStyle,
            background: "rgba(255, 50, 50, 0.1)",
            color: "#ff4444",
            borderColor: "#ff4444",
          }}
          title="Load 2009 Historical Collision Data"
        >
          [ ⏮️ 2009 IRIDIUM COLLISION ]
        </button>
        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          style={{
            ...btnStyle,
            marginTop: "10px",
            width: "100%",
            borderColor: showHeatmap ? "#ff0000" : "rgba(255,255,255,0.2)",
            color: showHeatmap ? "#ff0000" : "#fff",
          }}
        >
          {showHeatmap ? "[X] HIDE HEATMAP" : "[ ] SHOW DENSITY HEATMAP"}
        </button>
      </div>

      {/* Target 4: Bottom-Right (Unified Intelligence Hub) */}
      {(selectedSat || isSimulating) && (
        <div
          style={{
            ...glassPanelStyle,
            position: "absolute",
            bottom: "20px",
            right: "20px",
            zIndex: 100,
            borderLeft: isSimulating
              ? "4px solid #ff4444"
              : "4px solid #00ffcc",
            borderColor: isSimulating
              ? "rgba(255, 68, 68, 0.4)"
              : "rgba(0, 255, 204, 0.4)",
            minWidth: "360px",
          }}
        >
          {isSimulating ? (
            <>
              <div
                style={{
                  borderBottom: "1px solid #ff4444",
                  paddingBottom: "8px",
                  marginBottom: "12px",
                  color: "#ff4444",
                  fontWeight: "bold",
                }}
              >
                [!] SYSTEM OVERRIDE: CONJUNCTION ALERT
              </div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "8px",
                  fontSize: "12px",
                  fontFamily: '"JetBrains Mono", monospace',
                }}
              >
                <span style={{ color: "#aaa" }}>TARGET_ID:</span>
                <span style={{ color: "#fff", textAlign: "right" }}>
                  {demoTarget?.name || "UNKNOWN"}
                </span>

                <span style={{ color: "#aaa" }}>ROGUE_ID:</span>
                <span style={{ color: "#ffaaaa", textAlign: "right" }}>
                  UNTRACKED_DEBRIS_OBJ
                </span>

                <span style={{ color: "#aaa" }}>TCA:</span>
                <span
                  style={{
                    color: "#ff4444",
                    fontWeight: "bold",
                    textShadow: "0 0 5px #ff4444",
                    textAlign: "right",
                  }}
                >
                  T- {Math.max(0, 60 - Math.floor(simElapsed % 60))}s
                </span>

                <span style={{ color: "#aaa" }}>PROB_OF_COLLISION (Pc):</span>
                <span style={{ color: "#ff4444", textAlign: "right" }}>
                  9.34e-2 (93.4%)
                </span>

                <span style={{ color: "#aaa" }}>MISS_DISTANCE:</span>
                <span style={{ color: "#fff", textAlign: "right" }}>
                  48.2m ± 3.1m
                </span>

                <span style={{ color: "#aaa" }}>RELATIVE_VELOCITY:</span>
                <span style={{ color: "#fff", textAlign: "right" }}>
                  14.6 km/s
                </span>

                <span style={{ color: "#aaa" }}>COVARIANCE_INTERSECT:</span>
                <span style={{ color: "#00ffcc", textAlign: "right" }}>
                  TRUE (MA &lt; 2.0)
                </span>

                <span style={{ color: "#aaa" }}>ML_CONFIDENCE:</span>
                <span style={{ color: "#00ffcc", textAlign: "right" }}>
                  HIGH (RDR+OPT)
                </span>
              </div>
              <button
                onClick={() => {
                  setIsSimulating(false);
                  setDemoTarget(null);
                  setSelectedSat(null);
                  setSimElapsed(0);
                }}
                style={{
                  width: "100%",
                  marginTop: "15px",
                  padding: "10px",
                  backgroundColor: "rgba(255, 0, 0, 0.15)",
                  border: "1px solid #ff4444",
                  color: "#ff4444",
                  textTransform: "uppercase",
                  letterSpacing: "2px",
                  cursor: "pointer",
                  fontWeight: "bold",
                  fontFamily: '"JetBrains Mono", monospace',
                  transition: "0.2s",
                }}
              >
                [X] ABORT SIMULATION
              </button>
            </>
          ) : (
            <>
              <h2
                style={{
                  margin: "0 0 15px 0",
                  fontSize: "16px",
                  color: "#00ffcc",
                  textTransform: "uppercase",
                  borderBottom: "1px solid currentColor",
                  paddingBottom: "8px",
                }}
              >
                TELEMETRY DATALINK
              </h2>

              <div
                style={{
                  marginBottom: "15px",
                  color: "#ccc",
                  fontSize: "13px",
                  lineHeight: "1.6",
                }}
              >
                <div
                  style={{ display: "flex", justifyContent: "space-between" }}
                >
                  <span>TARGET_ID:</span> <strong>{selectedSat.name}</strong>
                </div>
                <div
                  style={{ display: "flex", justifyContent: "space-between" }}
                >
                  <span>NORAD_CAT:</span>{" "}
                  <strong>{selectedSat.line1.substring(2, 7).trim()}</strong>
                </div>
              </div>

              {telemetry && (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "8px",
                    fontSize: "12px",
                    fontFamily: '"JetBrains Mono", monospace',
                    marginBottom: "15px",
                  }}
                >
                  <span style={{ color: "#aaa" }}>LATITUDE:</span>
                  <span style={{ color: "#00ffcc", textAlign: "right" }}>
                    {telemetry.lat.toFixed(4)}°
                  </span>

                  <span style={{ color: "#aaa" }}>LONGITUDE:</span>
                  <span style={{ color: "#00ffcc", textAlign: "right" }}>
                    {telemetry.lon.toFixed(4)}°
                  </span>

                  <span style={{ color: "#aaa" }}>ALTITUDE:</span>
                  <span style={{ color: "#fff", textAlign: "right" }}>
                    {telemetry.height.toFixed(2)} km
                  </span>

                  <span style={{ color: "#aaa" }}>VELOCITY:</span>
                  <span style={{ color: "#fff", textAlign: "right" }}>
                    {telemetry.velocity.toFixed(2)} km/s
                  </span>

                  <span style={{ color: "#aaa" }}>INCLINATION:</span>
                  <span style={{ color: "#00ffcc", textAlign: "right" }}>
                    {telemetry.inclination.toFixed(2)}°
                  </span>

                  <span style={{ color: "#aaa" }}>ORBITAL PERIOD:</span>
                  <span style={{ color: "#00ffcc", textAlign: "right" }}>
                    {telemetry.period.toFixed(1)} min
                  </span>
                </div>
              )}

              <div>
                <h3
                  style={{
                    margin: "0 0 8px 0",
                    fontSize: "12px",
                    color: "#00ffcc",
                  }}
                >
                  [ORBITAL CONGESTION INDEX]
                </h3>
                <div
                  style={{ display: "flex", alignItems: "center", gap: "10px" }}
                >
                  <div
                    style={{
                      flex: 1,
                      height: "6px",
                      backgroundColor: "rgba(0,255,204,0.1)",
                      borderRadius: "3px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${(calculateKesslerDensity(selectedSat) / 10) * 100}%`,
                        height: "100%",
                        backgroundColor:
                          calculateKesslerDensity(selectedSat) > 7
                            ? "#ff4444"
                            : calculateKesslerDensity(selectedSat) > 4
                              ? "#ffaa00"
                              : "#00ffcc",
                      }}
                    />
                  </div>
                  <span
                    style={{
                      fontSize: "14px",
                      fontWeight: "bold",
                      color: "#fff",
                    }}
                  >
                    {calculateKesslerDensity(selectedSat).toFixed(1)}
                  </span>
                </div>
              </div>
              <button
                onClick={exportTelemetryCSV}
                style={{
                  width: "100%",
                  marginTop: "15px",
                  padding: "10px",
                  backgroundColor: "rgba(0, 255, 204, 0.1)",
                  border: "1px solid #00ffcc",
                  color: "#00ffcc",
                  cursor: "pointer",
                  fontFamily: "monospace",
                  fontWeight: "bold",
                  letterSpacing: "1px",
                  transition: "all 0.3s",
                }}
              >
                [↓] EXPORT DATA (CSV)
              </button>
            </>
          )}
        </div>
      )}

      {/* Target 1: Bottom-Center (Timeline Panel) */}
      {showControls && (
        <div
          style={{
            position: "absolute",
            bottom: "30px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 100,
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              ...glassPanelStyle,
              pointerEvents: "auto",
              display: "flex",
              alignItems: "center",
              gap: "20px",
              padding: "10px 30px",
              borderRadius: "30px",
            }}
          >
            <span
              style={{ color: "#fff", fontSize: "14px", fontWeight: "bold" }}
            >
              UTC:{" "}
              {new Date(baseTime + offsetMinutes * 60000)
                .toISOString()
                .substring(11, 19)}
            </span>
            <div style={{ display: "flex", gap: "10px" }}>
              <button
                style={{ ...btnStyle, border: "none" }}
                onClick={() => setPlaybackRate(-10)}
                title="Rewind"
              >
                ⏪
              </button>
              <button
                style={{ ...btnStyle, border: "none" }}
                onClick={() => setPlaybackRate(0)}
                title="Pause"
              >
                ⏸
              </button>
              <button
                style={{ ...btnStyle, border: "none" }}
                onClick={() => setPlaybackRate(10)}
                title="Fast Forward"
              >
                ⏩
              </button>
              <button
                style={{ ...btnStyle, border: "none", color: "#ff4444" }}
                onClick={() => {
                  setPlaybackRate(0);
                  setOffsetMinutes(0);
                  setBaseTime(Date.now());
                }}
                title="Go Live"
              >
                ◉
              </button>
            </div>
            <input
              type="range"
              min="-1440"
              max="1440"
              value={offsetMinutes}
              onChange={(e) => {
                setPlaybackRate(0);
                setOffsetMinutes(parseFloat(e.target.value));
              }}
              style={{
                width: "200px",
                cursor: "pointer",
                accentColor: "#00ffcc",
              }}
            />
          </div>
        </div>
      )}

      <Canvas camera={{ position: [0, 0, 25], fov: 45 }}>
        <SunLight offsetMinutes={offsetMinutes} baseTime={baseTime} />

        <Stars
          radius={300}
          depth={60}
          count={10000}
          factor={7}
          saturation={0}
          fade
        />

        <OrbitControls
          makeDefault
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
        />

        <CameraController
          selectedSat={selectedSat}
          offsetMinutes={offsetMinutes}
          resetTrigger={resetTrigger}
          baseTime={baseTime}
        />

        <DynamicEarth offsetMinutes={offsetMinutes} baseTime={baseTime} />

        {showSwarm && <DebrisSwarm />}
        {showHeatmap && <DensityHeatmap />}

        {/* Orbit Segments Map Visual Reference */}
        {showLEO && (
          <mesh>
            <sphereGeometry args={[13.14, 64, 64]} />
            <meshBasicMaterial
              wireframe
              transparent
              opacity={0.1}
              color="cyan"
            />
          </mesh>
        )}
        {showMEO && (
          <mesh>
            <sphereGeometry args={[41.39, 64, 64]} />
            <meshBasicMaterial
              wireframe
              transparent
              opacity={0.1}
              color="orange"
            />
          </mesh>
        )}
        {showGEO && (
          <mesh>
            <sphereGeometry args={[66.17, 64, 64]} />
            <meshBasicMaterial
              wireframe
              transparent
              opacity={0.1}
              color="magenta"
            />
          </mesh>
        )}

        {/* Dynamic Satellite Mesh Mapping */}
        {satellites.map((sat) => (
          <SatelliteMesh
            key={sat.name}
            sat={sat}
            offsetMinutes={offsetMinutes}
            selectedSat={selectedSat}
            setSelectedSat={setSelectedSat}
            baseTime={baseTime}
          />
        ))}

        {isSimulating && demoTarget && (
          <CollisionEvent
            target={demoTarget}
            offsetMinutes={offsetMinutes}
            baseTime={baseTime}
          />
        )}
      </Canvas>
    </>
  );
}

export default App;
