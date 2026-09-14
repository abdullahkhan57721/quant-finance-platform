# Quantitative Finance Research & Validation Platform

A **validation-first equity-derivatives research and model-risk platform** for pricing, inference, hedging, calibration, empirical validation, and measured performance engineering.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

## 30-second overview

| Question | Answer |
| --- | --- |
| **What is this?** | A Python quantitative-finance platform plus a native **PySide6 / Qt Quick** research workbench, built around reproducible model evidence rather than isolated formula demos. |
| **What quantitative problems does it solve?** | European-option pricing, Greeks, dynamic delta hedging, implied-volatility inversion, Heston valuation, Heston calibration/identifiability, Black-Scholes vs Heston validation, and performance analysis. |
| **What makes it technically interesting?** | Independent valuation methods, explicit **Problem → Method → Result/Evidence** boundaries, observation provenance, no-leakage held-out validation, calibration-conditioning diagnostics, and profiling-driven optimization instead of speculative native code. |
| **What empirical result did it produce?** | On a pinned **January 4, 2023 SPX/SPXW** sample with a predeclared **10-train / 4-held-out** split, Heston reduced held-out price RMSE from **8.412 to 0.671** and relative MAE from **8.27% to 0.66%** versus a fairly fitted one-volatility Black-Scholes benchmark. This is a same-date cross-sectional result, not a claim of temporal forecasting skill. |
| **What can I run / see?** | A native desktop workbench for pricing, Greeks, hedging, implied volatility, Heston calibration, validation/model risk, and measured performance evidence; plus reproducible scripts, tests, and committed evidence artifacts. |

## Run the native workbench

```bash
python -m pip install -e ".[desktop]"
python -m qf_platform.desktop.main
```

Run the repository quality gate with:

```bash
./scripts/check_all
```

The committed evidence includes the [SPX Black-Scholes vs Heston held-out comparison](docs/evidence/m7_spx_bs_vs_heston_validation_reference.json) and the [measured performance study](docs/evidence/m8_performance_reference.json). M8 improved representative heavy workloads by **4.61×–27.38×** through Python/NumPy and algorithmic changes; after profiling, a C++ kernel was deliberately **not** retained for v0.1 because the remaining absolute cost did not justify the added binding, packaging, and parity surface.

## Status

**M0–M8 and UI1–UI5 are complete. M9 — Portfolio-Quality v0.1 Release is next.**

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
→ v0.1 release
```

## Deep documentation

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
