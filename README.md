# Quantitative Finance Research & Validation Platform

A **validation-first equity-derivatives research and model-risk platform** for pricing, inference, hedging, calibration, empirical validation, and measured performance engineering.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

## 30-second overview

| Question | Answer |
| --- | --- |
| **What is this?** | A multi-surface quantitative-finance research and model-risk platform: the same validated Python semantics are available through Python, Jupyter, structured XLSX/CSV/JSON exports, Dash/Plotly, and a native **PySide6 / Qt Quick** Workbench. |
| **What quantitative problems does it solve?** | European-option pricing, Greeks, dynamic delta hedging, implied-volatility inversion, Heston valuation, Heston calibration/identifiability, Black-Scholes vs Heston validation, and performance analysis. |
| **What makes it technically interesting?** | Independent valuation methods, explicit **Problem → Method → Result/Evidence** boundaries, observation provenance, no-leakage held-out validation, calibration-conditioning diagnostics, and profiling-driven optimization instead of speculative native code. |
| **What empirical result did it produce?** | On a pinned **January 4, 2023 SPX/SPXW** sample with a predeclared **10-train / 4-held-out** split, Heston reduced held-out price RMSE from **8.412 to 0.671** and relative MAE from **8.27% to 0.66%** versus a fairly fitted one-volatility Black-Scholes benchmark. This is a same-date cross-sectional result, not a claim of temporal forecasting skill. |
| **What can I run / see?** | Programmatic research scripts, three executable Jupyter studies, auditable analyst exports, a local browser analytics workbench, and a native desktop Workbench—all downstream of the same quantitative/application contracts. |

## Choose an interface

| Interface | Best for | Install | Run / verify |
| --- | --- | --- | --- |
| **Python API** | Custom programmatic research and composition | `python -m pip install .` | `python examples/research/pricing_and_greeks.py` |
| **Jupyter** | Reproducible investigation with tables and figures | `python -m pip install -e ".[research]"` | `python scripts/check_notebooks.py` or `python -m jupyterlab notebooks` |
| **XLSX / CSV / JSON** | Analyst handoff, audit, and downstream reporting | `python -m pip install -e ".[reporting]"` | `python examples/reporting/export_reference_validation.py --output reporting_output` |
| **Dash / Plotly** | Local browser analytics and model-risk review | `python -m pip install -e ".[web]"` | `python -m qf_platform.web.main` |
| **PySide6 / QML** | Native interactive research Workbench | `python -m pip install ".[desktop]"` | `python -m qf_platform.desktop.main` |

The interfaces are **siblings, not separate finance engines**. Python/domain and
application results remain authoritative; notebooks own narrative, exports own
schemas/files, Dash owns browser interaction/rendering, and Qt owns native
interaction/rendering.

See the [multi-surface architecture](docs/architecture/research_interfaces.md)
for the dependency contract, consistency checks, and clean-install CI evidence.

## Research from Python

Use the shared quantitative/application APIs without a desktop dependency:

```bash
python -m pip install .
python examples/research/pricing_and_greeks.py
```

The [Python research guide](docs/research/python_api.md) maps the public inputs,
methods and evidence for pricing/Greeks, hedging, market/IV, Heston forward,
calibration/identifiability, validation and recorded performance. Six standalone
examples exercise those APIs.

## Jupyter flagship studies

Install the research tools and execute the three output-free notebooks in memory:

```bash
python -m pip install -e ".[research]"
python scripts/check_notebooks.py
```

See [`notebooks/README.md`](notebooks/README.md) for the pricing/Greeks,
dynamic-hedging/model-risk, and SPX/Heston-validation studies plus the evidence
and non-claim boundaries they preserve.

## Analyst exports

Generate the flagship validation/model-risk evidence as XLSX, JSON, and CSV:

```bash
python -m pip install -e ".[reporting]"
python examples/reporting/export_reference_validation.py --output reporting_output
```

The [structured export guide](docs/research/structured_exports.md) documents the
concrete M2/M3/M4/M6/M7 adapters, sheet/table schemas, units, provenance, and
model-risk non-claims. Exported files are downstream evidence artifacts; Python
results remain the quantitative authority. Dash and Qt remain sibling clients of the same frontend-neutral semantics.

