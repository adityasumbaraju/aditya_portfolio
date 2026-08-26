"""
Scenario B: Data Reconciliation Automation Investment
Investment: $150,000 over 12 months
Horizon: 3 years

DESCRIPTION:
Automates manual ETL reconciliation steps (data quality checks currently 
performed by pipeline engineers ad hoc). Returns from:
1. Labor cost reduction (fixed FTE savings, NOT demand-scaled)
2. Error recovery from chargeback dispute resolution
3. SLA/throughput improvements from faster processing
"""

import numpy as np
from scipy.stats import lognorm, beta, norm


class ScenarioB:
    def __init__(self, params):
        self.params = params
        self.investment = 150000  # USD
        self.horizon = 3  # years

    def transform_uniform_to_variables(self, u):
        """
        Transform uniform copula samples to scenario variables via PPF.
        All variables use inverse CDF to preserve copula dependence structure.
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
        resource_util = beta.ppf(u[:, 2], a=p['alpha'], b=p['beta']) * 100

        p = self.params['variables']['pipeline_throughput_recs_per_sec']
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
        Calculate ROI for reconciliation automation scenario.
        """
        annual_demand = samples['demand'] * 365

        automation = self.params['scenarios']['automation']
        benefits = automation['benefits']

        # Prefer configuration values rather than hard-coded values
        investment = automation['investment_usd']
        horizon = automation['horizon_years']

        # Labor savings
        fte_reduction_pct = benefits['fte_reduction_pct']
        fte_cost = benefits['fte_cost_usd']
        labor_savings_annual = fte_reduction_pct * fte_cost

        # Error recovery from disputed transactions
        dispute_transaction_rate = benefits['dispute_transaction_rate']
        dispute_recovery_rate = benefits['dispute_recovery_rate']

        error_recovery_annual = (
                annual_demand
                * samples['unit_cost']
                * dispute_transaction_rate
                * dispute_recovery_rate
        )

        # Throughput / SLA value
        baseline_sla_value_per_record = benefits['sla_value_per_record_usd']
        throughput_improvement_pct = benefits['throughput_improvement_pct']

        throughput_value_annual = (
                samples['throughput']
                * 86400
                * 365
                * baseline_sla_value_per_record
                * throughput_improvement_pct
        )

        total_benefit_annual = (
                labor_savings_annual
                + error_recovery_annual
                + throughput_value_annual
        )

        total_benefit_npv = total_benefit_annual * horizon
        roi = (total_benefit_npv - investment) / investment

        return roi
