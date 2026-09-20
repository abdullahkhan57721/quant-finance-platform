# Flagship Jupyter research studies

These three F2 notebooks are downstream research/presentation clients of the
production quantitative library. They do not own pricing formulas, hedge
accounting, calibration algorithms, validation metrics, or financial
conventions.

## Environment

From a clean checkout:

```bash
python -m pip install -e ".[research]"
```

Execute every notebook top-to-bottom without changing the committed files:

```bash
python scripts/check_notebooks.py
```

Open them interactively with:

```bash
python -m jupyterlab notebooks
```

The repository commits notebooks without execution counts or cell outputs. The
execution check runs them in memory, which keeps review diffs stable while still
making broken notebooks a CI failure.

## Studies

1. `01_pricing_numerical_methods_and_greeks.ipynb`
   - one explicit European option problem;
   - Black-Scholes analytic, CRR, and Monte Carlo valuation;
   - discretization/sampling evidence;
   - analytic and finite-difference Greeks with units.

2. `02_dynamic_delta_hedging_and_model_risk.ipynb`
   - seeded model-generated Black-Scholes paths;
   - rebalance-frequency evidence;
   - volatility misspecification;
   - proportional transaction costs;
   - terminal replication-error distributions.

3. `03_spx_heston_calibration_and_validation.ipynb`
   - raw/normalized/inferred observation semantics;
   - pinned derived SPX implied-volatility evidence;
   - Heston calibration conditioning and a rank-deficient counterexample;
   - the predeclared M7 10-training / 4-held-out comparison;
   - explicit model-risk limitations and non-claims.

## Reproducibility and evidence boundary

Default execution requires no live market service or external network access.
Stochastic configurations use explicit production-owned seeds. The SPX study
uses package-safe derived evidence and does not redistribute the pinned source
rows.

The notebooks intentionally preserve these distinctions:

```text
numerical-method agreement != market-model validity
Monte Carlo sampling error != deterministic numerical error != model error
model-generated hedging experiment != historical trading backtest
raw observation != normalized target != inferred parameter
calibration fit != parameter identification
same-date cross-sectional holdout != temporal forecasting
```

For formula provenance, assumptions, and the authoritative evidence contracts,
follow the links from each notebook into `docs/models/` and
`docs/quantitative_conventions.md`.
