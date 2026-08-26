"""
Main simulation runner - orchestrates Monte Carlo analysis across all scenarios
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import multivariate_normal

# Import scenario classes
from scenarios.scenario_a import ScenarioA
from scenarios.scenario_b import ScenarioB
from scenarios.scenario_c import ScenarioC
import json
with open('config/params_config.json') as f:
 params = json.load(f)


class MonteCarloFramework:
    def __init__(self, config_path='config/params_config.json'):
        """Initialize framework with configuration."""
        with open(config_path, 'r') as f:
            self.params = json.load(f)

        self.n_iterations = self.params['simulation']['n_iterations']
        np.random.seed(self.params['simulation']['random_seed'])

    def generate_copula_samples(self):
        """
        Generate Gaussian copula samples preserving observed correlation structure.
        Returns uniform samples [0,1] that preserve multi-variable dependence.
        """
        # Get correlation matrix from config
        corr_matrix = np.array(self.params['correlation_matrix']['matrix'])

        # Generate standard normal samples
        z_samples = np.random.multivariate_normal(
            mean=np.zeros(len(corr_matrix)),
            cov=corr_matrix,
            size=self.n_iterations
        )

        # Transform to uniform via standard normal CDF
        from scipy.stats import norm
        u_samples = norm.cdf(z_samples)

        return u_samples

    def run_scenario(self, scenario_class, scenario_name):
        """
        Run a single scenario and compute ROI distribution.
        """
        print(f"\nRunning {scenario_name}...")

        # Generate copula samples
        u_samples = self.generate_copula_samples()

        # Initialize scenario
        scenario = scenario_class(self.params)

        # Transform to variables and calculate ROI
        samples = scenario.transform_uniform_to_variables(u_samples)
        roi_distribution = scenario.calculate_roi(samples)

        # Compute statistics
        stats = {
            'scenario': scenario_name,
            'mean_roi': np.mean(roi_distribution),
            'std_roi': np.std(roi_distribution),
            'median_roi': np.median(roi_distribution),
            'min_roi': np.min(roi_distribution),
            'max_roi': np.max(roi_distribution),
            'p5_roi': np.percentile(roi_distribution, 5),
            'p25_roi': np.percentile(roi_distribution, 25),
            'p75_roi': np.percentile(roi_distribution, 75),
            'p95_roi': np.percentile(roi_distribution, 95),
            'threshold_exceedance': np.sum(roi_distribution > 0.20) / self.n_iterations,
            'negative_roi_probability': np.sum(roi_distribution < 0) / self.n_iterations
        }

        return roi_distribution, stats

    def run_all_scenarios(self):
        """Run all three scenarios and generate comparison."""
        results = {}
        distributions = {}

        # Scenario A: Capacity Expansion
        roi_a, stats_a = self.run_scenario(
            ScenarioA, 
            'Scenario A: Capacity Expansion'
        )
        results['scenario_a'] = stats_a
        distributions['scenario_a'] = roi_a

        # Scenario B: Automation
        roi_b, stats_b = self.run_scenario(
            ScenarioB,
            'Scenario B: Reconciliation Automation'
        )
        results['scenario_b'] = stats_b
        distributions['scenario_b'] = roi_b

        # Scenario C: Governance
        roi_c, stats_c = self.run_scenario(
            ScenarioC,
            'Scenario C: Multi-Cloud Governance'
        )
        results['scenario_c'] = stats_c
        distributions['scenario_c'] = roi_c

        return results, distributions

    def export_results(self, results, distributions, output_dir='outputs'):
        """Export results to CSV and JSON."""
        Path(output_dir).mkdir(exist_ok=True)

        # Export statistics table
        stats_df = pd.DataFrame(results).T
        stats_df.to_csv(f'{output_dir}/roi_statistics.csv')
        print(f"\n✓ Exported ROI statistics to {output_dir}/roi_statistics.csv")

        # Export distributions
        dist_df = pd.DataFrame(distributions)
        dist_df.to_csv(f'{output_dir}/roi_distributions.csv', index=False)
        print(f"✓ Exported ROI distributions to {output_dir}/roi_distributions.csv")

        # Export JSON summary
        with open(f'{output_dir}/simulation_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=float)
        print(f"✓ Exported JSON summary to {output_dir}/simulation_results.json")


def main():
    # Initialize framework
    framework = MonteCarloFramework('config/params_config.json')

    # Run all scenarios
    results, distributions = framework.run_all_scenarios()

    # Print summary table
    print("\n" + "="*80)
    print("MONTE CARLO SIMULATION RESULTS (10,000 iterations)")
    print("="*80)

    summary_df = pd.DataFrame(results).T[
        ['mean_roi', 'std_roi', 'p5_roi', 'p95_roi', 'threshold_exceedance', 'negative_roi_probability']
    ]
    print(summary_df.to_string())

    # Export results
    framework.export_results(results, distributions)

    print("\n✓ Simulation complete!")


if __name__ == '__main__':
    main()
