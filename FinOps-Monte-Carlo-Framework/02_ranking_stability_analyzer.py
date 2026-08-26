
import json
import numpy as np
import pandas as pd
from collections import defaultdict

class RankingStabilityAnalyzer:
    """
    Compares scenario rankings across three correlation structures:
    - Observed Gaussian copula (baseline)
    - Independent sampling (breaks correlations)
    - T-copula with df=5 (adds tail dependence)

    Outputs:
    - Ranking consistency table
    - ROI variance deltas
    - Threshold exceedance probability changes
    - Summary statistics for publication
    """

    def __init__(self, results_by_correlation, threshold_roi=0.20):
        """
        Args:
            results_by_correlation: dict with keys ['observed', 'independent', 't_copula']
                Each value contains:
                  {'scenario_a': roi_dist_array,
                   'scenario_b': roi_dist_array,
                   'scenario_c': roi_dist_array}
            threshold_roi: Exceedance threshold (default 20%)
        """
        self.results = results_by_correlation
        self.threshold = threshold_roi
        self.analysis = {}

    def run_analysis(self):
        """Execute full ranking stability analysis"""
        print("\n" + "="*90)
        print("RANKING STABILITY & VARIANCE ROBUSTNESS ANALYSIS")
        print("="*90 + "\n")

        # Test 1: Ranking consistency
        ranking_table = self._compute_ranking_consistency()
        print("\nTEST 1: RANKING CONSISTENCY ACROSS CORRELATION STRUCTURES")
        print("-" * 90)
        print(ranking_table)

        # Test 2: Variance deltas
        variance_table = self._compute_variance_deltas()
        print("\n\nTEST 2: ROI VARIANCE COMPARISON (% change vs. Observed Baseline)")
        print("-" * 90)
        print(variance_table)

        # Test 3: Threshold exceedance probability
        threshold_table = self._compute_threshold_exceedance()
        print("\n\nTEST 3: THRESHOLD EXCEEDANCE PROBABILITY (ROI > 20%)")
        print("-" * 90)
        print(threshold_table)

        # Test 4: Summary statistics
        summary = self._compute_summary_stats()
        print("\n\nTEST 4: SUMMARY STATISTICS & PUBLICATION READINESS")
        print("-" * 90)
        print(summary)

        self.analysis = {
            'ranking_table': ranking_table,
            'variance_table': variance_table,
            'threshold_table': threshold_table,
            'summary': summary
        }

        return self.analysis

    def _compute_ranking_consistency(self):
        """Compute scenario rankings for each correlation structure"""
        rankings = {}

        for corr_name in ['observed', 'independent', 't_copula']:
            roi_data = self.results[corr_name]

            means = {
                'A': np.mean(roi_data['scenario_a']),
                'B': np.mean(roi_data['scenario_b']),
                'C': np.mean(roi_data['scenario_c'])
            }

            # Sort by mean ROI descending
            sorted_scenarios = sorted(means.items(), key=lambda x: x[1], reverse=True)
            rankings[corr_name] = [s[0] for s in sorted_scenarios]

        # Build table
        rows = []
        for corr_name in ['observed', 'independent', 't_copula']:
            ranking = rankings[corr_name]
            ranking_str = ' > '.join(ranking)

            # Check stability
            stable = ranking == rankings['observed']
            stability_marker = '[STABLE]' if stable else '[CHANGED]'

            rows.append({
                'Correlation Structure': corr_name.replace('_', ' ').title(),
                'Ranking': ranking_str,
                'Stability vs. Baseline': stability_marker
            })

        df = pd.DataFrame(rows)
        return df.to_string(index=False)

    def _compute_variance_deltas(self):
        """Compute variance % change for each scenario across structures"""
        rows = []

        # Get baseline (observed) standard deviations
        std_obs = {
            'A': np.std(self.results['observed']['scenario_a']),
            'B': np.std(self.results['observed']['scenario_b']),
            'C': np.std(self.results['observed']['scenario_c'])
        }

        for scenario_name, scenario_key in [('A', 'scenario_a'), 
                                            ('B', 'scenario_b'), 
                                            ('C', 'scenario_c')]:
            std_indep = np.std(self.results['independent'][scenario_key])
            std_t = np.std(self.results['t_copula'][scenario_key])
            std_baseline = std_obs[scenario_name]

            # Variance delta: (std_test - std_baseline) / std_baseline * 100
            delta_indep = ((std_indep - std_baseline) / std_baseline) * 100
            delta_t = ((std_t - std_baseline) / std_baseline) * 100

            # Robustness check: < 2% for t-copula is good
            robust_t = '[ROBUST <2%]' if abs(delta_t) < 2.0 else '[DRIFT >2%]'

            rows.append({
                'Scenario': scenario_name,
                'Observed Std': f'{std_baseline:.2f}%',
                'Independent Std': f'{std_indep:.2f}% (D {delta_indep:+.1f}%)',
                'T-Copula Std': f'{std_t:.2f}% (D {delta_t:+.1f}%)',
                'T-Copula Robustness': robust_t
            })

        df = pd.DataFrame(rows)
        return df.to_string(index=False)

    def _compute_threshold_exceedance(self):
        """Compute P[ROI > threshold] for each scenario & structure"""
        rows = []

        for scenario_name, scenario_key in [('A', 'scenario_a'), 
                                            ('B', 'scenario_b'), 
                                            ('C', 'scenario_c')]:
            probs = {}

            for corr_name in ['observed', 'independent', 't_copula']:
                roi_dist = self.results[corr_name][scenario_key]
                prob = np.mean(roi_dist > self.threshold) * 100
                probs[corr_name] = prob

            # Compute deltas vs. observed
            prob_indep_delta = probs['independent'] - probs['observed']
            prob_t_delta = probs['t_copula'] - probs['observed']

            rows.append({
                'Scenario': scenario_name,
                'Observed P(ROI>20%)': f'{probs["observed"]:.1f}%',
                'Independent': f'{probs["independent"]:.1f}% (D {prob_indep_delta:+.1f}pp)',
                'T-Copula': f'{probs["t_copula"]:.1f}% (D {prob_t_delta:+.1f}pp)',
                'Stability': '[OK]' if abs(prob_t_delta) < 2.0 else '[DRIFT]'
            })

        df = pd.DataFrame(rows)
        return df.to_string(index=False)

    def _compute_summary_stats(self):
        """Publish-ready summary: ranking stability, variance robustness, exceedance robustness"""
        # Check 1: All rankings identical?
        rankings = {}
        for corr_name in ['observed', 'independent', 't_copula']:
            roi_data = self.results[corr_name]
            means = {
                'A': np.mean(roi_data['scenario_a']),
                'B': np.mean(roi_data['scenario_b']),
                'C': np.mean(roi_data['scenario_c'])
            }
            sorted_scenarios = sorted(means.items(), key=lambda x: x[1], reverse=True)
            rankings[corr_name] = [s[0] for s in sorted_scenarios]

        ranking_stable = (rankings['observed'] == rankings['independent'] and 
                         rankings['observed'] == rankings['t_copula'])

        # Check 2: T-copula variance delta < 2%?
        max_variance_delta = 0
        for scenario_key in ['scenario_a', 'scenario_b', 'scenario_c']:
            std_obs = np.std(self.results['observed'][scenario_key])
            std_t = np.std(self.results['t_copula'][scenario_key])
            delta = abs((std_t - std_obs) / std_obs) * 100
            max_variance_delta = max(max_variance_delta, delta)

        variance_robust = max_variance_delta < 2.0

        # Check 3: Independent variance amplification ~40% for Scenario A?
        std_obs_a = np.std(self.results['observed']['scenario_a'])
        std_indep_a = np.std(self.results['independent']['scenario_a'])
        indep_variance_change = ((std_indep_a - std_obs_a) / std_obs_a) * 100

        # Check 4: Negative ROI probability zero for all scenarios?
        neg_roi_issues = []
        for scenario_key in ['scenario_a', 'scenario_b', 'scenario_c']:
            for corr_name in ['observed', 'independent', 't_copula']:
                roi_dist = self.results[corr_name][scenario_key]
                neg_count = np.sum(roi_dist < 0)
                if neg_count > 0:
                    scenario_name = scenario_key.replace('scenario_', '').upper()
                    neg_roi_issues.append(f"  WARNING: {scenario_name} ({corr_name}): {neg_count} negative ROI outcomes")

        summary_text = f"""
Ranking Stability:
  Consistent across all structures: {ranking_stable}
  Observed ranking: {' > '.join(rankings['observed'])}
  Independent ranking: {' > '.join(rankings['independent'])}
  T-copula ranking: {' > '.join(rankings['t_copula'])}

Variance Robustness (vs. Observed Baseline):
  T-copula max delta < 2%: {variance_robust} (max observed: {max_variance_delta:.2f}%)
  Independent variance change for Scenario A: {indep_variance_change:+.1f}%
    (Expected ~-40% per reference; framework captures correlation sensitivity)

Negative ROI Outcomes:
  {"NONE detected across all scenarios/structures" if not neg_roi_issues else chr(10).join(neg_roi_issues)}

Publication Readiness:
  RQ1 (Ranking stability): {"PASS" if ranking_stable else "FAIL"}
  RQ2 (Variance robustness): {"PASS" if variance_robust else "FAIL"}
  Copula choice robustness: {"PASS (< 2% variation)" if variance_robust else "FAIL (> 2% variation)"}

  Overall: {"GREEN - PUBLICATION READY" if (ranking_stable and variance_robust) else "YELLOW - NEEDS REVIEW"}
"""

        return summary_text.strip()

    def export_results(self, filename='sensitivity_analysis_results.json'):
        """Export results to JSON for archival & reproducibility"""
        export_dict = {
            'ranking_analysis': self.analysis.get('ranking_table', ''),
            'variance_analysis': self.analysis.get('variance_table', ''),
            'threshold_analysis': self.analysis.get('threshold_table', ''),
            'summary': self.analysis.get('summary', ''),
            'config': {
                'n_iterations': len(self.results['observed']['scenario_a']),
                'threshold_roi': self.threshold,
                'correlation_structures': list(self.results.keys())
            }
        }

        with open(filename, 'w') as f:
            json.dump(export_dict, f, indent=2)

        print(f"\n[EXPORT] Results saved to {filename}")
        return filename


# USAGE EXAMPLE:
# Once you have results_by_correlation from running all scenarios:
#
# analyzer = RankingStabilityAnalyzer(results_by_correlation, threshold_roi=0.20)
# analysis = analyzer.run_analysis()
# analyzer.export_results('sensitivity_results.json')
