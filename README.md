# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, calibrating, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Foundational mathematical distinctions may be explicit from the outset; operational frameworks still need concrete behavior and evidence.

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

**M2 — Independent Valuation and Sensitivity/Greeks is complete.** M2 adds CRR/binomial and Monte Carlo valuation over the same M1 financial problem, explicit Monte Carlo sampling uncertainty, and the first concrete sensitivity Problem → Method → Result family with analytic and finite-difference Greeks.

**M3 — Dynamic Hedging / Control is complete.** M3 adds exact-transition model-generated GBM paths, a Delta policy that consumes M2 sensitivity, explicit stock/cash self-financing accounting, replication-error evidence, rebalance-frequency and volatility-misspecification studies, and optional proportional transaction costs without creating a generic control/portfolio framework.

**M4 — Market Evidence / Inverse Problems is complete.** M4 adds provenance-bearing raw option/underlying observations, explicit quote normalization, Black-Scholes implied-volatility inversion as the first concrete inverse problem, conditioning/static-quote diagnostics, deterministic CI fixtures, and pinned SPX empirical evidence showing strike skew and maturity dependence.

**M5 — Heston Model and Independent Valuation is complete.** M5 adds explicit stochastic-volatility state/law/parameter semantics, deterministic characteristic-function/Fourier valuation, independent full-truncation Euler Monte Carlo valuation, exact deterministic-variance boundary handling, method-specific numerical evidence, and cross-method/theoretical validation.

**M6 — Heston Calibration / Inverse Problem is complete.** M6 adds explicit price-space calibration targets and objective/weighting semantics, bounded five-coordinate Heston calibration with a separate SciPy least-squares method, synthetic truth recovery, multiple-start and perturbation evidence, local Jacobian identifiability diagnostics, and a provenance-preserving SPX calibration workflow. M4 and M6 together do **not** yet justify a universal runtime inverse/optimizer framework.

**M7 — Empirical Validation, Model Risk, and Black-Scholes vs Heston Comparison is next.**

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for milestone sequencing;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed, local, and deferred quantitative conventions;
- [`docs/models/black_scholes.md`](docs/models/black_scholes.md) for M1 formula provenance and reference evidence;
- [`docs/models/m2_numerical_methods_and_sensitivities.md`](docs/models/m2_numerical_methods_and_sensitivities.md) for M2 numerical methods, Greeks, uncertainty, and error taxonomy;
- [`docs/models/m3_dynamic_delta_hedging.md`](docs/models/m3_dynamic_delta_hedging.md) for M3 path, policy, accounting, replication, and misspecification evidence;
- [`docs/models/m4_market_evidence_and_implied_volatility.md`](docs/models/m4_market_evidence_and_implied_volatility.md) for M4 observation, normalization, scalar inverse-problem, conditioning, and empirical-evidence semantics;
- [`docs/models/m5_heston_stochastic_volatility.md`](docs/models/m5_heston_stochastic_volatility.md) for M5 Heston dynamics, Fourier/Monte Carlo method provenance, numerical conventions, and validation evidence;
- [`docs/models/m6_heston_calibration.md`](docs/models/m6_heston_calibration.md) for M6 objective/weighting, parameter recovery, optimizer separation, identifiability, and market-calibration evidence;
- [`docs/evidence/m4_spx_implied_volatility_evidence.json`](docs/evidence/m4_spx_implied_volatility_evidence.json) and [`docs/evidence/m6_spx_heston_calibration_reference.json`](docs/evidence/m6_spx_heston_calibration_reference.json) for the pinned derived market-evidence artifacts;
- [`docs/decisions/0002-mathematical-problem-architecture.md`](docs/decisions/0002-mathematical-problem-architecture.md) for the current mathematical-problem doctrine; and
- [`docs/development/engineering_principles.md`](docs/development/engineering_principles.md) for engineering/collaboration rationale.

## Mathematical problem architecture

The platform is organized conceptually as:

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS

state / state space
stochastic law
model parameters
probability semantics
physical measure P
pricing measure Q^N
numeraire N
market observations + provenance
financial contracts
cash flows
quantitative conventions

        ↓

PROBLEM FAMILIES

forward / pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation

        ↓

SOLUTION METHODS

analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenario methods / tests

        ↓

SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The execution pattern is:

```text
Problem + supported Method -> specific immutable Result
```

This is a mathematical responsibility map, not a universal runtime inheritance tree.

## Pricing and sensitivity reference verticals

The production pricing composition is:

```text
state / state space / path
+
stochastic law + separate parameter values
+
financial contract → cash-flow stream
+
numeraire + pricing-measure semantics
        ↓
PricingProblem
        +
supported ValuationMethod
        ↓
ValuationResult
```

M1 specializes it with Black-Scholes and a European option. M2 keeps the same financial pricing question while varying the valuation method:

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

Sensitivity remains a separate question:

```text
BlackScholesSensitivityProblem
        ├── AnalyticBlackScholesSensitivity
        └── FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

The first specialization supports Delta, Gamma, Vega, Theta, and Rho with explicit differentiation variable, derivative order, units, scaling, sign conventions, and finite-difference cross-validation.

## M3 — dynamic hedging as the first control specialization

M3 consumes pricing and sensitivity without redefining either:

```text
Black-Scholes pricing problem
        +
