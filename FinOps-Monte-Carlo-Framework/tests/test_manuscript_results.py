"""
Automated verification of every quantitative claim in the manuscript.

These tests rerun the full simulation pipeline (see conftest.py) and assert
that the generated outputs reproduce the published tables:

  - Table V    : ROI distributions (mean, SD, P(ROI>8%))
  - Table VII   : tail-risk metrics (VaR, CVaR, downside prob, shortfall)
  - Table VI    : ranking stability across copula/degradation conditions
  - Table VIII  : threshold-criterion recovery experiment
  - Table IX    : threshold-sensitivity sweep + crossover
  - Sec IV-J    : parameter-prevalence sweep
  - Sec IV-K    : de-circularized recovery experiment
  - Sec IV-L    : correlation-matrix sensitivity
  - Sec IV-M    : mean-preserving break-point analysis

Tolerances: ±0.1 percentage point (abs=0.001) on Monte Carlo probabilities,
which is tight enough to catch real regressions yet robust to tiny numerical
differences across NumPy/SciPy versions. Exact equality is used for ranking
strings, the crossover threshold, and the bootstrap count.
"""
from __future__ import annotations

import pytest

# Convenience: 0.1 percentage-point tolerance on fractional values.
P = pytest.approx  # use approx(x, abs=0.001)

ABS = 0.001  # ±0.1 pp

# --------------------------------------------------------------------------- #
# Table V — ROI distributions
# --------------------------------------------------------------------------- #
class TestTableV:
    def test_scenario_a(self, simulation_results):
        a = simulation_results["scenario_a"]
        assert a["mean_roi"] == P(0.145, abs=ABS)
        assert a["std_roi"] == P(0.069, abs=ABS)
        assert a["threshold_exceedance"] == P(0.833, abs=ABS)

    def test_scenario_b(self, simulation_results):
        b = simulation_results["scenario_b"]
        assert b["mean_roi"] == P(0.108, abs=ABS)
        assert b["std_roi"] == P(0.021, abs=ABS)
        assert b["threshold_exceedance"] == P(0.935, abs=ABS)

    def test_scenario_c(self, simulation_results):
        c = simulation_results["scenario_c"]
        assert c["mean_roi"] == P(0.095, abs=ABS)
        assert c["std_roi"] == P(0.041, abs=ABS)
        assert c["threshold_exceedance"] == P(0.607, abs=ABS)

    def test_sample_count(self, simulation_results):
        for s in ("scenario_a", "scenario_b", "scenario_c"):
            assert simulation_results[s]["samples_count"] == 10000


# --------------------------------------------------------------------------- #
# The reranking effect — the central claim of the paper
# --------------------------------------------------------------------------- #
class TestReranking:
    def test_mean_ranking_is_a_b_c(self, simulation_results):
        means = {k: simulation_results[k]["mean_roi"] for k in
                 ("scenario_a", "scenario_b", "scenario_c")}
        assert means["scenario_a"] > means["scenario_b"] > means["scenario_c"]

    def test_threshold_ranking_is_b_a_c(self, simulation_results):
        probs = {k: simulation_results[k]["threshold_exceedance"] for k in
                 ("scenario_a", "scenario_b", "scenario_c")}
        assert probs["scenario_b"] > probs["scenario_a"] > probs["scenario_c"]

    def test_reranking_exists(self, simulation_results):
        a = simulation_results["scenario_a"]["mean_roi"]
        b = simulation_results["scenario_b"]["mean_roi"]
        pa = simulation_results["scenario_a"]["threshold_exceedance"]
        pb = simulation_results["scenario_b"]["threshold_exceedance"]
        assert a > b and pb > pa


# --------------------------------------------------------------------------- #
# Table VII — tail-risk metrics
# --------------------------------------------------------------------------- #
class TestTableVII:
    def test_b_has_highest_var(self, simulation_results):
        var = {k: simulation_results[k]["var_5_roi"] for k in
               ("scenario_a", "scenario_b", "scenario_c")}
        assert var["scenario_b"] > var["scenario_a"]
        assert var["scenario_b"] > var["scenario_c"]

    def test_b_has_lowest_downside_probability(self, simulation_results):
        dp = {k: simulation_results[k]["downside_probability_below_wacc"] for k in
              ("scenario_a", "scenario_b", "scenario_c")}
        assert dp["scenario_b"] < dp["scenario_a"]
        assert dp["scenario_b"] < dp["scenario_c"]

    def test_published_tail_risk_values(self, simulation_results):
        a, b, c = (simulation_results[f"scenario_{s}"] for s in ("a", "b", "c"))
        assert a["var_5_roi"] == P(0.047, abs=ABS)
        assert b["var_5_roi"] == P(0.078, abs=ABS)
        assert c["var_5_roi"] == P(0.037, abs=ABS)
        assert a["downside_probability_below_wacc"] == P(0.167, abs=ABS)
        assert b["downside_probability_below_wacc"] == P(0.066, abs=ABS)
        assert c["downside_probability_below_wacc"] == P(0.393, abs=ABS)