## Browser analytics workbench

Install the optional Dash/Plotly client and launch the local internal-analytics surface:

```bash
python -m pip install -e ".[web]"
python -m qf_platform.web.main
```

The [browser analytics guide](docs/research/web_analytics.md) documents the workspaces, launch options, evidence boundaries, and architecture. The browser workbench exposes valuation/Greeks, dynamic hedging, market/implied-volatility evidence, Heston pricing/calibration, and M7/M8 model-validation evidence through the same frontend-neutral application/presentation contracts used by Python, Jupyter, exports, and Qt. Default studies are network-free, and the web package does not import the desktop layer.

## Native desktop Workbench

Python 3.12+ is required. From a clean checkout:

```bash
python -m pip install ".[desktop]"
python -m qf_platform.desktop.main
```

The dedicated Desktop CI also proves an offscreen source launch, standalone
`pyside6-deploy` build, packaged launch, and artifact upload. See the
[native Workbench architecture](docs/architecture/native_quant_workbench.md)
for the Qt boundary and supported workflows.

Historical v0.1 packaging evidence remains available in the
[v0.1 Release Guide](docs/release/v0.1.md) and [`CHANGELOG.md`](CHANGELOG.md);
publishing or advancing a release version is not a prerequisite for continued
platform development.

The committed evidence includes the [SPX Black-Scholes vs Heston held-out comparison](docs/evidence/m7_spx_bs_vs_heston_validation_reference.json) and the [measured performance study](docs/evidence/m8_performance_reference.json). M8 improved representative heavy workloads by **4.61×–27.38×** through Python/NumPy and algorithmic changes; after profiling, a C++ kernel was deliberately **not** retained because the remaining absolute cost did not justify the added binding, packaging, and parity surface.

## Status

**M0–M9, UI1–UI5, and F1–F4 are complete. F5 multi-surface integration is in review.**

The implemented research arc is:

```text
Black-Scholes theory
→ independent valuation + Greeks
→ dynamic hedging
→ observed SPX evidence + implied volatility
→ Heston forward valuation
→ calibration + identifiability
→ predeclared held-out model comparison
→ measured performance engineering
→ native validation/model-risk workbench
→ Python / Jupyter / exports / Dash / Qt sibling interfaces
```

## Deep documentation

- [`docs/architecture/research_interfaces.md`](docs/architecture/research_interfaces.md) — multi-surface ownership, interface matrix, consistency contract, and clean-install evidence
- [`docs/architecture/native_quant_workbench.md`](docs/architecture/native_quant_workbench.md) — native Qt Workbench boundary
- [`docs/research/python_api.md`](docs/research/python_api.md) — public Python research API
- [`notebooks/README.md`](notebooks/README.md) — reproducible Jupyter studies
- [`docs/research/structured_exports.md`](docs/research/structured_exports.md) — XLSX/CSV/JSON analyst exports
- [`docs/research/web_analytics.md`](docs/research/web_analytics.md) — Dash/Plotly browser analytics
- [`docs/release/v0.1.md`](docs/release/v0.1.md) — v0.1 install, verification, demo, evidence, and distribution boundary
- [`CHANGELOG.md`](CHANGELOG.md) — v0.1 release notes
- [`AGENTS.md`](AGENTS.md) — repository workflow and guardrails
- [`docs/development/current_state.md`](docs/development/current_state.md) — current project truth
- [`docs/development/roadmap.md`](docs/development/roadmap.md) — milestone sequencing
- [`docs/architecture/index.md`](docs/architecture/index.md) — architecture and extraction rules
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) — quantitative convention register
- [`docs/decisions/0002-mathematical-problem-architecture.md`](docs/decisions/0002-mathematical-problem-architecture.md) — governing mathematical architecture

Model/evidence documents:

