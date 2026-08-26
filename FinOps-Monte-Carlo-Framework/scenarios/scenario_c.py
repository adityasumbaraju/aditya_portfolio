"""
Scenario C: Multi-Cloud Governance Tooling
Investment: $300,000 (project capex) over a 3-year horizon.

Returns combine a fixed risk-avoidance component (expected compliance and
penalty-exposure reduction) with a demand-linked compute-efficiency term.
The mixed fixed/demand-sensitive structure produces medium ROI variance.
"""
import numpy as np
from scenarios.base import transform_uniform_to_variables, compute_base_cloud_spend


class ScenarioC:
    def __init__(self, params):
        self.params = params
        self.investment = params["scenarios"]["governance"]["investment_usd"]
        self.horizon = params["scenarios"]["governance"]["horizon_years"]
        self.wacc = params["simulation"]["discount_rate_wacc"]

    def transform_uniform_to_variables(self, u):
        return transform_uniform_to_variables(u, self.params)

    def calculate_roi(self, samples):
        benefits = self.params["scenarios"]["governance"]["benefits"]
        fixed = benefits["fixed_component_usd"]
        rate = benefits["variable_rate_of_cloud_spend"]

        base_cloud_spend = compute_base_cloud_spend(samples)
        variable_benefit = rate * base_cloud_spend
        annual_benefit = fixed + variable_benefit

        npv_factor = sum(1 / (1 + self.wacc) ** t for t in range(1, self.horizon + 1))
        npv_benefit = annual_benefit * npv_factor

        roi = (npv_benefit - self.investment) / self.investment
        return roi
