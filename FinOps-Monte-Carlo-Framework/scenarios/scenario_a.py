"""
Scenario A: Pipeline Capacity Expansion
Investment: $200,000 (project capex) over a 3-year horizon.

Returns come from a fixed capacity-cost component (bulk pricing, reserved
capacity, overflow surcharge avoidance) plus a demand-linked component that
reflects variable compute-cost exposure during peak load. The demand-linked
component carries the demand-compute-cost correlation (0.62), giving Scenario A
the widest ROI variance of the three scenarios.
"""
import numpy as np
from scenarios.base import transform_uniform_to_variables, compute_base_cloud_spend


class ScenarioA:
    def __init__(self, params):
        self.params = params
        self.investment = params["scenarios"]["capacity_expansion"]["investment_usd"]
        self.horizon = params["scenarios"]["capacity_expansion"]["horizon_years"]
        self.wacc = params["simulation"]["discount_rate_wacc"]

    def transform_uniform_to_variables(self, u):
        return transform_uniform_to_variables(u, self.params)

    def calculate_roi(self, samples):
        benefits = self.params["scenarios"]["capacity_expansion"]["benefits"]
        fixed = benefits["fixed_component_usd"]
        rate = benefits["variable_rate_of_cloud_spend"]

        base_cloud_spend = compute_base_cloud_spend(samples)
        variable_benefit = rate * base_cloud_spend
        annual_benefit = fixed + variable_benefit

        # NPV of benefits over the horizon at the WACC discount rate
        npv_factor = sum(1 / (1 + self.wacc) ** t for t in range(1, self.horizon + 1))
        npv_benefit = annual_benefit * npv_factor

        roi = (npv_benefit - self.investment) / self.investment
        return roi
