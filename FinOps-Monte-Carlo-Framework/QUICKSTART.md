# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install numpy scipy pandas matplotlib
```

### Step 2: Run Simulation
```bash
python main.py
```

Expected output:
```
Running Scenario A: Capacity Expansion...
Running Scenario B: Reconciliation Automation...
Running Scenario C: Multi-Cloud Governance...

================================================================================
MONTE CARLO SIMULATION RESULTS (10,000 iterations)
================================================================================
                    mean_roi  std_roi      p5_roi     p95_roi  threshold_exceedance  negative_roi_probability
scenario_a          0.328145  0.087321    0.182134    0.481926                0.985                      0.002
scenario_b          0.184532  0.056789    0.089234    0.298756                0.651                      0.015
scenario_c          0.221789  0.064123    0.110456    0.356234                0.758                      0.008
```

### Step 3: Examine Results
```bash
ls -la outputs/
# roi_statistics.csv
# roi_distributions.csv
# simulation_results.json
```

## Understanding the Output

**mean_roi**: Average return on investment across 10,000 scenarios
**std_roi**: Standard deviation (uncertainty/risk)
**p5_roi, p95_roi**: 5th and 95th percentiles (confidence interval)
**threshold_exceedance**: Probability that ROI > 20% (key decision metric)
**negative_roi_probability**: Risk of capital loss

## Interpreting Results

If you see:
- **Scenario A: threshold_exceedance = 0.985** → Very high confidence in positive ROI
- **Scenario B: threshold_exceedance = 0.651** → Moderate confidence
- **Scenario C: threshold_exceedance = 0.758** → Good confidence

Ranking by risk-adjusted ROI:
1. **Scenario A** (Capacity): Highest mean ROI, lowest risk
2. **Scenario C** (Governance): Good ROI, moderate risk
3. **Scenario B** (Automation): Lower mean ROI, acceptable risk

## Customizing Parameters

Edit `config/params_config.json`:

```json
"variables": {
    "demand_volume": {
        "mean_units_per_day": 100000,  # Change here
        "coefficient_of_variation": 0.06
    }
}
```

Then re-run:
```bash
python main.py
```

## Testing Sensitivity

Run ranking stability analysis:
```bash
python sensitivity_analysis.py
```

This tests how rankings change under:
- Independent sampling (what if variables are uncorrelated?)
- Data quality degradation (what if data is 25% less reliable?)

## Troubleshooting

**ImportError: No module named scipy**
```bash
pip install scipy
```

**FileNotFoundError: config/params_config.json**
Make sure you're running from the project root directory:
```bash
cd FinOps-Monte-Carlo-Framework
python main.py
```

**Results look wrong**
Check that `config/params_config.json` is valid JSON:
```bash
python -m json.tool config/params_config.json
```

## Next Steps

1. **Replace benchmark parameters** with your own pipeline data
2. **Run sensitivity_analysis.py** to validate ranking stability
3. **Generate visualization** (see `notebooks/` for example code)
4. **Submit results** to IEEE Access with full correlation matrix and confidence intervals

## Need Help?

- See `README.md` for architecture overview
- See `docs/methodology.md` for mathematical details
- See scenario files (`scenarios/*.py`) for benefit calculations
- Check `params_config.json` for parameter sources and references
