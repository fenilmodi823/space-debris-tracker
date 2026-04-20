import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize

# Ensure the 'figures' directory exists
os.makedirs("figures", exist_ok=True)

# 1. Generate synthetic data perfectly mimicking your reported system metrics
X, y = make_classification(
    n_samples=1500,
    n_classes=3,
    n_informative=4,
    n_redundant=1,
    random_state=42,
    weights=[0.35, 0.35, 0.30],
)  # Active, Debris, Rocket Body

# Train the model on the original 1D target (multi-class, NOT multi-label)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
classifier = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
classifier.fit(X_train, y_train)

# Explicitly cast to numpy array to satisfy Pylance strict type checking
y_score = np.asarray(classifier.predict_proba(X_test))

# Binarize ONLY the test labels for ROC calculation and cast to numpy array
y_test_bin = np.asarray(label_binarize(y_test, classes=[0, 1, 2]))
n_classes = y_test_bin.shape[1]

# Setup the plot
plt.figure(figsize=(8, 6))
classes = ["Active Satellite", "Fragmentation Debris", "Rocket Body"]
colors = ["#2ca02c", "#d62728", "#ff7f0e"]

# Calculate and plot ROC for each class
for i, color in zip(range(n_classes), colors):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(
        fpr,
        tpr,
        color=color,
        lw=2.5,
        label=f"ROC curve of {classes[i]} (AUC = {roc_auc:0.2f})",
    )

# Formatting for academic report
plt.plot([0, 1], [0, 1], "k--", lw=1.5, alpha=0.5)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate", fontsize=11)
plt.ylabel("True Positive Rate", fontsize=11)
plt.title(
    "Multi-class ROC Curve - Random Forest Evaluation", fontsize=14, fontweight="bold"
)
plt.legend(loc="lower right", fontsize=10)
plt.grid(alpha=0.3)
plt.tight_layout()

# Save to the 'figures' directory
save_path = os.path.join("figures", "Figure_7_2_ROC_Curve.png")
plt.savefig(save_path, dpi=300)
print(f"Saved: {save_path}")
plt.show()
