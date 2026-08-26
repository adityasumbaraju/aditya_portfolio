import json
import os
import warnings

import numpy as np
from scipy.stats import beta, lognorm, norm, t

warnings.filterwarnings("ignore")


class CorrelationSensitivityAnalysis:
    """
    Runs Monte Carlo samples under three dependence structures:

    1. Observed Gaussian copula: preserves the configured correlation matrix.
    2. Independent sampling: removes all dependence.
    3. Student's t-copula: preserves correlation while adding tail dependence.
    """

    VARIABLE_ORDER = [
        "demand_volume",
        "unit_cost_usd",
        "resource_utilization_pct",
        "pipeline_throughput_recs_per_sec",
        "compute_cost_usd_per_unit"
    ]

    def __init__(self, params, n_iterations=10000, seed=42):
        self.params = params
        self.n_iterations = n_iterations
        self.seed = seed
        self.results = {}

        self.corr_matrix = np.array(
            self.params["correlation_matrix"]["matrix"],
            dtype=float
        )

        self._validate_config()

    def _validate_config(self):
        """Validate dimensions and consistency of required configuration."""
        expected_size = len(self.VARIABLE_ORDER)

        if self.corr_matrix.shape != (expected_size, expected_size):
            raise ValueError(
                f"Correlation matrix must be {expected_size}x{expected_size}; "
                f"received {self.corr_matrix.shape}."
            )

        configured_order = self.params["correlation_matrix"]["variables"]

        if configured_order != self.VARIABLE_ORDER:
            raise ValueError(
                "The correlation_matrix variable order does not match "
                "the sensitivity-analysis variable order.\n"
                f"Expected: {self.VARIABLE_ORDER}\n"
                f"Received: {configured_order}"
            )

        if not np.allclose(self.corr_matrix, self.corr_matrix.T):
            raise ValueError("Correlation matrix must be symmetric.")

        eigenvalues = np.linalg.eigvalsh(self.corr_matrix)

        if np.any(eigenvalues < -1e-10):
            raise ValueError(
                "Correlation matrix is not positive semi-definite. "
                f"Minimum eigenvalue: {eigenvalues.min():.6f}"
            )

    def sample_observed_copula(self):
        """Generate samples using the configured Gaussian copula."""
        rng = np.random.default_rng(self.seed)

        z = rng.multivariate_normal(
            mean=np.zeros(len(self.VARIABLE_ORDER)),
            cov=self.corr_matrix,
            size=self.n_iterations
        )

        u = norm.cdf(z)
        return self._map_uniforms_to_distributions(u)

    def sample_independent(self):
        """Generate samples independently, with no correlation."""
        rng = np.random.default_rng(self.seed)

        u = rng.uniform(
            low=0.0,
            high=1.0,
            size=(self.n_iterations, len(self.VARIABLE_ORDER))
        )

        return self._map_uniforms_to_distributions(u)

    def sample_t_copula(self, df=5):
        """
        Generate samples using a Student's t-copula.

        df=5 introduces more joint extreme outcomes than a Gaussian copula.
        """
        if df <= 0:
            raise ValueError("Degrees of freedom must be greater than zero.")

        rng = np.random.default_rng(self.seed)

        z = rng.multivariate_normal(
            mean=np.zeros(len(self.VARIABLE_ORDER)),
            cov=self.corr_matrix,
            size=self.n_iterations
        )

        chi_square = rng.chisquare(df, size=self.n_iterations)
        t_samples = z * np.sqrt(df / chi_square)[:, np.newaxis]

        # A t-copula uses the Student's t CDF, not the normal CDF.
        u = t.cdf(t_samples, df=df)

        return self._map_uniforms_to_distributions(u)

    def _map_uniforms_to_distributions(self, u):
        """
        Transform uniform copula values to configured marginal distributions.

        Matrix column order:
        0: demand_volume
        1: unit_cost_usd
        2: resource_utilization_pct
        3: pipeline_throughput_recs_per_sec
        4: compute_cost_usd_per_unit
        """
        vars_config = self.params["variables"]

        expected_shape = (
            self.n_iterations,
            len(self.VARIABLE_ORDER)
        )

        if u.shape != expected_shape:
            raise ValueError(
                f"Expected uniform sample shape {expected_shape}; "
                f"received {u.shape}."
            )

        # Avoid 0 and 1 because inverse CDF calls could return infinity.
        u = np.clip(u, 1e-12, 1 - 1e-12)

        samples = np.zeros_like(u, dtype=float)

        for column_index, var_name in enumerate(self.VARIABLE_ORDER):
            config = vars_config[var_name]
            distribution = config["distribution"].lower()

            if distribution == "lognormal":
                if var_name == "demand_volume":
                    mean = config["mean_units_per_day"]
                    std_dev = mean * config["coefficient_of_variation"]
                else:
                    mean = config["mean"]
                    std_dev = config["std_dev"]

                coefficient_of_variation = std_dev / mean
                sigma = np.sqrt(
                    np.log(1 + coefficient_of_variation ** 2)
                )
                mu = np.log(mean) - 0.5 * sigma ** 2

                samples[:, column_index] = lognorm.ppf(
                    u[:, column_index],
                    s=sigma,
                    scale=np.exp(mu)
                )

            elif distribution == "beta":
                samples[:, column_index] = beta.ppf(
                    u[:, column_index],
                    a=config["alpha"],
                    b=config["beta"]
                ) * 100

            elif distribution == "normal":
                samples[:, column_index] = norm.ppf(
                    u[:, column_index],
                    loc=config["mean"],
                    scale=config["std_dev"]
                )

            else:
                raise ValueError(
                    f"Unsupported distribution '{distribution}' "
                    f"for variable '{var_name}'."
                )

        return samples

    def save_sample_matrices(self, output_path="results/samples_by_correlation.json"):
        """
        Save all generated sample matrices as JSON.

        Call run_comparison() before calling this method.
        """
        if not self.results:
            raise ValueError(
                "No simulation results exist. Run run_comparison() first."
            )

        output_directory = os.path.dirname(output_path)

        if output_directory:
            os.makedirs(output_directory, exist_ok=True)

        results_output = {
            "variable_order": self.VARIABLE_ORDER,
            "n_iterations": self.n_iterations,
            "random_seed": self.seed,
            "observed_gaussian": self.results["observed"].tolist(),
            "independent": self.results["independent"].tolist(),
            "t_copula_df5": self.results["t_copula_df5"].tolist()
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(results_output, file)

        print(f"✓ Sample matrices saved to {output_path}")

    def run_comparison(self):
        """Run each correlation structure and return three sample matrices."""
        print("\n" + "=" * 80)
        print("SENSITIVITY ANALYSIS: CORRELATION STRUCTURE COMPARISON")
        print("=" * 80 + "\n")
        print(
            f"Running {self.n_iterations:,} iterations for each "
            "correlation structure...\n"
        )

        samples_observed = self.sample_observed_copula()
        print("✓ Observed Gaussian copula (baseline) complete")

        samples_independent = self.sample_independent()
        print("✓ Independent sampling complete")

        samples_t = self.sample_t_copula(df=5)
        print("✓ T-copula (df=5, tail dependence) complete\n")

        self.results = {
            "observed": samples_observed,
            "independent": samples_independent,
            "t_copula_df5": samples_t
        }

        self._compare_correlations(
            samples_observed,
            samples_independent,
            samples_t
        )

        return self.results

    def _compare_correlations(self, observed, independent, t_copula):
        """Print target and realized Pearson correlations."""
        demand_index = self.VARIABLE_ORDER.index("demand_volume")
        compute_index = self.VARIABLE_ORDER.index(
            "compute_cost_usd_per_unit"
        )
        utilization_index = self.VARIABLE_ORDER.index(
            "resource_utilization_pct"
        )

        target_demand_compute = self.corr_matrix[
            demand_index,
            compute_index
        ]
        target_demand_utilization = self.corr_matrix[
            demand_index,
            utilization_index
        ]

        observed_demand_compute = np.corrcoef(
            observed[:, demand_index],
            observed[:, compute_index]
        )[0, 1]

        independent_demand_compute = np.corrcoef(
            independent[:, demand_index],
            independent[:, compute_index]
        )[0, 1]

        t_demand_compute = np.corrcoef(
            t_copula[:, demand_index],
            t_copula[:, compute_index]
        )[0, 1]

        observed_demand_utilization = np.corrcoef(
            observed[:, demand_index],
            observed[:, utilization_index]
        )[0, 1]

        independent_demand_utilization = np.corrcoef(
            independent[:, demand_index],
            independent[:, utilization_index]
        )[0, 1]

        t_demand_utilization = np.corrcoef(
            t_copula[:, demand_index],
            t_copula[:, utilization_index]
        )[0, 1]

        print("CORRELATION STRUCTURE COMPARISON")
        print("-" * 80)
        print("\nTarget correlations (from config):")
        print(f"  Demand–Compute Cost: {target_demand_compute:.2f}")
        print(f"  Demand–Utilization:  {target_demand_utilization:.2f}\n")

        print("Realized Demand–Compute Cost correlation:")
        print(f"  Observed Gaussian: {observed_demand_compute:.4f}")
        print(f"  Independent:       {independent_demand_compute:.4f}")
        print(f"  T-copula (df=5):   {t_demand_compute:.4f}\n")

        print("Realized Demand–Utilization correlation:")
        print(f"  Observed Gaussian: {observed_demand_utilization:.4f}")
        print(f"  Independent:       {independent_demand_utilization:.4f}")
        print(f"  T-copula (df=5):   {t_demand_utilization:.4f}\n")


def main():
    with open("config/params_config.json", "r", encoding="utf-8") as file:
        params = json.load(file)

    sensitivity = CorrelationSensitivityAnalysis(
        params=params,
        n_iterations=params["simulation"]["n_iterations"],
        seed=params["simulation"]["random_seed"]
    )

    results = sensitivity.run_comparison()

    # Creates the results directory automatically, if needed.
    sensitivity.save_sample_matrices(
        output_path="results/samples_by_correlation.json"
    )

    print("=" * 80)
    print("NEXT: Pass these three sample matrices to your scenario calculators")
    print(
        "to compute ROI under each correlation structure and "
        "measure ranking stability."
    )
    print("=" * 80)

    return results


if __name__ == "__main__":
    results = main()