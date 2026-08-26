"""
Scenario A: Pipeline Capacity Expansion
Investment: $200,000 over 12 months
Horizon: 3 years

DESCRIPTION:
Expanding cloud infrastructure (BigQuery slots, Snowflake credits, EC2 instances)
to handle 40% volume growth. Returns come from:
1. Reduced unit processing costs via bulk pricing discounts
2. Elimination of overflow/on-demand surcharges
3. SLA compliance improvements enabling premium tier pricing
"""

import numpy as np
from scipy.stats import lognorm, beta, norm


class ScenarioA:
    def __init__(self, params):
        self.params = params
        self.investment = 200000  # USD
        self.horizon = 3  # years

    def transform_uniform_to_variables(self, u):
        """
        Transform uniform copula samples to scenario variables via PPF.
        Preserves demand-compute-cost correlation (0.62) and 
        demand-utilization correlation (0.55).
        """
        p = self.params['variables']['demand_volume']
        mu = np.log(p['mean_units_per_day']) - 0.5 * np.log(1 + p['coefficient_of_variation']**2)
        sigma = np.sqrt(np.log(1 + p['coefficient_of_variation']**2))
        demand = lognorm.ppf(u[:, 0], s=sigma, scale=np.exp(mu))

        p = self.params['variables']['unit_cost_usd']
        mu_uc = np.log(p['mean']) - 0.5 * np.log(1 + (p['std_dev']/p['mean'])**2)
        sigma_uc = np.sqrt(np.log(1 + (p['std_dev']/p['mean'])**2))
        unit_cost = lognorm.ppf(u[:, 1], s=sigma_uc, scale=np.exp(mu_uc))

        p = self.params['variables']['resource_utilization_pct']
        # Transform via Beta PPF (preserves copula structure)
        resource_util = beta.ppf(u[:, 2], a=p['alpha'], b=p['beta']) * 100

        p = self.params['variables']['pipeline_throughput_recs_per_sec']
        # Transform via Normal PPF
        throughput = norm.ppf(u[:, 3], loc=p['mean'], scale=p['std_dev'])

        p = self.params['variables']['compute_cost_usd_per_unit']
        mu_cc = np.log(p['mean']) - 0.5 * np.log(1 + (p['std_dev']/p['mean'])**2)
        sigma_cc = np.sqrt(np.log(1 + (p['std_dev']/p['mean'])**2))
        compute_cost = lognorm.ppf(u[:, 4], s=sigma_cc, scale=np.exp(mu_cc))

        return {
            'demand': demand,
            'unit_cost': unit_cost,
            'resource_util': resource_util,
            'throughput': throughput,
            'compute_cost': compute_cost
        }

    def calculate_roi(self, samples):
        """
        Calculate ROI for capacity expansion scenario.

        BENEFIT BREAKDOWN (per year):
        1. Unit cost savings: Volume growth triggers bulk pricing discounts
           Formula: (current_unit_cost - discounted_unit_cost) × annual_demand
        2. Overflow cost elimination: No on-demand surcharges
           Formula: annual_demand × surcharge_rate × unit_cost
        3. SLA compliance premium: Higher uptime enables premium pricing
           Formula: annual_demand × premium_uplift × unit_cost
        """
        # Annualize daily demand
        annual_demand = samples['demand'] * 365

        # Unit cost savings from volume-tier discounts
        # At 40% growth, unit costs drop 8% (industry FinOps benchmarks)
        unit_cost_savings_annual = annual_demand * samples['unit_cost'] * 0.08

        # Overflow cost elimination: on-demand premium avoided
        # Baseline: 3% of transactions overflow at current capacity
        overflow_cost_avoided_annual = annual_demand * samples['unit_cost'] * 0.03 * 0.15  # 15% on-demand premium

        # SLA compliance premium: uptime improvement to 99.99%
        # Enables 2% revenue uplift on premium tier
        sla_premium_annual = annual_demand * samples['unit_cost'] * 0.02

        # Total annual benefit
        total_benefit_annual = unit_cost_savings_annual + overflow_cost_avoided_annual + sla_premium_annual

        # NPV: Multiply by 3-year horizon (discount rate implicitly = 0 for base case)
        total_benefit_npv = total_benefit_annual * self.horizon

        # ROI calculation
        roi = (total_benefit_npv - self.investment) / self.investment

        return roi
