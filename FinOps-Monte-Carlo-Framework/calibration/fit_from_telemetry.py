"""
Empirical Calibration Module
============================

Converts observed pipeline telemetry (CSV matching
`calibration/telemetry_schema.md`) into empirically fitted parameter
distributions and a calibrated `params_config_empirical_template.json`.

Design rules (honesty-preserving):
  * If no telemetry file is supplied, the script exits with a clear message
    listing the required columns. It does NOT fabricate "empirical" parameters.
  * If a telemetry file is supplied, marginals are fitted from observed telemetry
    (lognormal/normal via sample estimates; beta via method-of-moments) and
    correlations are estimated by rank (Spearman) to match the Gaussian-copula
    construction used in the simulation engine.
  * Goodness-of-fit (Kolmogorov-Smirnov) is reported per variable so the
    Gaussian-vs-Student-t copula choice can be made on evidence.

Usage:
    python calibration/fit_from_telemetry.py --csv telemetry.csv
    python calibration/fit_from_telemetry.py            # prints required schema
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "calibration" / "telemetry_schema.md"

# Columns required to fit the five simulation input distributions.
REQUIRED_COLUMNS = [
    "date",
    "demand_records",
    "unit_cost",
    "utilization",
    "throughput",
    "compute_cost_per_record",
]

LOGNORMAL_VARS = ["demand_records", "unit_cost", "compute_cost_per_record"]


def _print_schema() -> None:
    print(
        "No telemetry CSV supplied. To calibrate the framework empirically,\n"
        "provide a CSV matching the schema in:\n"
        f"  {SCHEMA_PATH}\n\n"
        "Required columns for distribution fitting:\n  "
        + "\n  ".join(REQUIRED_COLUMNS)
        + "\n\nOptional governance columns and scenario benefit columns are\n"
        "documented in the schema. No synthetic 'empirical' parameters are\n"
        "generated without observed telemetry."
    )


def _fit_lognormal(samples: np.ndarray) -> dict:
    # Fit lognormal via the underlying Normal distribution of log(samples).
    log_s = np.log(samples[samples > 0])
    mu, sigma = float(np.mean(log_s)), float(np.std(log_s, ddof=1))
    return {"mu": mu, "sigma": sigma, "mean": float(np.exp(mu + sigma**2 / 2))}


def _fit_beta(samples: np.ndarray) -> dict:
    # Method-of-moments Beta fit on the (0,1) interval.
    s = np.clip(samples, 1e-6, 1 - 1e-6)
    mean, var = float(np.mean(s)), float(np.var(s, ddof=1))
    common = mean * (1 - mean) / var - 1
    alpha = max(mean * common, 1e-3)
    beta = max((1 - mean) * common, 1e-3)
    return {"alpha": alpha, "beta": beta, "mean": mean}


def _fit_normal(samples: np.ndarray) -> dict:
    return {
        "mean": float(np.mean(samples)),
        "std": float(np.std(samples, ddof=1)),
    }


def fit_marginals(df) -> dict:
    fits: dict[str, dict] = {}
    for col in REQUIRED_COLUMNS[1:]:  # skip "date"
        s = df[col].to_numpy(dtype=float)
        s = s[~np.isnan(s)]
        if col in LOGNORMAL_VARS:
            fits[col] = {"family": "lognormal", **_fit_lognormal(s)}
        elif col == "utilization":
            fits[col] = {"family": "beta", **_fit_beta(s)}
        else:  # throughput
            fits[col] = {"family": "normal", **_fit_normal(s)}
    return fits


def estimate_correlation(df) -> list[list[float]]:
    cols = REQUIRED_COLUMNS[1:]
    # Spearman rank correlation -> suitable input to a Gaussian copula.
    rank_df = df[cols].rank()
    rho = rank_df.corr(method="spearman").to_numpy()
    # Symmetrize / clamp numerical noise.
    rho = (rho + rho.T) / 2.0
    np.fill_diagonal(rho, 1.0)
    return rho.tolist()


def goodness_of_fit(df, fits) -> dict:
    from scipy import stats

    report: dict[str, dict] = {}
    for col, fit in fits.items():
        s = df[col].to_numpy(dtype=float)
        s = s[~np.isnan(s)]
        if fit["family"] == "lognormal":
            log_s = np.log(s[s > 0])
            mu, sigma = fit["mu"], fit["sigma"]
            ks, p = stats.kstest(log_s, lambda x: stats.norm.cdf(x, loc=mu, scale=sigma))
        elif fit["family"] == "beta":
            a, b = fit["alpha"], fit["beta"]
            ks, p = stats.kstest(np.clip(s, 0, 1), lambda x: stats.beta.cdf(x, a, b))
        else:
            mu, sigma = fit["mean"], fit["std"]
            ks, p = stats.kstest(s, lambda x: stats.norm.cdf(x, loc=mu, scale=sigma))
        report[col] = {"ks_statistic": float(ks), "p_value": float(p)}
    return report


def build_template(df, wacc: float = 0.08, horizon_years: int = 3) -> dict:
    fits = fit_marginals(df)
    corr = estimate_correlation(df)
    gof = goodness_of_fit(df, fits)
    ann_factor = sum(1 / (1 + wacc) ** t for t in range(1, horizon_years + 1))
    return {
        "calibration_source": "empirical_telemetry",
        "telemetry_rows": int(len(df)),
        "distributions": fits,
        "correlation_matrix": {"matrix": corr},
        "goodness_of_fit": gof,
        "analysis": {
            "wacc": wacc,
            "horizon_years": horizon_years,
            "annuity_factor": round(ann_factor, 4),
            "threshold_exceedance_roi": wacc,
        },
        "note": (
            "Empirically fitted template. Scenario benefit components still "
            "require finance/operations-derived estimates per the telemetry "
            "schema; this template only calibrates input distributions and "
            "dependence structure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv", type=str, default=None, help="Path to telemetry CSV file."
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(REPO_ROOT / "config" / "params_config_empirical_template.json"),
        help="Output JSON path for the empirical template.",
    )
    args = parser.parse_args()

    if not args.csv:
        _print_schema()
        return 0

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Telemetry file not found: {csv_path}")
        _print_schema()
        return 1

    import pandas as pd

    df = pd.read_csv(csv_path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"Telemetry CSV is missing required columns: {missing}")
        _print_schema()
        return 1

    template = build_template(df)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    print(f"Empirical calibration template written to: {out_path}")
    print(
        f"Fitted {len(template['distributions'])} marginals from "
        f"{template['telemetry_rows']} telemetry rows."
    )
    print("Goodness-of-fit (Kolmogorov-Smirnov):")
    for col, g in template["goodness_of_fit"].items():
        print(f"  {col}: KS={g['ks_statistic']:.4f}, p={g['p_value']:.4f}")
    print("\nNOTE: scenario benefit components must still be supplied from "
          "finance/operations sources (see telemetry_schema.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
