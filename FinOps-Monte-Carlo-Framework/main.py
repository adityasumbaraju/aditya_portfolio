"""
FinOps Monte Carlo Framework - Master Simulation Runner

Runs the three investment scenarios (A: capacity expansion, B: automation,
C: governance) under the observed Gaussian-copula correlation structure and
produces Table V-equivalent statistics from a clean run of the committed code.

All ROI values are NPV-based (8% WACC, 3-year horizon). The decision threshold
is 8% (the WACC). 10,000 iterations per scenario; random seed 42.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scenarios import ScenarioA, ScenarioB, ScenarioC
from utils.copula import generate_gaussian_copula_samples, validate_correlation_matrix

CONFIG_PATH = Path("config/params_config.json")
OUTPUT_DIR = Path("outputs")


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    params = load_config(CONFIG_PATH)
    n_iterations = params["simulation"]["n_iterations"]
    seed = params["simulation"]["random_seed"]
    threshold = params["analysis"]["threshold_exceedance_roi"]

    corr_matrix = np.array(params["correlation_matrix"]["matrix"], dtype=float)
    validate_correlation_matrix(corr_matrix)

    # Generate Gaussian copula samples preserving the correlation structure
    u_samples = generate_gaussian_copula_samples(corr_matrix, n_iterations, random_seed=seed)

    scenario_classes = [(ScenarioA, "A"), (ScenarioB, "B"), (ScenarioC, "C")]
    results = {}
    distributions = {}

    for scenario_class, name in scenario_classes:
        scenario = scenario_class(params)
        samples = scenario.transform_uniform_to_variables(u_samples)
        roi = scenario.calculate_roi(samples)

        results[f"scenario_{name.lower()}"] = {
            "scenario": name,
            "mean_roi": float(np.mean(roi)),
            "std_roi": float(np.std(roi)),
            "p5_roi": float(np.percentile(roi, 5)),
            "p95_roi": float(np.percentile(roi, 95)),
            "threshold_exceedance": float(np.mean(roi > threshold)),
            "negative_roi_probability": float(np.mean(roi < 0)),
            "samples_count": int(len(roi)),
        }
        distributions[f"scenario_{name.lower()}"] = roi

    # Export
    OUTPUT_DIR.mkdir(exist_ok=True)
    pd.DataFrame(results).T.to_csv(OUTPUT_DIR / "roi_statistics.csv")
    pd.DataFrame(distributions).to_csv(OUTPUT_DIR / "roi_distributions.csv", index=False)
    with open(OUTPUT_DIR / "simulation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary (Table V)
    print("\n" + "=" * 80)
    print("MONTE CARLO SIMULATION RESULTS (10,000 iterations, 8% WACC)")
    print("=" * 80)
    print(f"{'Scenario':<12}{'Mean ROI':>12}{'SD (pts)':>12}{'5th pct':>12}{'95th pct':>12}{'P(ROI>8%)':>12}")
    print("-" * 80)
    for name in ["A", "B", "C"]:
        r = results[f"scenario_{name.lower()}"]
        print(f"{name:<12}{r['mean_roi']*100:>11.1f}%{r['std_roi']*100:>11.1f}{r['p5_roi']*100:>11.1f}%{r['p95_roi']*100:>11.1f}%{r['threshold_exceedance']*100:>11.1f}%")

    # Reranking check
    by_mean = sorted(["A", "B", "C"], key=lambda n: results[f"scenario_{n.lower()}"]["mean_roi"], reverse=True)
    by_prob = sorted(["A", "B", "C"], key=lambda n: results[f"scenario_{n.lower()}"]["threshold_exceedance"], reverse=True)
    print("\nRanking by mean ROI:        " + " > ".join(by_mean))
    print("Ranking by P(ROI > 8%):    " + " > ".join(by_prob))
    reranked = by_mean != by_prob
    print(f"Reranking under probabilistic rule: {'YES' if reranked else 'NO'}")


if __name__ == "__main__":
    main()