- [`docs/models/black_scholes.md`](docs/models/black_scholes.md)
- [`docs/models/m2_numerical_methods_and_sensitivities.md`](docs/models/m2_numerical_methods_and_sensitivities.md)
- [`docs/models/m3_dynamic_delta_hedging.md`](docs/models/m3_dynamic_delta_hedging.md)
- [`docs/models/m4_market_evidence_and_implied_volatility.md`](docs/models/m4_market_evidence_and_implied_volatility.md)
- [`docs/models/m5_heston_stochastic_volatility.md`](docs/models/m5_heston_stochastic_volatility.md)
- [`docs/models/m6_heston_calibration.md`](docs/models/m6_heston_calibration.md)
- [`docs/models/m7_empirical_validation_and_model_risk.md`](docs/models/m7_empirical_validation_and_model_risk.md)
- [`docs/models/m8_performance_engineering.md`](docs/models/m8_performance_engineering.md)
- [`docs/evidence/m4_spx_implied_volatility_evidence.json`](docs/evidence/m4_spx_implied_volatility_evidence.json)
- [`docs/evidence/m6_spx_heston_calibration_reference.json`](docs/evidence/m6_spx_heston_calibration_reference.json)
- [`docs/evidence/m7_spx_bs_vs_heston_validation_reference.json`](docs/evidence/m7_spx_bs_vs_heston_validation_reference.json)
- [`docs/evidence/m8_performance_reference.json`](docs/evidence/m8_performance_reference.json)

## Mathematical problem architecture

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS
state / state space
stochastic law
model parameters
probability / measure semantics
numeraire
market observations + provenance
financial contracts / cash flows
quantitative conventions
        ↓
PROBLEM FAMILIES
pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation
        ↓
METHODS
analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenarios / tests
        ↓
SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The execution pattern is:

```text
Problem + supported Method -> specific immutable Result / Evidence
```

This is a mathematical responsibility map, not a universal runtime inheritance tree.

## Protected distinctions

```text
financial state != market observation
raw observation != normalized observation != modeled value
state != stochastic law != parameters != calibrated estimate
contract != cash-flow stream
numeraire != pricing measure
problem != solution method
pricing != sensitivity != control != inverse != validation
GBM/Heston stochastic law != Monte Carlo/Fourier/path method
Delta sensitivity != hedge policy != realized hedge action
inverse problem != root finder / optimizer
calibration objective / weighting != optimizer configuration
financial domain != optimizer bound mechanism != parameter transform
calibration != validation
training fit != held-out evaluation
model residual != quote width != numerical error
optimizer converged != parameter identified != model valid
same-date holdout != temporal forecasting
Python financial semantics != accelerated numerical execution
production library != research study != presentation
```

## Pricing and sensitivity

The production pricing composition is:

```text
ModeledState / StateSpace
+
StochasticLaw + separate parameter values
+
FinancialContract -> CashFlowStream
+
Numeraire + PricingMeasureSemantics
        ↓
PricingProblem
        +
supported ValuationMethod
        ↓
ValuationResult or method-specific subtype
```

Black-Scholes supports closed form, CRR, and seeded Monte Carlo. Heston supports independent characteristic-function/Fourier and seeded full-truncation Euler Monte Carlo valuation.

Sensitivity remains a separate question:

```text
BlackScholesSensitivityProblem
        ├── AnalyticBlackScholesSensitivity
        └── FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

with Delta, Gamma, Vega, Theta, and Rho.

## Dynamic hedging / control

M3 composes M1/M2 behavior without redefining it:

```text
Black-Scholes pricing problem
+
exact-transition pricing-measure GBM path
+
explicit rebalance schedule
+
M2 analytic Delta as hedge-policy input
+
stock / money-market accounting
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

Evidence covers self-financing identities, no-lookahead behavior, rebalance-frequency effects, volatility misspecification, and proportional transaction costs. These are model-generated replication experiments, not historical trading backtests.

## Observed market evidence and implied volatility

M4 creates the observed-data bridge:

```text
RawOptionQuote + RawUnderlyingObservation
+ ObservationProvenance
        ↓
explicit normalization
        ↓
NormalizedOptionObservation
        ↓
BlackScholesImpliedVolatilityProblem
+ BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
```

The pinned January 4, 2023 SPX study shows systematic strike skew and maturity dependence under explicit flat rate/carry assumptions. Implied volatility remains a model-dependent inferred parameter, not observed physical volatility.