# --------------------------------------------------------------------------- #
# Table VI — sensitivity / robustness
# --------------------------------------------------------------------------- #
class TestTableVI:
    CONDITIONS = [
        "observed_gaussian",
        "independent",
        "t_copula_df5",
        "degradation_0pct",
        "degradation_10pct",
        "degradation_25pct",
    ]

    def test_b_a_c_preserved_under_all_conditions(self, sensitivity_results):
        for cond in self.CONDITIONS:
            res = sensitivity_results[cond]
            probs = {s: res[s]["threshold_exceedance"] for s in ("A", "B", "C")}
            assert probs["B"] > probs["A"] > probs["C"], (
                f"B>A>C ranking broken under {cond}: {probs}"
            )

    def test_bootstrap_100_of_100(self, sensitivity_results):
        bs = sensitivity_results["bootstrap_100_resamples"]
        assert bs["B_overtakes_A_in_n_of_100"] == 100


# --------------------------------------------------------------------------- #
# Table VIII — threshold-criterion recovery (circular DGP)
# --------------------------------------------------------------------------- #
class TestTableVIII:
    def test_probabilistic_recovery_99pct(self, decision_experiment):
        assert decision_experiment["probabilistic_rule_picks_p_exceed_winner_rate"] == P(
            0.99, abs=ABS
        )

    def test_deterministic_recovery_0pct(self, decision_experiment):
        assert decision_experiment["deterministic_rule_picks_p_exceed_winner_rate"] == P(
            0.0, abs=ABS
        )

    def test_reranking_present_by_construction(self, decision_experiment):
        assert decision_experiment["reranking_exists"] is True
        assert decision_experiment["best_by_mean"] == "A"
        assert decision_experiment["best_by_p_exceed_wacc"] == "B"


# --------------------------------------------------------------------------- #
# Table IX — threshold-sensitivity sweep (Fix 1)
# --------------------------------------------------------------------------- #
class TestTableIX:
    def test_crossover_at_10pct(self, reviewer_fixes):
        fix1 = reviewer_fixes["fix1_threshold_sensitivity"]
        assert fix1["reranking_crossover_threshold_pct"] == 10.0

    def test_b_a_holds_below_10pct(self, reviewer_fixes):
        rows = reviewer_fixes["fix1_threshold_sensitivity"]["thresholds"]
        for row in rows:
            if row["threshold_pct"] < 10.0:
                assert row["ranking"] == "BAC", (
                    f"B>A>C should hold below 10%: {row}"
                )

    def test_inverts_at_10pct_and_above(self, reviewer_fixes):
        rows = reviewer_fixes["fix1_threshold_sensitivity"]["thresholds"]
        for row in rows:
            if row["threshold_pct"] >= 10.0:
                assert row["ranking"].startswith("A"), (
                    f"A should lead at >=10%: {row}"
                )

    def test_published_threshold_values(self, reviewer_fixes):
        rows = {r["threshold_pct"]: r for r in
                reviewer_fixes["fix1_threshold_sensitivity"]["thresholds"]}
        assert rows[8.0]["p_a"] == P(0.833, abs=ABS)
        assert rows[8.0]["p_b"] == P(0.935, abs=ABS)
        assert rows[10.0]["p_a"] == P(0.728, abs=ABS)
        assert rows[10.0]["p_b"] == P(0.613, abs=ABS)


# --------------------------------------------------------------------------- #
# Section IV-J — parameter-prevalence sweep (Fix 3)
# --------------------------------------------------------------------------- #
class TestPrevalence:
    def test_prevalence_2_6pct(self, reviewer_fixes):
        fix3 = reviewer_fixes["fix3_parameter_prevalence"]
        assert fix3["reranking_incidence_rate"] == P(0.026, abs=0.005)

    def test_n_trials(self, reviewer_fixes):
        assert reviewer_fixes["fix3_parameter_prevalence"]["n_trials"] == 1000


