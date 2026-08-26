# FinOps Monte Carlo Framework

**Integrating Predictive Demand Analytics into Multi-Cloud Data Pipelines: A Monte Carlo Framework for Enterprise Investment Decisions**

This repository contains the complete implementation of a Monte Carlo simulation framework for evaluating capital investment decisions in enterprise data operations, published in IEEE Access.

## Project Structure

```
FinOps-Monte-Carlo-Framework/
├── scenarios/                    # Investment scenario classes
│   ├── scenario_a.py            # Capacity Expansion (200K investment)
│   ├── scenario_b.py            # Reconciliation Automation (150K investment)
│   └── scenario_c.py            # Governance Tooling (300K investment)
├── config/
│   └── params_config.json       # Centralized parameter configuration
├── utils/
│   └── copula.py                # Gaussian copula utilities
├── main.py                      # Master simulation runner
├── sensitivity_analysis.py      # Ranking stability under uncertainty
├── outputs/                     # Results directory
├── docs/                        # Documentation
└── README.md                    # This file
```

## Key Features

### ✓ Correlation-Preserving Sampling
Uses Gaussian copulas to maintain observed multi-variable dependencies:
- **Demand–Compute-Cost correlation**: 0.62
- **Demand–Utilization correlation**: 0.55
- **Impact**: Ignoring these correlations underestimates ROI variance by ~40%

### ✓ Parameterized Configuration
All assumptions stored in `config/params_config.json`:
- 5-variable probability model with documented sources
- Full correlation matrix for copula construction
- Scenario-specific benefits and investment parameters

### ✓ Three Investment Scenarios
1. **Scenario A**: Pipeline Capacity Expansion ($200K)
   - Unit cost discounts from volume growth
   - Elimination of on-demand overflow surcharges
   - SLA compliance improvements

2. **Scenario B**: ETL Reconciliation Automation ($150K)
   - Fixed labor savings (25% FTE reduction = $12.5K/year)
   - Error recovery from chargeback disputes (~2% transaction rate)
   - Throughput improvements

3. **Scenario C**: Multi-Cloud Governance Tooling ($300K)
   - Risk mitigation (compliance cost avoidance)
   - Data quality improvement (dispute reduction)
   - Compute efficiency gains

### ✓ Sensitivity Analysis
Tests ranking stability under:
- Independent sampling (no correlation)
- Observed correlation structure
- Data-quality degradation (0%, 10%, 25%)

## Running the Simulation

### 1. Install Dependencies
```bash
pip install numpy scipy pandas matplotlib
```

### 2. Run Main Simulation
```bash
python main.py
```

**Output files** (in `outputs/`):
- `roi_statistics.csv` — Mean, std, percentiles, threshold exceedance
- `roi_distributions.csv` — Full ROI distribution for each scenario
- `simulation_results.json` — JSON summary of all statistics

### 3. Run Sensitivity Analysis
```bash
python sensitivity_analysis.py
```

**Output file**:
- `sensitivity_analysis.csv` — Ranking stability comparison

## Configuration

Edit `config/params_config.json` to customize:

- **Demand volume**: Daily transaction volume (default: 100,000 records/day)
- **Unit cost**: Processing cost per record (default: $18)
- **Compute cost**: Infrastructure cost per record (default: $0.42)
- **Resource utilization**: Cloud resource usage (default: 68%)
- **Pipeline throughput**: Records processed per second (default: 8,500 rec/sec)

All parameters include documented sources and units.

## Key Research Questions

**RQ1**: Does preserving observed inter-variable dependence change capital-investment rankings relative to deterministic and independent-sampling models?

**RQ2**: How sensitive is ranking stability to distributional assumptions, correlation estimates, and data-quality degradation?

**RQ3**: What operational latency, data-quality, and governance controls are required for deployment?

## Reproducibility

- All parameters are version-controlled in JSON
- Random seed: 42 (configurable in params_config.json)
- 10,000 Monte Carlo iterations per scenario
- Correlation matrix validated for positive semi-definiteness
- Code available in public repository

## Citation

If you use this framework, please cite:

```bibtex
@article{Sumbaraju2024FinOps,
  title={Integrating Predictive Demand Analytics into Multi-Cloud Data Pipelines: 
         A Monte Carlo Framework for Enterprise Investment Decisions},
  author={Sumbaraju, Aditya},
  journal={IEEE Access},
  year={2026}
}
```

## Important Notes

- This is an **illustrative demonstration**, not validation against a live production deployment
- Organizations adopting the framework should substitute **their own pipeline-derived distributions** before relying on the output for capital decisions
- The reference parameterization is calibrated to publicly reported FinOps benchmarks, not proprietary operational data

## References

TBD

## License

TBD

## Contact

For questions or issues, contact: adityacsumbaraju@gmail.com
