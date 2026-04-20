import os
import matplotlib.pyplot as plt

# Ensure the 'figures' directory exists
os.makedirs("figures", exist_ok=True)

# Data matching the enhanced report metrics
features = [
    "Inclination",
    "Orbital Altitude",
    "Orbital Eccentricity",
    "Scalar Velocity",
]
importances = [0.15, 0.20, 0.25, 0.40]

# Setup the plot
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(
    features, importances, color=["#7f7f7f", "#7f7f7f", "#1f77b4", "#1f77b4"]
)

# Add data labels
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.01,
        bar.get_y() + bar.get_height() / 2,
        f"{width:.2f}",
        ha="left",
        va="center",
        fontweight="bold",
    )

# Formatting for academic report
ax.set_xlabel("Relative Importance (Gini Information Gain)", fontsize=11)
ax.set_title("Random Forest Feature Importance Profile", fontsize=14, fontweight="bold")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
plt.xlim(0, 0.45)
plt.tight_layout()

# Save to the 'figures' directory
save_path = os.path.join("figures", "Figure_6_6_Feature_Importance.png")
plt.savefig(save_path, dpi=300)
print(f"Saved: {save_path}")
plt.show()
