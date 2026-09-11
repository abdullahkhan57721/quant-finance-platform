# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, calibrating, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

Foundational mathematical distinctions may be explicit from the outset; operational frameworks still need concrete behavior and evidence.

## Status

**M0 through M7 are complete.**

The implemented research progression is now:

```text
M0A mathematical problem architecture
        ↓
M1 Black-Scholes / European options
        ↓
M2 independent valuation + Greeks
        ├───────────────┐
        ↓               ↓
M3 dynamic hedging   M4 market evidence / implied vol
        └──────┬────────┘
               ↓
M5 Heston + independent valuation
               ↓
M6 Heston calibration + identifiability
               ↓
M7 predeclared empirical validation / model risk
               ↓
M8 profiling + targeted C++ acceleration       ← next
               ↓
M9 portfolio-quality v0.1 release
```

The native desktop workbench is a parallel downstream track. UI1–UI3 are complete; UI4 consumes the authoritative M5/M6 Heston/calibration contracts and remains separate from M7 validation semantics.

## Read first

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
- [`docs/evidence/m4_spx_implied_volatility_evidence.json`](docs/evidence/m4_spx_implied_volatility_evidence.json)
- [`docs/evidence/m6_spx_heston_calibration_reference.json`](docs/evidence/m6_spx_heston_calibration_reference.json)
- [`docs/evidence/m7_spx_bs_vs_heston_validation_reference.json`](docs/evidence/m7_spx_bs_vs_heston_validation_reference.json)

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
- predeclared held-out Black-Scholes vs Heston pricing comparison; and
- explicit model-risk limitations and unsupported-comparison boundaries.

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
```

## M8 — profile before accelerating

M7 hands M8 six representative workloads:

1. one Black-Scholes closed-form valuation;
2. one Heston Fourier valuation (`upper=100`, `intervals=256`);
3. one seeded Heston Monte Carlo valuation (`20,000` paths, `252` timesteps, seed `20260910`);
4. 10-target / 3-start Heston training calibration;
5. 14-target / 3-start Heston stability calibration; and
6. the complete M7 validation study.

M8 must profile before selecting any C++ boundary. Python reference implementations remain the correctness authority. Any native kernel must demonstrate numerical/statistical parity and measured value.

## Python/C++ direction

```text
Python owns
financial semantics
market-data / inference orchestration
control / validation / research composition
presentation adapters
        ↓
measured narrow numerical boundary
        ↓
Python reference kernel
or targeted C++ accelerated kernel
```

No generic native backend registry should precede a second real implementation.

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

The finance core remains Qt-independent. UI4 may expose authoritative M5/M6 Heston/calibration behavior but must not invent M7 validation calculations or conclusions in QML.

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
- generic model/plugin registries; or
- an unprofiled C++ backend abstraction.

Those capabilities should be added only when concrete mathematical and empirical pressure earns them.
