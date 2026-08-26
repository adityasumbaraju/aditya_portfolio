"""
Gaussian Copula utilities - correlation-preserving sampling.

These helpers generate uniform copula samples that preserve the observed
correlation structure among the five simulation variables. They are used by
the sensitivity-analysis framework to test ranking stability under alternative
dependence assumptions (specified Gaussian, independent, Student-t).
"""

import numpy as np
from scipy.stats import norm, multivariate_normal, t


def generate_gaussian_copula_samples(correlation_matrix, n_samples, random_seed=None):
    """
    Generate uniform copula samples preserving the correlation structure.

    Args:
        correlation_matrix: NxN correlation matrix (positive semi-definite).
        n_samples: Number of samples to generate.
        random_seed: Optional random seed for reproducibility.

    Returns:
        numpy array of shape (n_samples, N) with values in [0, 1].
    """
    rng = np.random.default_rng(random_seed)
    z_samples = rng.multivariate_normal(
        mean=np.zeros(len(correlation_matrix)),
        cov=correlation_matrix,
        size=n_samples,
    )
    u_samples = norm.cdf(z_samples)
    return u_samples


def generate_t_copula_samples(correlation_matrix, n_samples, df=5, random_seed=None):
    """
    Generate uniform copula samples using a Student-t copula.

    The t-copula preserves the correlation structure while introducing
    tail dependence, producing more joint extreme outcomes than the
    Gaussian copula. df=5 represents moderate tail dependence.

    Args:
        correlation_matrix: NxN correlation matrix.
        n_samples: Number of samples to generate.
        df: Degrees of freedom for the Student-t distribution.
        random_seed: Optional random seed for reproducibility.

    Returns:
        numpy array of shape (n_samples, N) with values in [0, 1].
    """
    if df <= 0:
        raise ValueError("Degrees of freedom must be greater than zero.")
    rng = np.random.default_rng(random_seed)
    z = rng.multivariate_normal(
        mean=np.zeros(len(correlation_matrix)),
        cov=correlation_matrix,
        size=n_samples,
    )
    chi_square = rng.chisquare(df, size=n_samples)
    t_samples = z * np.sqrt(df / chi_square)[:, np.newaxis]
    u_samples = t.cdf(t_samples, df=df)
    return u_samples


def generate_independent_samples(n_variables, n_samples, random_seed=None):
    """
    Generate independent uniform samples (no correlation structure).

    Used as a baseline to test how ranking changes when inter-variable
    dependence is removed.
    """
    rng = np.random.default_rng(random_seed)
    return rng.uniform(low=0.0, high=1.0, size=(n_samples, n_variables))


def validate_correlation_matrix(corr_matrix):
    """
    Validate correlation matrix properties.

    Checks:
    - Symmetric
    - Diagonal equals 1
    - All entries in [-1, 1]
    - Positive semi-definite
    """
    corr_matrix = np.array(corr_matrix, dtype=float)
    n = len(corr_matrix)
    assert np.allclose(corr_matrix, corr_matrix.T), "Correlation matrix must be symmetric"
    assert np.allclose(np.diag(corr_matrix), 1.0), "Diagonal must be 1"
    assert np.all((corr_matrix >= -1) & (corr_matrix <= 1)), "All entries must be in [-1, 1]"
    eigenvalues = np.linalg.eigvalsh(corr_matrix)
    assert np.all(eigenvalues >= -1e-10), "Correlation matrix must be positive semi-definite"
    return True
