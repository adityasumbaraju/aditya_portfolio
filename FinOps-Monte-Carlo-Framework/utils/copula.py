"""
Gaussian Copula utilities - correlation-preserving sampling
"""

import numpy as np
from scipy.stats import norm, multivariate_normal


def generate_gaussian_copula_samples(correlation_matrix, n_samples, random_seed=None):
    """
    Generate uniform copula samples preserving correlation structure.

    Args:
        correlation_matrix: NxN correlation matrix
        n_samples: Number of samples to generate
        random_seed: Optional random seed for reproducibility

    Returns:
        numpy array of shape (n_samples, N) with values in [0,1]
    """
    if random_seed:
        np.random.seed(random_seed)

    # Generate standard normal samples with specified correlation
    z_samples = multivariate_normal.rvs(
        mean=np.zeros(len(correlation_matrix)),
        cov=correlation_matrix,
        size=n_samples
    )

    # Transform to uniform via standard normal CDF
    u_samples = norm.cdf(z_samples)

    return u_samples


def validate_correlation_matrix(corr_matrix):
    """
    Validate correlation matrix properties.

    Checks:
    - Symmetric
    - Diagonal = 1
    - All entries in [-1, 1]
    - Positive semi-definite
    """
    n = len(corr_matrix)

    # Check symmetry
    assert np.allclose(corr_matrix, corr_matrix.T), "Correlation matrix must be symmetric"

    # Check diagonal
    assert np.allclose(np.diag(corr_matrix), 1.0), "Diagonal must be 1"

    # Check range
    assert np.all((corr_matrix >= -1) & (corr_matrix <= 1)), "All entries must be in [-1, 1]"

    # Check positive semi-definite
    eigenvalues = np.linalg.eigvals(corr_matrix)
    assert np.all(eigenvalues >= -1e-10), "Correlation matrix must be positive semi-definite"

    return True
