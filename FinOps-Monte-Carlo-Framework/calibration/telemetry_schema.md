# Empirical Calibration Telemetry Schema

This schema defines the observed pipeline telemetry required to replace the
illustrative calibrated assumptions in `config/params_config.json` with
empirically fitted distributions. The calibration script
`calibration/fit_from_telemetry.py` consumes a CSV matching this schema and
emits an empirical parameter template; it fails gracefully (with a clear
message listing required columns) when telemetry is not supplied.

## Required columns (one row per observation; recommend >= 1 full seasonal cycle)

| Column                    | Type    | Unit                  | Target distribution variable |
| ------------------------- | ------- | --------------------- | ---------------------------- |
| `date`                    | ISO-8601| day                   | index / seasonal grouping    |
| `demand_records`          | int     | records/day           | Demand volume (lognormal)     |
| `unit_cost`               | float   | USD per record        | Per-record unit cost (lognormal)|
| `utilization`             | float   | 0..1                  | Resource utilization (Beta)    |
| `throughput`              | float   | records/second        | Pipeline throughput (Normal)   |
| `compute_cost_per_record` | float   | USD per record        | Cloud compute cost (lognormal) |

## Optional governance / data-quality columns (calibrate degradation sensitivity)

| Column                       | Type  | Unit        | Purpose                                 |
| ---------------------------- | ----- | ----------- | --------------------------------------- |
| `schema_failures_count`      | int   | events/day  | Calibration of data-quality degradation  |
| `timestamp_drift_rate`       | float | 0..1        | Fraction of drift-affected records      |
| `reconciliation_defects_rate`| float | 0..1        | Fraction of defective records           |
| `missingness_rate`           | float | 0..1        | Fraction of missing fields              |

## Scenario benefit columns (replace assumed fixed/demand-linked split)

For each investment scenario under study, provide per-period:

| Column                      | Type  | Unit  | Purpose                                |
| --------------------------- | ----- | ----- | -------------------------------------- |
| `investment_cost`           | float | USD   | One-time capital outlay                |
| `labor_savings`             | float | USD/yr| Fixed benefit (volume-invariant)       |
| `reserved_capacity_savings` | float | USD/yr| Fixed benefit                          |
| `risk_avoidance_savings`    | float | USD/yr| Fixed benefit                          |
| `dispute_recovery_amount`   | float | USD/yr| Demand-linked benefit                 |
| `compute_efficiency_savings`| float | USD/yr| Demand-linked benefit                 |

## Capital parameters (from finance stakeholders)

| Parameter | Source                |
| --------- | --------------------- |
| WACC       | Finance / treasury     |
| Horizon    | Capital governance     |
| Risk tolerance (VaR level) | Finance / risk |

## Notes

- A production deployment should fit the demand-volume distribution to an
  LSTM (or comparable) demand-forecast model's prediction residuals, not to
  raw demand alone, so that forecast uncertainty propagates into the ROI
  distribution.
- When telemetry is restricted or unavailable, this schema documents exactly
  which illustrative assumption each collected field replaces.
