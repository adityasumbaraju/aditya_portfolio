"""
Scenario B: ETL Reconciliation Automation
Investment: $150,000 (project capex) over a 3-year horizon.

Returns are predominantly fixed labor savings (FTE reduction) plus a small
demand-linked dispute-recovery term. Because the cost structure is largely
volume-invariant, Scenario B exhibits the narrowest ROI distribution, which
is the structural reason it overtakes Scenario A on probability of clearing
the 8% ROI threshold despite a lower mean ROI.
"""
import numpy as np
from scenarios.base import transform_uniform_to_variables, compute_base_cloud_spend


class ScenarioB:
    def __init__(self, params):
        self.params = params
        self.investment = params["scenarios"]["automation"]["investment_usd"]
        self.horizon = params["scenarios"]["automation"]["horizon_years"]
        self.wacc = params["simulation"]["discount_rate_wacc"]

    def transform_uniform_to_variables(self, u):
        return transform_uniform_to_variables(u, self.params)

    def calculate_roi(self, samples):
        benefits = self.params["scenarios"]["automation"]["benefits"]
        fixed = benefits["fixed_component_usd"]
        rate = benefits["variable_rate_of_cloud_spend"]

        base_cloud_spend = compute_base_cloud_spend(samples)
        variable_benefit = rate * base_cloud_spend
        annual_benefit = fixed + variable_benefit

        npv_factor = sum(1 / (1 + self.wacc) ** t for t in range(1, self.horizon + 1))
        npv_benefit = annual_benefit * npv_factor

        roi = (npv_benefit - self.investment) / self.investment
        return roi
