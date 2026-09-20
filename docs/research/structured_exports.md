# Structured analyst exports

F3 exposes existing quantitative evidence as auditable XLSX, CSV, and JSON
artifacts. The export layer is downstream of the production quantitative and
application APIs; it does not price, hedge, infer, calibrate, or validate.

```text
typed quantitative result/evidence
            ↓
concrete report adapter
            ↓
limited tabular report values
            ↓
XLSX / CSV / JSON renderer
```

## Install and run

```bash
python -m pip install -e ".[reporting]"
python examples/reporting/export_reference_validation.py --output reporting_output
```

Programmatically:

```python
from qf_platform.application import (
    canonical_m8_performance_reference,
    make_ui5_reference_validation_request,
    run_ui5_validation,
)
from qf_platform.reporting import export_report, validation_model_risk_report

request = make_ui5_reference_validation_request()
analysis = run_ui5_validation(request)
report = validation_model_risk_report(
    request,
    analysis,
    performance=canonical_m8_performance_reference(),
)
paths = export_report(report, "reporting_output")
```

`paths.xlsx`, `paths.json`, and `paths.csv` are presentation artifacts.
The authoritative values remain the typed Python request/result/evidence objects
supplied to the adapter.

## Supported concrete adapters

| Adapter | Authoritative inputs | Main exported tables |
| --- | --- | --- |
| `valuation_greeks_report` | `M2WorkbenchRequest`, `M2WorkbenchAnalysis` | valuations, Greeks, CRR convergence, Monte Carlo convergence |
| `hedging_report` | `HedgeWorkbenchRequest`, `HedgeWorkbenchAnalysis` | condition summaries, path replicates, rebalance-frequency evidence |
| `market_iv_report` | `MarketWorkbenchConfig`, `MarketWorkbenchAnalysis` | raw/normalized/inferred observations, derived SPX smile, SPX provenance |
| `heston_calibration_report` | `HestonCalibrationWorkbenchRequest`, `HestonCalibrationWorkbenchAnalysis` | truth, multiple starts, residuals, conditioning |
| `validation_model_risk_report` | `UI5ValidationRequest`, `UI5ValidationAnalysis`, optional `UI5PerformanceReference` | flagship M7/M8 workbook tables described below |

These are concrete adapters, not an arbitrary-object serializer. Adding another
quantitative workflow requires an explicit adapter that chooses which
authoritative values, units, assumptions, and provenance belong in the exported
evidence.

## Tabular representation

The small shared representation is earned by all five concrete adapters:

- `ReportField`: report-level assumption/provenance scalar;
- `ReportColumn`: explicit key, display label, unit, and optional meaning;
- `ReportTable`: a rectangular table of scalar values;
- `TabularReport`: stable report identity plus metadata and named tables.

It intentionally has no formulas, expression language, dataframe semantics,
model registry, or document-layout system.

## Format semantics

### JSON

JSON uses schema identifier `qf-platform-tabular-report-v1`. Numeric values
remain numeric and are not rounded for presentation. Column units/descriptions
and report metadata are explicit.

### CSV

Each meaningful table becomes its own CSV. Column headers include units where
present. `_metadata.csv` carries report-level assumptions and provenance.

### XLSX

Each table becomes one worksheet with explicit unit-bearing headers.
`_metadata` records the report identity and report-level fields. The workbook
contains values only: no pricing, Greek, calibration, validation, or other
financial formulas are written into spreadsheet cells.

OpenPyXL is an optional reporting dependency. Base `qf_platform.reporting`
imports and CSV/JSON rendering remain usable without it.

Generated binary workbooks are not committed by default. Tests create them only
in temporary directories.

## Flagship validation workbook

The M7/M8 validation report deliberately separates:

- `summary` — bounded result statement and comparison flags;
- `training_metrics` — training metrics by model;
- `heldout_metrics` — held-out metrics by model;
- `training_contracts` and `heldout_contracts` — predeclared partition
  membership and observed targets;
- `residuals` — model residual, quote half-spread, standardized residual, and
  relative error kept distinct;
- `calibrated_parameters` — training and later full-sample stability estimates;
- `calibration_starts` — initial guesses and outcomes for each optimizer start;
- `stability` — start dispersion and train-to-full parameter movement;
- `conditioning` — rank, target count, singular values, and condition number;
- `assumptions` — day-count/design/model-risk limitations and explicit
  non-claims;
- `provenance` — source/market-date/license lineage;
- `performance` — revision-pinned M8 evidence when explicitly supplied.

The full-sample Heston calibration remains stability evidence produced after
held-out predictions were fixed; it is not allowed to feed back into held-out
pricing metrics.

## Protected distinctions

Exports preserve rather than collapse:

```text
exported cell != quantitative authority
formatted display value != raw typed value
Monte Carlo sampling error != deterministic numerical error != model error
Delta sensitivity != realized hedge action
model residual != quote width
raw observation != normalized target != inferred parameter
training evidence != held-out evidence
calibration fit != parameter identification
provenance != decorative metadata
recorded M8 timing evidence != a new benchmark run
```

The M7 report remains a same-date cross-sectional 10-training / 4-held-out
study. It does not claim temporal forecasting, historical trading
profitability, global Heston identification, or Heston hedge superiority.
