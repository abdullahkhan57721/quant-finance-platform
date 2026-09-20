# Dash/Plotly analytics workbench

F4 provides a local browser analytics client for the same quantitative semantics
used by the Python API, Jupyter studies, structured exports, and native Qt
Workbench.

## Install and launch

From a clean checkout with Python 3.12+:

```bash
python -m pip install -e ".[web]"
python -m qf_platform.web.main
```

The default address is `http://127.0.0.1:8050`. Host, port, and Dash debug mode
are explicit command-line options:

```bash
python -m qf_platform.web.main --host 127.0.0.1 --port 8050
```

Automated headless verification is:

```bash
python scripts/check_web.py
```

That smoke constructs the Dash app, probes its root/layout routes, checks the
callback surface, and actively rejects any attempted Qt/Desktop import.

## Workspaces

| Workspace | Authoritative source |
| --- | --- |
| Overview | Repository-earned problem families and bounded evidence statements |
| Valuation & Greeks | M1 composition + M2 application analysis/presentation |
| Dynamic Hedging | M3 application analysis/presentation |
| Market / Implied Volatility | Package-safe M4 application/presentation evidence |
| Heston Pricing & Calibration | M5/M6 application/presentation evidence plus recorded M6 SPX reference |
| Model Validation | Recomputed package-safe M7 reference plus recorded M8 performance evidence |

Valuation/Greeks and hedging accept browser text inputs. Those strings are
normalized through the existing application Draft/request contracts before any
quantitative computation occurs. The browser does not maintain an alternate
financial-input parser or quantitative model.

Heston pricing/calibration and M7 validation are intentionally explicit actions
because they are comparatively expensive. Result regions use Dash loading states.
Errors at input/domain/method boundaries are displayed as errors rather than
being converted to zero or omitted.

## Architecture boundary

```text
Dash layout / callbacks + Plotly
             ↓
qf_platform.web.services
             +
PlotData → Plotly renderer
             ↓
qf_platform.application + qf_platform.presentation
             ↓
production quantitative core / committed evidence
```

The web client owns interaction state, navigation, HTML tables, loading/error
states, and Plotly rendering. It does **not** own pricing formulas, Greeks,
hedge accounting, implied-volatility inversion, Heston pricing/calibration,
validation metrics, or performance measurement.

Existing renderer-neutral `PlotData` is the numerical plotting handoff. F4
copies its x/y/uncertainty values into Plotly traces; it does not derive new
financial values from formatted strings.

## Evidence and non-claims

Default operation is network-free. Market and empirical calibration views use
package-safe derived evidence with recorded source lineage. Raw pinned market
source rows remain outside this repository.

The validation workspace preserves the M7 boundary:

- 10 training and 4 held-out contracts;
- one market date;
- same-date cross-sectional holdout, not temporal forecasting;
- held-out price comparison, not historical trading profitability;
- no Heston hedge-superiority claim;
- calibration fit and local rank/conditioning do not prove global parameter
  identification.

The performance panel renders revision-pinned M8 evidence. Opening or interacting
with F4 does **not** rerun the M8 benchmarks, so displayed timings are not a
performance measurement of the current browser session.

## Dependency boundary

Dash and Plotly live only in the optional `web` dependency group (and `dev`
for repository tests). Importing the quantitative/application/reporting packages
does not require web dependencies. The web package must not import PySide6,
`qf_platform.desktop`, direct quantitative implementation packages, or network
clients.

See [research and multi-surface interfaces](../architecture/research_interfaces.md)
for the cross-client architecture.
