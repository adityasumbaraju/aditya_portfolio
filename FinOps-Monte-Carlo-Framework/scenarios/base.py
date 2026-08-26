"""
Base scenario utilities shared across all investment scenarios.

The corrected ROI model uses economically coherent units:
  - demand_volume: records/day (volume count, not a dollar value). For a large
    enterprise pipeline this is on the order of 10 million records/day.
  - unit_cost_usd: USD per record ($0.018 = $18 per 1,000 records)
  - compute_cost_usd_per_unit: USD per record ($0.00042 = $0.42 per 1,000 records)
  - base_cloud_spend = annual_demand * compute_cost  (~$1.5M/year at 10M records/day)

base_cloud_spend is derived directly from demand and per-record compute cost with
no artificial scaling factor, so unit semantics stay internally consistent.

Each scenario's annual benefit is split into:
  (a) a fixed component (volume-invariant savings, e.g., labor, reserved-capacity pricing)
  (b) a demand-linked component (a small fraction of cloud spend, capturing
      demand-cost interaction variance from the copula correlation structure)

ROI is NPV-based with an 8% WACC discount rate applied over a 3-year horizon.
"""
import numpy as np
from scipy.stats import lognorm, beta, norm

VARIABLE_ORDER = [
    "demand_volume",
    "unit_cost_usd",
    "resource_utilization_pct",
    "pipeline_throughput_recs_per_sec",
    "compute_cost_usd_per_unit",
]


def lognormal_params(mean, std_dev):
    """Return (sigma, scale) for a lognormal with the given mean and std_dev."""
    cv = std_dev / mean
    sigma = np.sqrt(np.log(1 + cv ** 2))
    scale = np.exp(np.log(mean) - 0.5 * sigma ** 2)
    return sigma, scale


def transform_uniform_to_variables(u, params):
    """
    Transform uniform copula samples to scenario variables via inverse CDF (PPF).

    Preserves the copula dependence structure across all five variables.
    """
    u = np.clip(u, 1e-12, 1 - 1e-12)
    vars_config = params["variables"]

    p = vars_config["demand_volume"]
    sigma, scale = lognormal_params(
        p["mean_units_per_day"], p["mean_units_per_day"] * p["coefficient_of_variation"]
    )
    demand = lognorm.ppf(u[:, 0], s=sigma, scale=scale)

    p = vars_config["unit_cost_usd"]
    sigma, scale = lognormal_params(p["mean"], p["std_dev"])
    unit_cost = lognorm.ppf(u[:, 1], s=sigma, scale=scale)

    p = vars_config["resource_utilization_pct"]
    resource_util = beta.ppf(u[:, 2], a=p["alpha"], b=p["beta"]) * 100

    p = vars_config["pipeline_throughput_recs_per_sec"]
    throughput = norm.ppf(u[:, 3], loc=p["mean"], scale=p["std_dev"])

    p = vars_config["compute_cost_usd_per_unit"]
    sigma, scale = lognormal_params(p["mean"], p["std_dev"])
    compute_cost = lognorm.ppf(u[:, 4], s=sigma, scale=scale)

    return {
        "demand": demand,
        "unit_cost": unit_cost,
        "resource_util": resource_util,
        "throughput": throughput,
        "compute_cost": compute_cost,
    }


def compute_base_cloud_spend(samples):
    """
    Annual cloud compute spend (USD/year), derived directly from demand and
    per-record compute cost. No artificial scaling factor; units are internally
    consistent. This is the economically coherent base against which demand-linked
    benefit components are scaled (~$1.5M/year at 10M records/day).
    """
    annual_demand = samples["demand"] * 365
    return annual_demand * samples["compute_cost"]
