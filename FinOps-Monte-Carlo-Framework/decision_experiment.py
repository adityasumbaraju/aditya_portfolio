"""
Synthetic Threshold-Criterion Recovery Experiment
=================================================

This module is a *synthetic* criterion-recovery test, NOT an empirical backtest
(no realized investment outcomes are available). It tests whether a probabilistic
decision rule (P(ROI > WACC)) recovers the true threshold-exceedance winner
under a synthetic data-generating process (DGP) that exhibits reranking.

This is a criterion-recovery test under the rule's own stated objective
(threshold exceedance), not a claim that the probabilistic rule is universally
superior or produces better decisions overall.

Method:
  1. Define a synthetic DGP with known mean and variance per scenario, where the
     highest-mean scenario (A) has the highest variance and a lower true
     P(ROI > WACC) than a lower-mean, lower-variance scenario (B). This mirrors
     the reranking structure of the calibrated framework.
  2. For each of N_trials: draw a finite sample, compute (a) the deterministic
     mean-ROI ranking and (b) the probabilistic P(ROI>WACC) ranking from the
     sample, then record whether each rule selected the true P(ROI>WACC) winner.
  3. Report the recovery rate of each rule, plus a risk-adjusted utility
     comparison (E[ROI] - lambda * shortfall_below_WACC) to show that the two
     rules optimize for different objectives rather than one dominating the other.

Honesty: the "ground truth" here is a specified DGP, not observed reality.
The experiment shows that, *when variance structure causes reranking*, a
probabilistic rule recovers the true threshold-exceedance winner where a
point-estimate rule cannot. It does not prove the probabilistic rule
outperforms DCF on real infrastructure.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUTPUT_DIR = Path("outputs")
WACC = 0.08
LAMBDA = 1.0  # risk-aversion on shortfall below WACC (tunable)


def true_scenario_params() -> dict:
    # Mirrors the calibrated framework: A high-mean/high-var, B lower/low-var.
    return {
        "A": {"mu": 0.145, "sigma": 0.069},
        "B": {"mu": 0.108, "sigma": 0.021},
        "C": {"mu": 0.095, "sigma": 0.041},
    }


def true_metrics(mu: float, sigma: float) -> tuple[float, float]:
    # Return (true mean ROI, true P(ROI > WACC)) for the normal DGP.
    from scipy.stats import norm

    p_exceed = 1.0 - norm.cdf(WACC, loc=mu, scale=sigma)
    return mu, p_exceed


def true_utility(mu: float, sigma: float) -> float:
    # Risk-adjusted expected utility: E[ROI] - lambda * E[max(WACC-ROI,0)]
    # computed by numerical integration over the normal DGP.
    from scipy.integrate import quad
    from scipy.stats import norm

    def shortfall_pdf(x):
        return max(WACC - x, 0.0) * norm.pdf(x, loc=mu, scale=sigma)

    expected_shortfall, _ = quad(shortfall_pdf, -np.inf, np.inf)
    return mu - LAMBDA * expected_shortfall


def select_deterministic(sample: dict) -> str:
    return max(sample, key=lambda s: sample[s].mean())


def select_probabilistic(sample: dict) -> str:
    return max(sample, key=lambda s: (sample[s] > WACC).mean())


def run_experiment(n_trials: int = 1000, n_per_trial: int = 200, seed: int = 42):
    rng = np.random.default_rng(seed)
    params = true_scenario_params()
    true_utils = {s: true_utility(p["mu"], p["sigma"]) for s, p in params.items()}
    true_means = {s: p["mu"] for s, p in params.items()}
    true_p_exceed = {
        s: true_metrics(p["mu"], p["sigma"])[1] for s, p in params.items()
    }
    best_by_mean = max(true_means, key=true_means.get)
    best_by_p_exceed = max(true_p_exceed, key=true_p_exceed.get)
    reranking_exists = best_by_mean != best_by_p_exceed

    det_wins = 0
    prob_wins = 0
    det_utils = []
    prob_utils = []

    for _ in range(n_trials):
        sample = {
            s: rng.normal(p["mu"], p["sigma"], size=n_per_trial)
            for s, p in params.items()
        }
        d = select_deterministic(sample)
        p_ = select_probabilistic(sample)
        det_utils.append(true_utils[d])
        prob_utils.append(true_utils[p_])
        det_wins += int(d == best_by_p_exceed)
        prob_wins += int(p_ == best_by_p_exceed)

    return {
        "n_trials": n_trials,
        "n_per_trial": n_per_trial,
        "true_means": true_means,
        "true_p_exceed_wacc": true_p_exceed,
        "true_risk_adjusted_utilities": true_utils,
        "best_by_mean": best_by_mean,
        "best_by_p_exceed_wacc": best_by_p_exceed,
        "reranking_exists": reranking_exists,
        "deterministic_rule_picks_p_exceed_winner_rate": det_wins / n_trials,
        "probabilistic_rule_picks_p_exceed_winner_rate": prob_wins / n_trials,
        "deterministic_rule_mean_utility": float(np.mean(det_utils)),
        "probabilistic_rule_mean_utility": float(np.mean(prob_utils)),
        "utility_gain_probabilistic_vs_deterministic": float(
            np.mean(prob_utils) - np.mean(det_utils)
        ),
    }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    results = run_experiment()
    with open(OUTPUT_DIR / "decision_experiment.json", "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 72)
    print("SYNTHETIC THRESHOLD-CRITERION RECOVERY EXPERIMENT")
    print("=" * 72)
    print(f"Trials: {results['n_trials']} | samples per trial: {results['n_per_trial']}")
    print(f"Risk-aversion lambda (shortfall penalty): {LAMBDA}")
    print("\nTrue mean ROI / true P(ROI>WACC) per scenario:")
    for s in results["true_means"]:
        print(f"  {s}: mean={results['true_means'][s]*100:.1f}%  P(>WACC)={results['true_p_exceed_wacc'][s]*100:.1f}%")
    print(f"\nBest by mean ROI:        {results['best_by_mean']}")
    print(f"Best by P(ROI>WACC):     {results['best_by_p_exceed_wacc']}")
    print(f"Reranking exists in DGP: {results['reranking_exists']}")
    print("\nCriterion-recovery rate (picking the true P(ROI>WACC) winner):")
    print(f"  Deterministic mean-ROI rule:  {results['deterministic_rule_picks_p_exceed_winner_rate']*100:.1f}%")
    print(f"  Probabilistic P(ROI>WACC) rule: {results['probabilistic_rule_picks_p_exceed_winner_rate']*100:.1f}%")
    print(f"\nRisk-adjusted utility achieved:")
    print(f"  Deterministic rule:  {results['deterministic_rule_mean_utility']*100:.2f}%")
    print(f"  Probabilistic rule:  {results['probabilistic_rule_mean_utility']*100:.2f}%")
    print(f"  Utility gain (probabilistic - determin.): {results['utility_gain_probabilistic_vs_deterministic']*100:.2f} pts")
    print("\nNOTE: synthetic DGP, not an empirical backtest. This is a criterion-recovery")
    print("test under the probabilistic rule's own stated objective (threshold")
    print("exceedance), not a claim of universal decision superiority.")


if __name__ == "__main__":
    main()
