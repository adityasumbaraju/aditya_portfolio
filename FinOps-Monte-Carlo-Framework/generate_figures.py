"""Generate Figure 1 (architecture) and Figure 2 (ROI distributions) for the manuscript."""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from scenarios import ScenarioA, ScenarioB, ScenarioC
from utils.copula import generate_gaussian_copula_samples

FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

# ---------- Figure 2: ROI distributions ----------
params = json.load(open("config/params_config.json"))
n = params["simulation"]["n_iterations"]
seed = params["simulation"]["random_seed"]
threshold = params["analysis"]["threshold_exceedance_roi"]
corr = np.array(params["correlation_matrix"]["matrix"], dtype=float)
u = generate_gaussian_copula_samples(corr, n, random_seed=seed)

roi_data = {}
for cls, name in [(ScenarioA, "A"), (ScenarioB, "B"), (ScenarioC, "C")]:
    s = cls(params)
    samples = s.transform_uniform_to_variables(u)
    roi_data[name] = s.calculate_roi(samples)

fig, ax = plt.subplots(figsize=(8, 4.5))
colors = {"A": "#2b6cb0", "B": "#2f855a", "C": "#b7791f"}
for name, roi in roi_data.items():
    ax.hist(roi, bins=60, alpha=0.6, label=f"Scenario {name}", color=colors[name], density=True)
ax.axvline(threshold, color="#c53030", linestyle="--", linewidth=1.5, label=f"8% ROI threshold")
ax.set_xlabel("ROI", fontsize=11)
ax.set_ylabel("Density", fontsize=11)
ax.set_title("Simulated ROI Distributions (10,000 iterations, 8% WACC)", fontsize=12)
ax.legend(fontsize=9)
ax.set_xlim(-0.4, 0.6)
plt.tight_layout()
plt.savefig(FIG_DIR / "figure2_roi_distributions.png", dpi=200)
print("saved figure2")

# ---------- Figure 1: architecture ----------
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
layers = [
    ("1. Demand Signal\nIngestion", "AWS Lambda\nCDC pipelines", "#3182ce"),
    ("2. ETL Pipeline\nOrchestration", "Apache Airflow\n(GCP Composer)", "#319795"),
    ("3. Data Lake\nAggregation", "GCP BigQuery\nAWS S3", "#6b46c1"),
    ("4. Monte Carlo\nSimulation Engine", "Python (NumPy,\nSciPy), Airflow DAGs", "#b7791f"),
    ("5. Financial Output\nIntegration", "Snowflake\nPower BI", "#c53030"),
]
x = 0.3
for title, tool, color in layers:
    box = FancyBboxPatch((x, 1.8), 1.7, 1.4, boxstyle="round,pad=0.08", linewidth=1.2, edgecolor="#444", facecolor=color, alpha=0.85)
    ax.add_patch(box)
    ax.text(x + 0.85, 3.05, title, ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.text(x + 0.85, 2.35, tool, ha="center", va="center", color="white", fontsize=7.2)
    if x + 1.7 < 9.5:
        arrow = FancyArrowPatch((x + 1.75, 2.5), (x + 2.15, 2.5), arrowstyle="-|>", mutation_scale=14, linewidth=1.3, color="#555")
        ax.add_patch(arrow)
    x += 1.9
ax.text(5, 0.9, "Schema contracts and API boundaries between layers (pipeline-native, ERP-independent)", ha="center", fontsize=8, color="#555")
ax.text(5, 4.5, "Five-Layer Pipeline-Native Architecture", ha="center", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(FIG_DIR / "figure1_architecture.png", dpi=200)
print("saved figure1")