## Heston forward model and valuation

M5 responds to M4’s empirical pressure with a richer forward model:

```text
HestonEquityState(spot, instantaneous variance)
+
HestonLaw
+
HestonParameters(kappa, theta, xi, rho, q)
+
EuropeanOption
+
money-market numeraire + pricing measure
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
```

Current variance stays state-like rather than becoming a structural parameter. The Feller condition is diagnostic, not silently imposed as universal validity. Fourier quadrature and Monte Carlo timestep/RNG/full-truncation semantics remain method-owned.

## Heston calibration / inverse problem

M6 estimates:

```text
(v0, kappa, theta, xi, rho)
```

in option-price space with fixed spot/rate/q:

```text
HestonPriceCalibrationTarget(s)
+ financial bounds
+ explicit residual / weighting semantics
+ Heston Fourier forward map
        ↓
HestonCalibrationProblem
        +
ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
```

Synthetic truth recovery verifies the pipeline before noisy market fitting. Multiple-start, perturbation, rank, singular-value and condition-number evidence protect:

```text
small objective
!= unique parameters
!= trustworthy model
```

The real M6 SPX fit is stable across the three recorded starts but remains nontrivially conditioned.

## M7 — empirical validation and model risk

M7 introduces the first concrete production validation specialization:

```text
NormalizedOptionObservation(s)
+ predeclared train/evaluation partition
+ fair one-volatility Black-Scholes benchmark
+ Heston calibration domain / forward map
        ↓
BlackScholesHestonValidationProblem
        +
CrossSectionalBlackScholesHestonValidation
        ↓
BlackScholesHestonValidationEvidence
```

The 14 existing SPX observations come from one market date, so M7 explicitly uses a **same-date cross-sectional holdout**, not a temporal forecasting test:

```text
sort by (expiry, strike)
evaluation iff zero-based index % 3 == 2
```

This gives 10 training and 4 held-out contracts. Both models see exactly the same training prices and half-spread-standardized price residual scale. Black-Scholes fits one constant volatility; Heston uses three predeclared M6-style starts. Both estimates are frozen before evaluation.

A regression test changes only held-out prices and verifies that neither training fit nor held-out model predictions change.

### Reference evidence

The fair Black-Scholes fit gives approximately:

```text
sigma_BS = 0.20891
```

The selected Heston training fit is approximately:

```text
v0      = 0.04425
kappa   = 3.4968
theta   = 0.06436
xi      = 0.59557
rho     = -0.81317
```

Held-out evidence:

| Metric | Black-Scholes | Heston |
| --- | ---: | ---: |
| price RMSE | 8.412 | 0.671 |
| half-spread-standardized RMSE | 20.613 | 1.649 |
| relative MAE | 8.27% | 0.66% |

On this predeclared sample, Heston materially improves held-out pricing metrics. The training Heston Jacobian is full rank but has condition number around `425`; a post-evaluation full-sample stability fit has condition number around `404`. M6’s thin-slice rank-deficiency evidence remains a necessary counterweight to any temptation to equate good prices with globally identified parameters.

The supported conclusion is intentionally bounded:

> Under this predeclared same-date cross-sectional holdout, explicit rate/carry convention, price-space objective, and selected observations, Heston improves held-out price and half-spread-standardized RMSE relative to the one-volatility Black-Scholes benchmark. This does not establish temporal generalization or model validity; calibration conditioning, limited date/maturity coverage, numerical cost, and unsupported Heston hedging remain material limitations.

M7 does not fake a Heston hedge study: M3 paths have explicit Black-Scholes/GBM provenance and the production backend does not yet own a Heston path + Delta + hedge-accounting composition.

## Validation evidence ladder

The repository now contains evidence across:

- analytical identities, parity, bounds, and limiting cases;
- independent numerical valuation methods;
- analytic ↔ finite-difference Greeks;
- seeded stochastic uncertainty;
- dynamic replication/accounting/no-lookahead tests;
- volatility misspecification and transaction-cost studies;
- observed-market provenance and quote normalization;
- implied-volatility feasibility and conditioning;
- Heston Fourier ↔ Monte Carlo validation;
- synthetic Heston parameter recovery;
- multiple-start, perturbation, rank and condition diagnostics;
- real SPX calibration residual evidence;
- predeclared held-out Black-Scholes vs Heston pricing comparison;
- explicit model-risk limitations and unsupported-comparison boundaries; and
- profiled/reproducible before-and-after performance evidence.