exact-transition pricing-measure GBM path
        +
explicit rebalance schedule
        +
M2 analytic Delta as hedge policy input
        +
stock / money-market cash accounting
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

Evidence covers reproducibility, self-financing identities, no-lookahead behavior, rebalance-frequency effects, volatility misspecification, and transaction-cost drag.

Protect:

```text
Delta != hedge policy != realized hedge action
financial model != path generation != hedge execution
path observation grid != hedge rebalance schedule
replication error != model error by definition
```

## M4 — observed market evidence and implied-volatility inference

M4 creates the first production bridge from independently observed market data into the mathematical problem architecture:

```text
real market
    ↓
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

Raw observations retain source/timing/hash/licensing lineage and are not overwritten by normalized or modeled values. Financial feasibility is checked before root search. The root finder owns numerical search, not the financial meaning of the inverse problem. M2 analytic Vega exposes local inverse conditioning.

The pinned January 4, 2023 SPX study shows systematic downside skew and maturity dependence under explicit flat rate/carry and OTM-selection assumptions. One constant Black-Scholes volatility cannot reconcile that selected cross-section. Implied volatility remains a **model-dependent inferred parameter**, not directly observed physical volatility.

## M5 — Heston stochastic volatility and independent valuation

M5 responds to M4's empirical pressure with a richer forward model while reusing the same European-option contract and pricing architecture:

```text
HestonEquityState(spot, instantaneous variance)
+
HestonLaw
+
HestonParameters(kappa, theta, xi, rho, q)
+
existing EuropeanOption
+
existing money-market numeraire + pricing measure
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
```

`HestonEquityState` keeps current variance separate from the structural parameter values. The Feller condition is exposed as a diagnostic rather than silently over-enforced. Fourier valuation owns explicit quadrature configuration; Monte Carlo owns path/timestep/RNG configuration and full-truncation Euler. At `xi = 0`, M5 follows the exact deterministic-variance boundary and validates against independent Black-Scholes pricing.

## M6 — Heston calibration as a financial inverse problem

M6 calibrates the five financial coordinates

```text
(v0, kappa, theta, xi, rho)
```

while keeping observed/model spot, flat risk-free rate, and continuous dividend yield fixed for the first calibration consumer. `v0` remains state-like and is returned separately from a new immutable `HestonParameters` value.

The first target space is **option price**, deliberately not treated as equivalent to implied-volatility space. Calibration targets are either explicit synthetic model-generated targets or M4 `NormalizedOptionObservation` targets retaining provenance.

The problem owns the standardized price residual:

```text
(model price - target price) / residual scale
```

with two concrete policies:

```text
UNIFORM_PRICE
    residual scale = 1

BID_ASK_HALF_SPREAD
    residual scale = (ask - bid) / 2
```

The first supports truth-known synthetic recovery. The second gives observed price mismatch an explicit quote-width scale without interpreting half-spread as a statistical variance or universal likelihood.

Financial calibration bounds are explicit and distinct from broader M5 model validity, the optimizer's numerical bound mechanism, and parameter transforms. M6 uses direct bounded financial coordinates and does not impose Feller as a calibration constraint.

The numerical method is `ScipyLeastSquaresHestonCalibration`, a concrete SciPy trust-region-reflective bounded nonlinear least-squares method. It owns initial guess, tolerances, finite-difference Jacobian strategy, maximum evaluations, and mutable search state. It does **not** own the financial objective/weighting/domain semantics.

### Recovery and identifiability evidence

A deterministic 20-option surface over four maturities and five strikes is generated from known truth:

```text
v0    = 0.04
kappa = 2.0
theta = 0.04
xi    = 0.5
rho   = -0.7
q     = 0.01
```

Multiple materially different starts recover the known truth to tight numerical tolerance. Controlled target-price perturbations move the inferred coordinates while preserving a small objective.

A deliberately underdetermined three-quote slice demonstrates the key negative result: multiple starts can obtain near-zero price loss with materially different Heston estimates. Its local Jacobian is rank deficient.

```text
optimizer converged
!= uniquely identified parameters

small objective
!= trustworthy parameter estimate
```

M6 reports singular values/rank from the problem-standardized residual Jacobian after scaling parameter columns by their explicit financial-domain widths. A finite condition number is reported only for full five-column rank. This is local first-order identification evidence, not posterior uncertainty.

### SPX calibration evidence

The real workflow reuses M4's pinned January 4, 2023 SPX source lineage and selected 14 OTM-side contracts:

```text
local pinned raw CSV
→ M4 raw observations + provenance
→ M4 midpoint normalization
→ M6 Heston price targets
→ half-spread-standardized calibration
```

The three-start reference fit clusters around:

```text
v0      ≈ 0.04447
kappa   ≈ 3.2575
theta   ≈ 0.06622
xi      ≈ 0.62715
rho     ≈ -0.77937
```

with standardized sum-squared objective around `12.56`. The domain-scaled Jacobian is full rank but has condition number about `404`: stable optimizer convergence coexists with nontrivial parameter conditioning.

That result is calibration evidence—not a claim that Heston is valid or superior. M7 owns the actual model-risk comparison.

## Why there is still no generic inverse framework

M4 and M6 now provide two real inverse consumers:

```text
M4
scalar monotone Black-Scholes volatility inversion
financial feasibility + bracketing + root convergence

