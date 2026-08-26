# Methodology Document

## Overview

This framework implements a Monte Carlo simulation for evaluating capital investment decisions in enterprise data operations. It addresses the structural gap between real-time operational pipelines and static batch-based financial models by embedding simulation natively within a multi-cloud data architecture.

## Mathematical Framework

### 1. Five-Variable Probability Model

The framework models uncertainty across five operational variables:

| Variable | Distribution | Mean | Std Dev / CV |
|----------|--------------|------|--------------|
| Demand Volume (records/day) | Log-normal | 100,000 | CV = 6% |
| Unit Cost (USD/record) | Log-normal | $18 | σ = $3.60 |
| Compute Cost (USD/record) | Log-normal | $0.42 | σ = $0.084 |
| Resource Utilization (%) | Beta | 68% | α=4.32, β=2.16 |
| Pipeline Throughput (rec/sec) | Normal | 8,500 | σ = 850 |

**Source**: Public FinOps benchmarks (IDC, enterprise cloud cost surveys)

### 2. Gaussian Copula Construction

Preserves observed correlation structure while allowing marginal distributions to retain empirically-fitted forms.

**Correlation Matrix**:
```
                demand  unit_cost  utilization  throughput  compute_cost
demand          1.0     0.15      0.55         0.08        0.62
unit_cost       0.15    1.0       0.12         0.05        0.25
utilization     0.55    0.12      1.0          0.30        0.18
throughput      0.08    0.05      0.30         1.0         0.10
compute_cost    0.62    0.25      0.18         0.10        1.0
```

**Key Correlations**:
- Demand–Compute-Cost (0.62): Peak demand drives infrastructure costs
- Demand–Utilization (0.55): Higher volume → higher resource utilization
- **Impact of ignoring**: ROI variance underestimated by ~40%

### 3. Copula Sampling Process

1. Generate standard normal samples with correlation matrix Σ:
   ```
   Z ~ N(0, Σ)  // 10,000 iterations
   ```

2. Transform to uniform via standard normal CDF:
   ```
   U = Φ(Z)  // Element-wise CDF application
   ```

3. Apply inverse marginal CDFs (PPF) to each column:
   ```
   X₁ = F₁⁻¹(U₁)  // demand volume via Lognormal PPF
   X₂ = F₂⁻¹(U₂)  // unit cost via Lognormal PPF
   ...
   X₅ = F₅⁻¹(U₅)  // compute cost via Lognormal PPF
   ```

**Result**: Each variable follows its specified marginal distribution while preserving the observed correlation structure.

### 4. ROI Calculation

For each scenario:

```
Total Benefit (per year) = Σ(Scenario-specific benefits)
NPV = Total Benefit × Horizon (years)
ROI = (NPV - Investment) / Investment
```

## Scenario Definitions

### Scenario A: Pipeline Capacity Expansion
**Investment**: $200,000
**Horizon**: 3 years

**Benefits**:
1. Unit cost savings from volume-tier discounts: 8% × annual_demand × unit_cost
2. Overflow cost avoided (3% of transactions × 15% on-demand premium)
3. SLA premium from 99.99% uptime: 2% revenue uplift

### Scenario B: ETL Reconciliation Automation
**Investment**: $150,000
**Horizon**: 3 years

**Benefits**:
1. Labor savings: 25% FTE reduction × $50K/FTE = $12,500/year (FIXED, not demand-scaled)
2. Error recovery: 12% × (2% dispute rate) × annual_demand × unit_cost
3. Throughput value: SLA baseline ($0.001/record) × 5% improvement

### Scenario C: Multi-Cloud Governance Tooling
**Investment**: $300,000
**Horizon**: 3 years

**Benefits**:
1. Risk mitigation: $100K base exposure × 5% reduction (cost avoidance)
2. Data quality improvement: 18% dispute reduction on 2% of transactions
3. Compute efficiency: 20% reduction in wasteful resource consumption

## Key Metrics

**mean_roi**: E[ROI]
- Average return across all scenarios
- Directional indicator of expected value

**std_roi**: σ(ROI)
- Volatility/uncertainty
- Higher σ = higher risk

**Percentiles (p5, p25, p75, p95)**:
- Confidence intervals for decision-making
- p5 = pessimistic case, p95 = optimistic case

**Threshold Exceedance**:
- P(ROI > 20%)
- Key decision metric: if > 70%, scenario meets hurdle rate

**Negative ROI Probability**:
- P(ROI < 0)
- Risk of capital loss

## Sensitivity Analysis

Tests ranking stability under three alternative assumptions:

### 1. Independent Sampling
Set all correlations to 0 (identity matrix).
- Question: Does correlation structure matter?
- Expected: ROI variances drop by ~40%

### 2. Data-Quality Degradation
Reduce correlations by factor (1 - degradation_level):
- 0% degradation: Observed correlations (baseline)
- 10% degradation: Correlations × 0.9
- 25% degradation: Correlations × 0.75
- Question: Do rankings remain stable as data quality decays?

### 3. T-Copula (Tail Dependence)
Alternative copula with degrees of freedom = 5.
- Question: Does tail dependence risk matter?
- Expected: < 2% variation in final ROI probabilities

## Reproducibility

- **Random seed**: 42 (configurable)
- **Iterations**: 10,000 (adequate for ~1% Monte Carlo standard error)
- **Discount rate**: 0% in base case (can be sensitivity-tested)
- **All parameters**: Version-controlled in JSON
- **Validation**: Correlation matrix checked for positive semi-definiteness

## Validation Against Prior Work

Compares four methodological approaches:

1. **Deterministic (point estimate)**
   - Single best-guess values
   - No uncertainty quantification
   - Baseline for comparison

2. **Independent Monte Carlo**
   - Random sampling without correlation
   - Breaks observed variable dependencies
   - Shows 40% underestimation of ROI variance

3. **Correlated Monte Carlo (This work)**
   - Gaussian copulas preserve correlation
   - Realistic uncertainty quantification
   - Enables ranking stability analysis

4. **Pipeline-native (Future work)**
   - Incorporates real-time pipeline data
   - Periodically refreshed correlation estimates
   - Addresses architecture gap

## Assumptions & Limitations

1. **Illustrative parameterization**: Based on public benchmarks, not proprietary data
2. **Constant marginal distributions**: Assumes parameters don't shift over 3-year horizon
3. **Linear cost/benefit scaling**: May not hold for extreme demand scenarios
4. **No discounting**: Base case uses 0% discount rate (sensitivity-testable)
5. **No system dynamics**: Assumes independent scenarios (not competing for resources)

## Implementation Quality

- **Code coverage**: All scenarios tested with known-good inputs
- **Numerical stability**: Log-normal parameterization avoids underflow
- **Validation**: Correlation matrix eigenvalues checked for PSD
- **Reproducibility**: Seed fixed and documented

## References

See main manuscript (IEEE_Access_Article_FINAL.docx) for:
- Literature review on Monte Carlo capital allocation
- Copula theory and enterprise applications
- FinOps benchmarking sources
- Data quality impact analysis
