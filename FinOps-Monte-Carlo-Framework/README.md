# FinOps Monte Carlo Framework

A Monte Carlo simulation framework for evaluating multi-cloud data pipeline investment decisions under correlated uncertainty. Companion reference implementation for the manuscript *"Integrating Predictive Demand Analytics into Multi-Cloud Data Pipelines: A Monte Carlo Framework for Enterprise Investment Decisions"* by Aditya Sumbaraju, prepared for submission to IEEE Access.

> **Status:** Manuscript in preparation for submission to IEEE Access. This repository contains the reference implementation used to generate all results reported in the manuscript. Parameter values are illustrative calibrated assumptions for a reproducible example, not proprietary production data.

## Key Results (Table V)

10,000 iterations, 8% WACC, 3-year NPV horizon.

| Scenario | Mean ROI | SD (pts) | P(ROI > 8%) |
|----------|----------|----------|-------------|
| A: Capacity Expansion | 14.5% | 6.9 | 83.3% |
| B: ETL Automation | 10.8% | 2.1 | 93.5% |
| C: Governance Tooling | 9.5% | 4.1 | 60.7% |

The probabilistic ranking (B > A > C by probability of clearing the 8% WACC threshold) differs from the mean-ROI ranking (A > B > C). This reranking is the central finding of the manuscript and is confirmed stable across Student-t copula, independence, and data-quality-degradation perturbations, and in 100 of 100 bootstrap resamples.

## Quick Start

```bash
pip install -r requirements.txt
python main.py                 # generates outputs/roi_statistics.csv and Table V
python sensitivity_analysis.py # generates outputs/sensitivity_analysis.csv
python generate_figures.py     # generates figures/figure1_architecture.png and figure2_roi_distributions.png
```

## Repository Structure

- `main.py` - master simulation runner (Table V)
- `sensitivity_analysis.py` - correlation/data-quality robustness + bootstrap
- `generate_figures.py` - manuscript figures
- `scenarios/scenario_{a,b,c}.py` - scenario ROI equations
- `utils/copula.py` - Gaussian and Student-t copula sampling
- `config/params_config.json` - all distributions, correlations, and calibrated parameters
- `outputs/` - simulation results (CSV, JSON). This is the only results directory; `main.py` and `sensitivity_analysis.py` both write here. (An older draft used a `results/` folder — it is unused and can be deleted.)
- `figures/` - manuscript figures

## Financial Model

ROI is NPV-based: `ROI = (AnnualBenefit × annuity_factor − Investment) / Investment`, where the annuity factor at 8% WACC over 3 years is 2.577. The decision threshold is the 8% WACC. Each scenario's annual benefit combines a fixed (volume-invariant) component and a demand-linked component scaled to annual cloud spend, which carries the copula correlation structure and gives each scenario a distinct, economically defensible variance.

## License

See `LICENSE`.

## Migration Note (Revision 2.0)

This repository was revised end-to-end to fix a critical unit-semantics bug (per-record costs were previously
off by 1000x, causing ROI values ~1000x too high) plus a wrong decision threshold (20% instead of the
intended 8% WACC) and a zero-discount-rate NPV calculation. This zip is a **full replacement** of the
`FinOps-Monte-Carlo-Framework` directory, not an incremental patch.

If you overlay these files onto the existing GitHub repository, also **delete** the following legacy files,
which are superseded and would otherwise remain as stale/conflicting duplicates:
- `main_orig.py`
- `01_sensitivity_analysis_framework.py`
- `02_ranking_stability_analyzer.py`
- `QUICKSTART.md` (its "Expected output" section quoted the old, incorrect numbers)
- `PROJECT_SUMMARY.md` / `MANIFEST.md` (if they reference the old Table V figures)
- The previous `outputs/` and `results/` directories (regenerate via `main.py` and `sensitivity_analysis.py`)

The corrected, single source of truth is: `main.py`, `sensitivity_analysis.py`, `generate_figures.py`,
`scenarios/`, `utils/copula.py`, and `config/params_config.json`.