M6
five-coordinate noisy Heston calibration
weighted residuals + bounded nonlinear least squares + identifiability evidence
```

What is genuinely shared is the ADR-0002 conceptual split:

```text
financial inverse question
!= numerical solution method
!= immutable completed result/evidence
```

The operational responsibilities remain materially different. The repository therefore still has no universal runtime `InverseProblem`, optimizer, Bayesian, filtering, or forecasting framework.

## Validation evidence

The platform does not rely on plausible-looking prices alone. The evidence ladder now includes:

- analytical Black-Scholes benchmarks, parity, bounds, and limiting cases;
- CRR and Monte Carlo independent valuation evidence;
- analytic ↔ finite-difference Greek validation;
- dynamic-replication/accounting/no-lookahead/misspecification evidence;
- observed-market provenance, normalization, implied-volatility feasibility/conditioning, and SPX strike/maturity evidence;
- Heston Fourier convergence, deterministic-variance reduction, seeded Monte Carlo, variance-boundary diagnostics, and Fourier ↔ Monte Carlo validation;
- Heston synthetic parameter recovery from multiple starts;
- controlled calibration-target perturbation evidence;
- explicit rank-deficient low-loss non-identifiability evidence; and
- provenance-preserving SPX Heston calibration with residual and local conditioning evidence.

Keep distinct:

```text
financial model misspecification
numerical valuation error
Monte Carlo sampling error
Heston time-discretization bias
observed quote / data-quality uncertainty
implied-volatility inverse conditioning
calibration objective / weighting choice
optimizer convergence failure
calibration initialization dependence
parameter non-identifiability / ill-conditioning
calibration residual
model validity
```

## v0.1 direction

```text
M0A mathematical architecture                     complete
M1 Black-Scholes reference vertical               complete
M2 independent valuation + Greeks                 complete
M3 dynamic hedging/control                        complete
M4 market evidence + implied-vol inference        complete
M5 Heston stochastic volatility                   complete
M6 Heston calibration + identifiability           complete
M7 empirical/model-risk comparison                next
M8 profile + targeted C++ acceleration            planned
M9 portfolio-quality v0.1 release                 planned
```

## Architecture philosophy

Key protected distinctions include:

```text
financial state != market observation
raw observation != normalized observation != modeled value
state != stochastic law != parameters != calibrated estimate
contract != cash-flow stream
numeraire != pricing measure
problem != solution method
pricing problem != sensitivity problem != control problem != inverse problem
GBM/Heston stochastic law != valuation/path method
Delta sensitivity != hedge policy != realized hedge action
inverse problem != root finder / optimizer
calibration objective / weighting != optimizer configuration
financial domain constraint != optimizer bound mechanism != parameter transform
implied volatility != observed volatility
optimizer converged != model valid
FinancialContract != Trade != Portfolio
production library != research study != presentation
```

The governing rule remains:

```text
Foundational mathematical domain distinctions
may be represented explicitly from the outset.

Problem-specific software frameworks
should remain narrow and evidence-driven.

Mathematical generality
does not imply
universal operational APIs.
```

## Python/C++ direction

Python owns reference financial semantics, research/control orchestration, inference/calibration, validation, and market-data workflows.

C++ will be introduced only after M8 profiling identifies numerical hotspots worth accelerating. Python reference implementations remain the correctness authority, with numerical/statistical parity evidence across any future native boundary.

## Local development

Python 3.12+ is required.

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the canonical quality gate with:

```bash
./scripts/check_all
```

Apply supported Ruff fixes and formatting with:

```bash
./scripts/fix
```

The canonical core gate runs Ruff linting, Ruff format checking, strict Pyright, and pytest. The dedicated Desktop workflow owns PySide6/QML checks. `scipy-stubs` is a development-only typing dependency for strict checking of the SciPy-backed M6 method.

## Current non-goals

The repository intentionally still contains no production implementation of:

- generic stochastic-control, strategy, execution, trade, portfolio, VaR, or scenario frameworks;
- physical-measure M3 forecasting semantics or nonzero-dividend hedge accounting;
- generic/live market-data-provider infrastructure;
- generic quote-cleaning, staleness, or arbitrage-free surface construction/repair infrastructure;
- universal inverse/inference or optimizer framework;
- Bayesian Heston inference, filtering, or physical-measure Heston estimation;
- generic calibration weighting/loss or parameter-transform framework;
- discount/dividend curve inference from option chains;
- generic Fourier/quadrature or stochastic-simulator frameworks;
- generic experiment infrastructure; or
- a C++ backend abstraction before profiling justifies one.

Those capabilities should specialize or consume the existing mathematical architecture only when their milestones provide real quantitative pressure.
