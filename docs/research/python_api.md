# Python research API

The research-facing surface is the existing `qf_platform.application` package
plus the public domain packages. Install the base package with Python 3.12+:

```bash
python -m pip install .
python examples/research/pricing_and_greeks.py
```

No desktop extra, running GUI, live market service, or repository data directory
is needed by these examples. They are source examples, not installed console
commands: keep or copy the scripts after installing the package. They can run
from any working directory using their absolute paths.

## Choose the level of composition

- **One quantitative question:** construct a domain `Problem` and concrete
  method, then call its domain evaluator. This avoids running unrelated plots
  or comparison studies.
- **An existing comparative study:** construct an application request/config
  and call its concrete `run_*` function. It returns immutable evidence assembled
  from those same domain evaluators.
- **Interactive text editing:** optionally use a `*Draft` and its normalization
  helper. Numeric Python consumers do not need to convert numbers to strings.

Use package imports such as `from qf_platform.pricing import evaluate` and
`from qf_platform.application import HestonPricingRequest`. Historical `M2`,
`UI5`, and `Workbench` names identify existing contracts; they do not require Qt.
There is no second `research` façade or renamed copy of those contracts.

## Workflow map

All entries below are public imports from the indicated package.

| Question | Domain construction / execution | Existing application study | Returned evidence |
| --- | --- | --- | --- |
| Black-Scholes / independent pricing | `pricing.PricingProblem` + `BlackScholesClosedForm`, `CoxRossRubinstein`, or `MonteCarloEuropeanOption`; `evaluate` | `BlackScholesStudyComposition`, `M2WorkbenchRequest`, `M2WorkbenchConfig`; `run_m2_workbench` | `ValuationResult` or `MonteCarloValuationResult`; study adds valuations, convergence and Greek evidence |
| Greeks | `sensitivity.BlackScholesSensitivityProblem` + analytic or finite-difference method; `evaluate_sensitivity` | Same M2 study, with explicit bump configuration | `BlackScholesSensitivityResult` retains variable, derivative order and units |
| Delta hedging | `control.BlackScholesPathSimulation`; `simulate_black_scholes_path`; `BlackScholesDeltaHedgeProblem`; `run_delta_hedge` | `HedgeWorkbenchRequest` + `HedgeWorkbenchConfig`; `run_hedge_workbench` | Path accounting, per-seed errors, replication summaries, cadence/cost/misspecification comparisons |
| Market / implied volatility | `market_data.RawOptionQuote`, `RawUnderlyingObservation`, `ObservationProvenance`; `normalize_european_option_midpoint`; `inference.BlackScholesImpliedVolatilityProblem` + `BisectionImpliedVolatility`; `infer_implied_volatility` | `run_market_workbench(quotes, underlying, MarketWorkbenchConfig)` | Raw and normalized evidence, inferred volatility/conditioning or explicit rejection/failure |
| Heston forward | `pricing.PricingProblem` with `HestonEquityState`, `HestonLaw`, `HestonParameters`; Fourier or Monte Carlo method; `evaluate` | `HestonPricingRequest`; `run_heston_pricing` | Method-specific results, Fourier resolution stability, method difference |
| Heston calibration | `inference.HestonCalibrationProblem` with targets, financial bounds, price weighting, forward method + `ScipyLeastSquaresHestonCalibration`; `calibrate_heston` | `HestonCalibrationWorkbenchRequest`; `run_heston_calibration` for fixed synthetic `recovery`/`thin` studies | Coordinates, residuals, objective, termination, local Jacobian rank/conditioning, multiple starts |
| BS versus Heston validation | `validation.BlackScholesHestonValidationProblem` + `CrossSectionalBlackScholesHestonValidation`; `validate_black_scholes_vs_heston` | `make_ui5_reference_validation_request`; `run_ui5_validation` | Training/evaluation metrics separately, contract residuals, stability, bounded conclusions |
| Recorded performance | No new benchmark runs through this accessor | `canonical_m8_performance_reference` | Immutable revision/environment-pinned M8 timings, parity and native decision |

The M2 nested evidence types are also public from `application`:
`ValuationRun`, `CRRConvergencePoint`, `MonteCarloConvergencePoint`,
`SensitivityRun`, `GreekCurvePoint`, and `GammaBumpPoint`. Their instances are
the original implementation types, not wrappers or serialized copies.

## Runnable studies

Run each independently from the checkout after installing the base package:

```bash
python examples/research/pricing_and_greeks.py
python examples/research/delta_hedging.py
python examples/research/market_and_iv.py
python examples/research/heston_forward.py
python examples/research/heston_calibration.py
python examples/research/validation_and_performance.py
```

