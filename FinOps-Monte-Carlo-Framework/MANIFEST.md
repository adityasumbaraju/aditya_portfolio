# Project Manifest - FinOps Monte Carlo Framework

**Generated**: 2026-08-26 05:11:38
**Total Files**: 14
**Total Size**: 51.77 KB

## Directory Structure

```
FinOps-Monte-Carlo-Framework/
├── scenarios/                       # Investment scenario implementations
│   ├── scenario_a.py               # Pipeline Capacity Expansion (4.0 KB)
│   ├── scenario_b.py               # Reconciliation Automation (4.2 KB)
│   └── scenario_c.py               # Governance Tooling (4.1 KB)
│
├── config/                          # Configuration and parameters
│   └── params_config.json          # Centralized 5-variable model + correlation matrix (4.4 KB)
│
├── utils/                           # Utility modules
│   └── copula.py                   # Gaussian copula utilities (1.7 KB)
│
├── docs/                            # Documentation
│   └── METHODOLOGY.md              # Complete mathematical framework (6.6 KB)
│
├── outputs/                         # Simulation results directory (empty at init)
│
├── main.py                          # Master simulation runner (5.1 KB)
├── sensitivity_analysis.py          # Ranking stability analysis (4.7 KB)
│
├── README.md                        # Project overview (5.3 KB)
├── QUICKSTART.md                    # 5-minute setup guide (3.3 KB)
├── PROJECT_SUMMARY.md              # Detailed project description (7.1 KB)
│
├── requirements.txt                 # Python dependencies (59 bytes)
├── LICENSE                          # MIT license (1.1 KB)
└── .gitignore                       # Git ignore rules (420 bytes)
```

## File Descriptions

### Core Scenario Classes (scenarios/)

**scenario_a.py** (4.0 KB)
- Pipeline Capacity Expansion scenario
- Investment: $200,000 over 12 months
- Benefits: Volume discounts, overflow avoidance, SLA premium
- CORRECTED: Uses Gaussian copula with PPF transforms

**scenario_b.py** (4.2 KB)
- ETL Reconciliation Automation scenario
- Investment: $150,000 over 12 months
- Benefits: Labor savings (fixed), error recovery (parametric), throughput gains
- CORRECTED: Error recovery now only applies to ~2% disputed transactions

**scenario_c.py** (4.1 KB)
- Multi-Cloud Governance Tooling scenario
- Investment: $300,000 over 12 months
- Benefits: Risk mitigation, data quality, compute efficiency
- CORRECTED: All benefits parameterized, no hardcoded values

### Configuration (config/)

**params_config.json** (4.4 KB)
- Complete 5-variable probability model:
  * Demand volume (lognormal, 100K units/day)
  * Unit cost (lognormal, $18/record)
  * Compute cost (lognormal, $0.42/record)
  * Resource utilization (Beta, 68%)
  * Pipeline throughput (Normal, 8,500 rec/sec)
- Full 5×5 Gaussian copula correlation matrix
- Scenario-specific parameters (benefit rates, investment amounts)
- All values sourced from FinOps benchmarks

### Utilities (utils/)

**copula.py** (1.7 KB)
- generate_gaussian_copula_samples(): Creates uniform samples preserving correlation
- validate_correlation_matrix(): Checks PSD, symmetry, diagonal=1
- Used by all scenario classes

### Documentation (docs/)

**METHODOLOGY.md** (6.6 KB)
- Complete mathematical framework
- 5-variable probability distributions
- Gaussian copula construction and sampling process
- Scenario benefit calculations (detailed formulas)
- Key metrics (mean ROI, std ROI, threshold exceedance)
- Sensitivity analysis methodology
- Reproducibility notes

### Main Execution Files

**main.py** (5.1 KB)
- MonteCarloFramework class
- Orchestrates simulation across all three scenarios
- Generates Gaussian copula samples
- Computes ROI distributions
- Exports results to CSV and JSON
- Prints summary statistics table

**sensitivity_analysis.py** (4.7 KB)
- SensitivityAnalysis class
- Tests ranking stability under:
  * Independent sampling (no correlation)
  * Observed correlation (baseline)
  * Data-quality degradation (10%, 25%)
- Exports comparison table

### Documentation Files

**README.md** (5.3 KB)
- Project overview
- Feature highlights
- Installation and execution instructions
- Configuration guide
- Research questions
- Citation information

**QUICKSTART.md** (3.3 KB)
- 5-minute setup guide
- Step-by-step execution
- Output interpretation
- Parameter customization
- Troubleshooting

**PROJECT_SUMMARY.md** (7.1 KB)
- Comprehensive project summary
- What's included and why
- Critical improvements made
- How to use the framework
- Publication checklist
- Next steps for IEEE Access submission

### Support Files

**requirements.txt** (59 bytes)
- Python dependencies:
  * numpy >= 1.21.0
  * scipy >= 1.7.0
  * pandas >= 1.3.0
  * matplotlib >= 3.4.0

**LICENSE** (1.1 KB)
- MIT license for open-source publication

**.gitignore** (420 bytes)
- Standard Python gitignore
- Excludes __pycache__, outputs, .env, etc.

## How to Use This Package

### 1. Extract the zip file
```bash
unzip FinOps-Monte-Carlo-Framework.zip
cd FinOps-Monte-Carlo-Framework
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the simulation
```bash
python main.py
```

### 4. Check results
```bash
ls -la outputs/
cat outputs/roi_statistics.csv
```

### 5. Test sensitivity
```bash
python sensitivity_analysis.py
cat outputs/sensitivity_analysis.csv
```

## Key Improvements Over Original

✓ **Correlation-Breaking Bug**: Fixed by using PPF transforms instead of independent random sampling
✓ **Error Recovery**: Corrected from 50× overestimate to realistic rate applied only to disputed transactions
✓ **Parameterization**: All benefits moved to central config.json with documented sources
✓ **Reproducibility**: Random seed, iteration count, discount rate all configurable
✓ **Sensitivity Analysis**: Full ranking stability testing under correlation/data-quality uncertainty

## Publication Readiness

This package includes everything needed for IEEE Access submission:
- ✓ Corrected scenario implementations
- ✓ Parameterized configuration with sources
- ✓ Complete documentation (README, QUICKSTART, METHODOLOGY)
- ✓ Sensitivity analysis for ranking stability
- ✓ MIT license for open-source code sharing
- ✓ Reproducible code (seed fixed, deterministic)

## Next Steps

1. Replace benchmark parameters in params_config.json with your pipeline data
2. Run main.py to regenerate ROI distributions
3. Run sensitivity_analysis.py to validate ranking stability
4. Generate figures for manuscript Section IV
5. Prepare results table for publication
6. Submit to IEEE Access with this complete, documented code

---

**Framework Version**: 1.0.0
**Author**: Aditya Sumbaraju
**Publication**: IEEE Access
**License**: MIT
**Generated**: 2026-08-26 05:11:38
