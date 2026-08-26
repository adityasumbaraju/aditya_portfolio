"""
Scenario C: Multi-Cloud Governance Tooling Deployment
Investment: $300,000 over 12 months
Horizon: 3 years

DESCRIPTION:
Deploys centralized anomaly detection and contract enforcement at the 
ingestion layer (GCP Dataplex, AWS Config). Returns from:
1. Risk mitigation: Avoids compliance remediation and regulatory penalties
2. Data quality improvement: Reduces chargeback disputes
3. Compute efficiency: Better resource allocation decisions
"""

import numpy as np
from scipy.stats import lognorm, beta, norm


class ScenarioC:
    def __init__(self, params):
        self.params = params
        self.investment = 300000  # USD
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
        Calculate ROI for governance tooling scenario.
        """
        annual_demand = samples['demand'] * 365

        governance = self.params['scenarios']['governance']
        benefits = governance['benefits']

        # Read investment assumptions from config
        investment = governance['investment_usd']
        horizon = governance['horizon_years']

        # Risk mitigation
        base_risk_exposure = benefits['base_risk_exposure_usd']
        risk_reduction_pct = benefits['risk_reduction_pct']
        risk_mitigation_annual = base_risk_exposure * risk_reduction_pct

        # Data-quality benefit
        # Scenario C config does not currently define dispute_transaction_rate,
        # so use the 2% baseline explicitly or add it to the config.
        dispute_transaction_rate = 0.02
        quality_improvement_rate = benefits['quality_improvement_rate']

        quality_benefit_annual = (
                annual_demand
                * dispute_transaction_rate
                * samples['unit_cost']
                * quality_improvement_rate
        )

        # Compute efficiency
        efficiency_gain_pct = benefits['efficiency_gain_pct']

        efficiency_gain_annual = (
                samples['compute_cost']
                * annual_demand
                * efficiency_gain_pct
        )

        total_benefit_annual = (
                risk_mitigation_annual
                + quality_benefit_annual
                + efficiency_gain_annual
        )

        total_benefit_npv = total_benefit_annual * horizon
        roi = (total_benefit_npv - investment) / investment

        return roi
