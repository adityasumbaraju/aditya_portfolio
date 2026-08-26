"""
Sensitivity Analysis - Test ranking stability under correlation and data-quality uncertainty
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import multivariate_normal, norm

from scenarios.scenario_a import ScenarioA
from scenarios.scenario_b import ScenarioB
from scenarios.scenario_c import ScenarioC


class SensitivityAnalysis:
    def __init__(self, config_path='config/params_config.json'):
        """Initialize sensitivity framework."""
        with open(config_path, 'r') as f:
            self.params = json.load(f)

        self.n_iterations = self.params['simulation']['n_iterations']

    def run_with_correlation_structure(self, correlation_matrix):
        """Run all scenarios with specified correlation matrix."""
        # Generate copula samples with given correlation
        z_samples = np.random.multivariate_normal(
            mean=np.zeros(len(correlation_matrix)),
            cov=correlation_matrix,
            size=self.n_iterations
        )
        u_samples = norm.cdf(z_samples)

        results = {}

        # Run each scenario
        for scenario_class, name in [
            (ScenarioA, 'scenario_a'),
            (ScenarioB, 'scenario_b'),
            (ScenarioC, 'scenario_c')
        ]:
            scenario = scenario_class(self.params)
            samples = scenario.transform_uniform_to_variables(u_samples)
            roi = scenario.calculate_roi(samples)

            results[name] = {
                'mean_roi': np.mean(roi),
                'std_roi': np.std(roi),
                'threshold_exceedance': np.sum(roi > 0.20) / self.n_iterations
            }

        return results

    def test_independent_sampling(self):
        """Test ranking stability under INDEPENDENT sampling (no correlation)."""
        print("\nTesting INDEPENDENT sampling (correlation = 0)...")

        # Identity matrix = independent variables
        independent_corr = np.eye(5)
        results = self.run_with_correlation_structure(independent_corr)

        return results

    def test_observed_correlation(self):
        """Test with OBSERVED correlation structure."""
        print("\nTesting OBSERVED correlation structure...")

        observed_corr = np.array(self.params['correlation_matrix']['matrix'])
        results = self.run_with_correlation_structure(observed_corr)

        return results

    def test_data_quality_degradation(self):
        """Test ranking stability under data-quality degradation."""
        print("\nTesting DATA-QUALITY degradation scenarios...")

        degradation_levels = [0.0, 0.1, 0.25]
        results_by_degradation = {}

        for deg_level in degradation_levels:
            # Increase correlation uncertainty: reduce correlation strength
            observed_corr = np.array(self.params['correlation_matrix']['matrix'])

            # Apply degradation by moving correlations toward 0
            degraded_corr = observed_corr.copy()
            degraded_corr = np.eye(5) + (degraded_corr - np.eye(5)) * (1 - deg_level)

            results = self.run_with_correlation_structure(degraded_corr)
            results_by_degradation[f'degradation_{deg_level:.0%}'] = results

        return results_by_degradation

    def export_sensitivity_results(self, all_results, output_dir='outputs'):
        """Export sensitivity analysis results."""
        Path(output_dir).mkdir(exist_ok=True)

        # Compile all results into comparison table
        comparison_data = []

        for test_name, test_results in all_results.items():
            for scenario_name, metrics in test_results.items():
                row = {
                    'test': test_name,
                    'scenario': scenario_name,
                    **metrics
                }
                comparison_data.append(row)

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv(f'{output_dir}/sensitivity_analysis.csv', index=False)
        print(f"\n✓ Exported sensitivity results to {output_dir}/sensitivity_analysis.csv")

        return comparison_df


def main():
    sensitivity = SensitivityAnalysis('config/params_config.json')

    # Run all sensitivity tests
    all_results = {
        'independent_sampling': sensitivity.test_independent_sampling(),
        'observed_correlation': sensitivity.test_observed_correlation(),
        **sensitivity.test_data_quality_degradation()
    }

    # Export and display results
    comparison_df = sensitivity.export_sensitivity_results(all_results)

    print("\n" + "="*80)
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("="*80)
    print(comparison_df.to_string(index=False))

    print("\n✓ Sensitivity analysis complete!")


if __name__ == '__main__':
    main()