Keep distinct:

```text
financial model misspecification
numerical valuation error
Monte Carlo sampling error
Heston time-discretization bias
quote / data-quality uncertainty
inverse conditioning
calibration objective / weighting choice
optimizer convergence failure
parameter non-identifiability
calibration residual
held-out validation error
model validity
performance overhead
```

## M8 — measured performance engineering

M8 profiled the exact six representative workloads frozen by M7 before changing implementation strategy. The measured hotspots were scalar Heston Monte Carlo path/RNG overhead and repeated strike-independent Heston characteristic-function work inside calibration.

Python/NumPy optimization removed those dominant costs while preserving finance ownership:

```text
Heston MC
scalar path loop + 10.08M scalar Gaussian draws
        ↓
NumPy path-state propagation + fresh local PCG64

Heston calibration
repeated scalar Fourier prices across same maturity
        ↓
stateless maturity-batched characteristic-function work
```

Same-run reference medians:

| Workload | Baseline | Optimized | Speedup |
| --- | ---: | ---: | ---: |
| Heston MC, 20k × 252 | 3.3673 s | 0.1230 s | **27.38×** |
| 10-target / 3-start calibration | 2.2919 s | 0.4971 s | **4.61×** |
| 14-target / 3-start calibration | 3.2752 s | 0.5454 s | **6.01×** |
| complete M7 validation study | 5.4136 s | 1.0819 s | **5.00×** |

Deterministic financial parity checks pass. The Monte Carlo RNG algorithm changed, so old/new evidence is statistical rather than streamwise: the reference estimates differ by about `0.853` combined standard errors.

**M8 does not add C++.** After the measured Python/algorithmic improvements, the remaining absolute latency does not justify a compiler/binding/cross-platform packaging and native-parity surface for v0.1. The scalar Python implementations remain correctness references, and no backend registry or generic compiled execution framework was introduced.

See [`docs/models/m8_performance_engineering.md`](docs/models/m8_performance_engineering.md) and [`docs/evidence/m8_performance_reference.json`](docs/evidence/m8_performance_reference.json).

## Python/C++ direction

```text
Python owns
financial semantics
market-data / inference orchestration
control / validation / research composition
presentation adapters
        ↓
profile actual workload
        ↓
optimize algorithm / Python numerical path first
        ↓
only if still justified:
narrow numerical C++ kernel
```

M8 found no v0.1 workload that still earns that final native boundary after Python/NumPy optimization. Future materially larger workloads must profile again rather than inheriting either a mandatory-C++ or never-C++ assumption.

## Native workbench direction

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs
        ↓
production quantitative core
```

The finance core remains Qt-independent. UI4 is complete and exposes authoritative M5/M6 Heston/calibration behavior. UI5 is complete and consumes authoritative M7/M8 validation, model-risk, and performance evidence while presenting M8’s measured no-C++ conclusion truthfully rather than inventing a native numerical path.

## Local development

Python 3.12+ is required.

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
./scripts/check_all
```

Apply supported Ruff fixes/formatting with:

```bash
./scripts/fix
```

The canonical core gate runs Ruff linting, Ruff formatting checks, strict Pyright, and pytest. Dedicated desktop CI owns PySide6/QML validation.

## Current non-goals

The repository intentionally still has no production implementation of:

- universal `Problem`/`Method`/`Result`, inverse, validation, risk, or optimizer frameworks;
- generic stochastic-control/strategy/trade/portfolio/VaR infrastructure;
- physical-measure Heston filtering or forecasting;
- Bayesian Heston inference;
- generic quote-cleaning or arbitrage-free surface repair;
- Heston dynamic hedging;
- generic model/plugin registries;
- generic numerical-backend registries; or
- a C++ numerical kernel for the current v0.1 representative workloads, because M8 profiling did not justify one.

Those capabilities should be added only when concrete mathematical and empirical pressure earns them.