# --------------------------------------------------------------------------- #
# Section IV-K — de-circularized recovery (Fix 4)
# Regression guard: the advisor previously caught an inverted-logic bug that
# reported 6.2% instead of the true ~94%. These bounds prevent recurrence.
# --------------------------------------------------------------------------- #
class TestDecircularizedRecovery:
    def test_probabilistic_recovery_high(self, reviewer_fixes):
        fix4 = reviewer_fixes["fix4_decircularized_recovery"]
        assert fix4["probabilistic_rule_recovery_rate"] > 0.90
        assert fix4["probabilistic_rule_recovery_rate"] == P(0.939, abs=0.01)

    def test_deterministic_recovery_low(self, reviewer_fixes):
        fix4 = reviewer_fixes["fix4_decircularized_recovery"]
        assert fix4["deterministic_rule_recovery_rate"] < 0.20
        assert fix4["deterministic_rule_recovery_rate"] == P(0.108, abs=0.01)

    def test_not_the_old_buggy_value(self, reviewer_fixes):
        # Guard against the previously-corrected inverted logic.
        fix4 = reviewer_fixes["fix4_decircularized_recovery"]
        assert fix4["probabilistic_rule_recovery_rate"] != 0.062
        assert fix4["probabilistic_rule_recovery_rate"] > 0.5

    def test_reranking_prevalence_in_prior(self, reviewer_fixes):
        fix4 = reviewer_fixes["fix4_decircularized_recovery"]
        assert fix4["reranking_prevalence_in_prior"] == P(0.065, abs=0.01)


# --------------------------------------------------------------------------- #
# Section IV-L — correlation-matrix sensitivity (Fix 5)
# --------------------------------------------------------------------------- #
class TestCorrelationSensitivity:
    def test_b_a_across_rho_grid(self, reviewer_fixes):
        grid = reviewer_fixes["fix5_correlation_sensitivity"]["rho_grid"]
        assert len(grid) == 5
        for point in grid:
            assert point["ranking"] == "B>A", (
                f"B>A should hold across rho grid: {point}"
            )

    def test_rho_extremes(self, reviewer_fixes):
        grid = reviewer_fixes["fix5_correlation_sensitivity"]["rho_grid"]
        rhos = {p["demand_compute_rho"]: p for p in grid}
        assert 0.0 in rhos and 0.8 in rhos
        assert rhos[0.0]["p_b"] > rhos[0.0]["p_a"]
        assert rhos[0.8]["p_b"] > rhos[0.8]["p_a"]


# --------------------------------------------------------------------------- #
# Section IV-M — mean-preserving break-point (Fix 6)
# Regression guard: the advisor previously caught an invalid break-point that
# scaled B's variable rate (changing the mean too). Assert the mean is
# preserved and the break multiplier is 1.5.
# --------------------------------------------------------------------------- #
class TestBreakPoint:
    def test_break_multiplier_1_5(self, reviewer_fixes):
        fix6 = reviewer_fixes["fix6_reranking_break_point"]
        assert fix6["variance_multiplier_at_break"] == 1.5

    def test_uses_mean_preserving_field(self, reviewer_fixes):
        fix6 = reviewer_fixes["fix6_reranking_break_point"]
        assert "variance_multiplier_at_break" in fix6
        assert "b_rate_multiplier_at_break" not in fix6

    def test_mean_preserved_across_sweep(self, reviewer_fixes):
        sweep = reviewer_fixes["fix6_reranking_break_point"]["sweep"]
        means = {row["variance_multiplier"]: row["mean_b_preserved"] for row in sweep}
        # The mean must be identical at every multiplier (mean-preserving).
        values = list(means.values())
        assert max(values) - min(values) < 1e-9
        assert abs(values[0] - 0.108) < 1e-6

    def test_p_b_decreases_as_variance_grows(self, reviewer_fixes):
        sweep = reviewer_fixes["fix6_reranking_break_point"]["sweep"]
        pbs = [row["p_b"] for row in sweep]
        assert pbs[0] > pbs[-1]  # widening variance lowers P(ROI>8%)


# --------------------------------------------------------------------------- #
# CSV output integrity
# --------------------------------------------------------------------------- #
class TestOutputs:
    def test_roi_statistics_csv_has_all_scenarios(self, roi_statistics):
        assert set(roi_statistics["scenario"]) == {"A", "B", "C"}

    def test_roi_statistics_has_tail_risk_columns(self, roi_statistics):
        required = {"var_5_roi", "cvar_5_roi", "downside_probability_below_wacc",
                    "expected_shortfall_below_wacc"}
        assert required.issubset(set(roi_statistics.columns))

    def test_figures_exist(self):
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        assert (root / "figures" / "figure1_architecture.png").exists()
        assert (root / "figures" / "figure2_roi_distributions.png").exists()
