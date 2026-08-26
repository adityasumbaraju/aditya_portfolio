"""
Sensitivity Analysis - ranking stability under correlation and data-quality uncertainty.

Tests how investment rankings change under:
  1. Observed Gaussian copula (baseline, preserves correlation structure)
  2. Independent sampling (removes all inter-variable dependence)
  3. Student-t copula (df=5, adds tail dependence)
  4. Data-quality degradation (0%, 10%, 25%: shrinks correlations toward zero)

Also runs a bootstrap analysis (100 resamples) confirming the persistence of
the reranking effect.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scenarios import ScenarioA, ScenarioB, ScenarioC
from utils.copula import (
    generate_gaussian_copula_samples,
    generate_t_copula_samples,
    generate_independent_samples,
)

CONFIG_PATH = Path("config/params_config.json")
OUTPUT_DIR = Path("outputs")


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_scenarios_on_samples(u_samples, params, threshold):
    scenario_classes = [(ScenarioA, "A"), (ScenarioB, "B"), (ScenarioC, "C")]
    results = {}
    for scenario_class, name in scenario_classes:
        scenario = scenario_class(params)
        samples = scenario.transform_uniform_to_variables(u_samples)
        roi = scenario.calculate_roi(samples)
        results[name] = {
            "mean_roi": float(np.mean(roi)),
            "std_roi": float(np.std(roi)),
            "p5_roi": float(np.percentile(roi, 5)),
            "p95_roi": float(np.percentile(roi, 95)),
            "threshold_exceedance": float(np.mean(roi > threshold)),
        }
    return results


def main():
    params = load_config(CONFIG_PATH)
    n = params["simulation"]["n_iterations"]
    seed = params["simulation"]["random_seed"]
    threshold = params["analysis"]["threshold_exceedance_roi"]
    corr = np.array(params["correlation_matrix"]["matrix"], dtype=float)
    n_vars = len(params["correlation_matrix"]["variables"])

    all_results = {}

    # 1. Observed Gaussian copula
    u = generate_gaussian_copula_samples(corr, n, random_seed=seed)
    all_results["observed_gaussian"] = run_scenarios_on_samples(u, params, threshold)

    # 2. Independent sampling
    u = generate_independent_samples(n_vars, n, random_seed=seed)
    all_results["independent"] = run_scenarios_on_samples(u, params, threshold)

    # 3. Student-t copula (df=5)
    u = generate_t_copula_samples(corr, n, df=5, random_seed=seed)
    all_results["t_copula_df5"] = run_scenarios_on_samples(u, params, threshold)

    # 4. Data-quality degradation (shrink correlations toward zero)
    for deg in [0.0, 0.10, 0.25]:
        degraded = np.eye(n_vars) + (corr - np.eye(n_vars)) * (1 - deg)
        u = generate_gaussian_copula_samples(degraded, n, random_seed=seed)
        all_results[f"degradation_{int(deg*100)}pct"] = run_scenarios_on_samples(u, params, threshold)

    # Bootstrap analysis: 100 resamples of the observed-Gaussian ROI distributions
    u = generate_gaussian_copula_samples(corr, n, random_seed=seed)
    bootstrap_counts = {"A_beats_B_by_prob": 0}
    for i in range(100):
        rng = np.random.default_rng(seed + i)
        idx = rng.integers(0, n, size=n)
        u_b = u[idx]
        res = run_scenarios_on_samples(u_b, params, threshold)
        if res["B"]["threshold_exceedance"] > res["A"]["threshold_exceedance"]:
            bootstrap_counts["A_beats_B_by_prob"] += 1
    all_results["bootstrap_100_resamples"] = {
        "B_overtakes_A_in_n_of_100": bootstrap_counts["A_beats_B_by_prob"]
    }

    # Export
    rows = []
    for test_name, test_results in all_results.items():
        if "threshold_exceedance" not in str(test_results):
            rows.append({"test": test_name, **test_results})
            continue
        for s, m in test_results.items():
            rows.append({"test": test_name, "scenario": s, **m})
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "sensitivity_analysis.csv", index=False)
    with open(OUTPUT_DIR / "sensitivity_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # Summary
    print("\n" + "=" * 80)
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("=" * 80)
    for test_name, test_results in all_results.items():
        print(f"\n{test_name}:")
        if isinstance(test_results, dict) and "B_overtakes_A_in_n_of_100" in test_results:
            print(f"  B overtakes A in {test_results['B_overtakes_A_in_n_of_100']} of 100 bootstrap resamples")
            continue
        for s, m in test_results.items():
            print(f"  Scenario {s}: mean={m['mean_roi']*100:.1f}% SD={m['std_roi']*100:.1f}pts P(ROI>8%)={m['threshold_exceedance']*100:.1f}%")


if __name__ == "__main__":
    main()
