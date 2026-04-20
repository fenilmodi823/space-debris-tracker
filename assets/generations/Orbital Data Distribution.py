import os
import numpy as np
import matplotlib.pyplot as plt

# Ensure the 'figures' directory exists
os.makedirs("figures", exist_ok=True)

# Synthetic data mimicking real Earth orbital distribution
np.random.seed(42)

# Active Payloads (Distinct clusters: LEO sun-synchronous and GEO)
alt_active = np.concatenate(
    [np.random.normal(600, 100, 150), np.random.normal(35786, 200, 100)]
)
inc_active = np.concatenate([np.random.normal(98, 2, 150), np.random.normal(0, 1, 100)])

# Fragmentation Debris (Heavy concentration in LEO)
alt_debris = np.random.normal(800, 250, 300)
inc_debris = np.random.normal(75, 15, 300)

# Rocket Bodies (Highly scattered transfer orbits)
alt_rocket = np.random.normal(1200, 400, 100)
inc_rocket = np.random.normal(65, 20, 100)

# Setup the plot
plt.figure(figsize=(9, 6))

# Plotting with distinct markers and colors
plt.scatter(
    alt_active,
    inc_active,
    c="#2ca02c",
    label="Active Satellite",
    alpha=0.7,
    edgecolors="w",
    s=45,
)
plt.scatter(
    alt_debris,
    inc_debris,
    c="#d62728",
    label="Fragmentation Debris",
    alpha=0.5,
    edgecolors="w",
    s=35,
    marker="X",
)
plt.scatter(
    alt_rocket,
    inc_rocket,
    c="#ff7f0e",
    label="Rocket Body",
    alpha=0.8,
    edgecolors="w",
    s=55,
    marker="^",
)

# Formatting for academic report
plt.xscale("log")  # Log scale is critical to show both LEO and GEO clearly
plt.xlabel("Orbital Altitude (km) - Logarithmic Scale", fontsize=11)
plt.ylabel("Orbital Inclination (Degrees)", fontsize=11)
plt.title(
    "Spatial Distribution of Tracked Orbital Objects", fontsize=14, fontweight="bold"
)
plt.legend(loc="upper left", framealpha=0.9)
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.tight_layout()

# Save to the 'figures' directory
save_path = os.path.join("figures", "Figure_6_5_Data_Distribution.png")
plt.savefig(save_path, dpi=300)
print(f"Saved: {save_path}")
plt.show()