| Example | Inputs to inspect/change | Evidence to inspect |
| --- | --- | --- |
| `pricing_and_greeks.py` | Numeric state/contract/rate/volatility; CRR steps; MC paths/seed; finite-difference bumps | Three valuations, convergence evidence, all five Greeks in native units |
| `delta_hedging.py` | Generating versus hedging volatility; proportional costs; rebalance days; base seed and replicate count | Selected path and aggregate errors; paired comparisons on common paths |
| `market_and_iv.py` | Explicit synthetic bid/ask, provenance, spot, rate/carry and root-search tolerances | Normalization/inference status, target and inferred result; separately identified committed SPX evidence |
| `heston_forward.py` | Initial variance in state; structural parameters in law parameters; independent Fourier/MC settings | Same-problem Fourier/MC results, sampling interval, resolution evidence |
| `heston_calibration.py` | Non-truth initial guess; evaluation budget; Fourier intervals; recovery versus thin sample | Truth/estimate, loss and rank/conditioning across two starts |
| `validation_and_performance.py` | Inspect the returned reference request before execution | Separate held-out/training metrics and scientific limits; historical M8 timings |

Each script exposes a small `run_example()` returning typed evidence and a
`__main__` block that prints it. These are executable teaching examples, not a
new production API. Downstream clients should import the documented package
contracts rather than importing scripts.

## Custom questions without running a whole study

The pricing example's `make_request()` shows full numeric construction. Once a
`PricingProblem` exists, select only the method you need:

```python
from qf_platform.pricing import CoxRossRubinstein, evaluate
from qf_platform.sensitivity import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    evaluate_sensitivity,
)

# problem is the typed Black-Scholes PricingProblem you constructed.
price = evaluate(problem, CoxRossRubinstein(steps=400))
delta = evaluate_sensitivity(
    BlackScholesSensitivityProblem(problem, BlackScholesSensitivity.DELTA),
    AnalyticBlackScholesSensitivity(),
)
```

The snippet illustrates an existing problem, rather than a standalone script.
Domain `supports()` checks distinguish structural validity from method support;
`evaluate` raises `UnsupportedPricingProblem` for unsupported combinations.
The study records unsupported M2 methods with `supported=False` and no result.
Do not replace unsupported/failed results with zero.

For arbitrary calibration targets, use `HestonPriceCalibrationTarget` and
`HestonCalibrationProblem` from `inference`, rather than trying to repurpose the
fixed synthetic workbench modes. For arbitrary validation data, use
`BlackScholesHestonValidationProblem` from `validation` with an explicitly
predeclared partition rather than relabeling the reference study. Keep request,
method configuration and result together in the calling research study.

## Evidence provenance and limits

| Source | What it means | What it does not mean |
| --- | --- | --- |
| F1 pricing, hedging, market and Heston examples | Explicit synthetic/model-generated inputs | New empirical evidence or historical trading performance |
| Synthetic calibration `recovery` / `thin` | Known-target recovery and non-identifiability evidence | Noisy real-market calibration or proof of globally unique parameters |
| `canonical_m4_spx_evidence`, `canonical_m6_market_reference` | Package-safe mirrors of committed derived evidence with source lineage | Redistributed raw vendor rows or fresh inference |
| `make_ui5_reference_validation_request` | Package-safe derived inputs for recomputing the M7 reference comparison | Replay of a newly downloaded/raw vendor artifact |
| `canonical_m8_performance_reference` | Previously measured M8 revisions, environment, methodology and parity | Timing of this invocation, portable latency guarantee or CI threshold |

The canonical M7 raw-artifact replay remains `scripts/m7_model_validation.py`,
using the separately obtained pinned input. See the M4/M6/M7 model documents
and `docs/evidence/` for provenance and existing mirror-to-artifact regression
checks. F1's base-install examples do not open those repository files.

Preserve the existing conventions:

- Annualized volatility and continuously compounded rates are decimals;
  date arithmetic is ACT/365F. Vega/rho are per 1.00 decimal; Theta is per
  model year. Printing a percentage is presentation, not a different API unit.
- M3 supports zero continuous dividend yield. Replication error is hedge value
  minus option payoff under explicit pricing-measure GBM paths. It is not a
  physical-measure forecast or a historical strategy backtest.
- Monte Carlo confidence intervals cover sampling uncertainty. Heston timestep
  bias, Fourier quadrature/truncation error and model error remain distinct.
- Heston initial variance is state-like. Feller is diagnostic, not a universal
  constructor constraint. Calibration convergence does not prove identification.
- M7 uses a same-date cross-sectional holdout, not temporal forecasting. Full
  sample calibration is post-evaluation stability evidence, not the held-out fit.

Constructors and evaluators preserve their existing errors. Market study
outcomes retain `NORMALIZATION_REJECTED` versus `INFERENCE_FAILED`; inspect
`diagnostic` and optional values. Calibration distinguishes invalid problems,
invalid starts and nonconvergence. Do not silently drop failures in downstream
notebooks, exports or dashboards.

## Following milestones

F2 notebooks can narrate these concrete APIs. F3 exporters should read unrounded
numeric results and retain configuration/provenance/units. F4 Dash can use the
same requests and immutable evidence, with frontend-owned session and execution
state. Existing `presentation` builders and `PlotData` are optional rendering
adapters; formatted strings are not input to financial calculations.

See [multi-surface architecture](../architecture/research_interfaces.md) for
ownership, audit rationale and dependency checks. F2/F3/F4 remain blocked until
F1 is merged and verified on main.
