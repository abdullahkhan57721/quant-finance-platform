# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, and empirically evaluating financial models.

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

**M5 — Heston Model and Independent Valuation is complete.** M5 adds an explicit stochastic-volatility state/law/parameter specialization, deterministic characteristic-function/Fourier valuation, independent full-truncation Euler Monte Carlo valuation, exact deterministic-variance boundary handling, method-specific numerical evidence, and cross-method/theoretical validation without introducing calibration or generic Fourier/simulation frameworks.

**M6 — Heston Calibration / Inverse Problem is next.** It will consume the validated M5 forward model and valuation semantics rather than redefining Heston model identity or numerical pricing responsibilities.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for milestone sequencing;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed, local, and deferred quantitative conventions;
- [`docs/models/black_scholes.md`](docs/models/black_scholes.md) for M1 formula provenance and reference evidence;
- [`docs/models/m2_numerical_methods_and_sensitivities.md`](docs/models/m2_numerical_methods_and_sensitivities.md) for M2 numerical methods, Greeks, uncertainty, and error taxonomy;
- [`docs/models/m3_dynamic_delta_hedging.md`](docs/models/m3_dynamic_delta_hedging.md) for M3 path, policy, accounting, replication, and misspecification evidence;
- [`docs/models/m4_market_evidence_and_implied_volatility.md`](docs/models/m4_market_evidence_and_implied_volatility.md) for M4 observation, normalization, inverse-problem, conditioning, and empirical-evidence semantics;
- [`docs/models/m5_heston_stochastic_volatility.md`](docs/models/m5_heston_stochastic_volatility.md) for M5 Heston dynamics, Fourier/Monte Carlo method provenance, numerical conventions, and validation evidence;
- [`docs/evidence/m4_spx_implied_volatility_evidence.json`](docs/evidence/m4_spx_implied_volatility_evidence.json) for the pinned derived SPX evidence artifact;
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

## Pricing core and Black-Scholes specialization

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

M1 specializes it with `EquityState`, `BlackScholesLaw`, `BlackScholesParameters`, `EuropeanOption`, `FlatMoneyMarketNumeraire`, `PricingMeasureSemantics`, and `BlackScholesClosedForm`.

The reference vertical uses calendar `datetime.date`, ACT/365F model time, modeled spot, a flat continuously compounded money-market rate, continuous proportional dividend/carry, annualized decimal volatility, explicit call/put rights, and non-negative finite spot/strike domains.

## M2 — independent valuation methods

M2 keeps one financial pricing question while changing the solution method:

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

`CoxRossRubinstein(steps)` distinguishes a fixed finite complete-market tree from increasing-step convergence toward the continuous Black-Scholes reference. `MonteCarloEuropeanOption(paths, seed)` owns explicit path-count/RNG configuration and returns method-specific sampling uncertainty on `MonteCarloValuationResult` without bloating the common valuation result.

## M2 — first concrete sensitivity family

Pricing and sensitivity remain separate questions:

```text
pricing:
PricingProblem + ValuationMethod -> ValuationResult

sensitivity:
BlackScholesSensitivityProblem
        +
supported sensitivity method
        ↓
BlackScholesSensitivityResult
```

The first specialization supports Delta, Gamma, Vega, Theta, and Rho with explicit differentiation variable, derivative order, units, scaling, and sign conventions. Analytic and finite-difference methods are independently cross-validated with explicit native-unit bumps.

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

The path observation grid and hedge schedule are separate. For one short European option, the hedge records explicit stock trades, cash financing, optional proportional transaction costs, terminal payoff/value, and replication error. Evidence covers reproducibility, self-financing identities, no-lookahead behavior, rebalance-frequency effects, volatility misspecification, and transaction-cost drag.

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
    ↓
strike / maturity / conditioning evidence
```

Raw observations retain source/timing/hash/licensing lineage and are not overwritten by normalized or modeled values. The first normalization policy uses a positive non-crossed bid/ask midpoint for supported European non-AM contracts and retains raw lineage plus a normalization version.

The financial inverse problem owns the observed target, Black-Scholes forward map, volatility domain, financial feasibility, and failure interpretation. The bisection method owns only the root-search procedure. No-arbitrage price bounds are checked before solving; unbracketed domains and unresolved numerical solves have distinct failure semantics.

M4 reuses M2 analytic Vega to expose local inverse conditioning. A numerically converged implied volatility can therefore still be flagged as sensitive to quote perturbations through inverse-Vega and half-spread diagnostics.

### Market evidence

Core CI uses a deterministic synthetic option fixture with deliberate strike and maturity structure. Separately, a pinned January 4, 2023 SPX research artifact derives implied volatility for approximately 30-day and 114-day expiries under explicit flat rate/carry and OTM quote-selection assumptions.

Representative inferred values are:

```text
30-day slice:
K=3720 put   ~23.03%
K=3850 put   ~21.45%
K=3900 call  ~20.65%
K=4020 call  ~19.08%

~114-day slice:
K=3720 put   ~23.12%
K=3900 call  ~21.49%
K=4075 call  ~19.63%
K=4240 call  ~18.22%
```

The systematic downside skew and maturity dependence contradict the one-constant-volatility structure as a cross-sectional description of these observed prices. Same-right midpoint slices also contain discrete convexity violations; M4 records those as data-quality evidence rather than silently repairing a surface.

Implied volatility is a **model-dependent inferred parameter**, not a directly observed physical volatility.

## M5 — Heston stochastic volatility and independent valuation

M5 answers the M4 model-pressure question with a concrete stochastic-volatility specialization while reusing the same European-option contract and the existing pricing architecture:

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

`HestonEquityState` refines `EquityState`, so a European option remains the same financial contract under Black-Scholes and Heston. The Heston parameter object owns mean-reversion speed, long-run variance, volatility of variance, Brownian correlation, and continuous dividend yield; the risk-free rate remains owned by the numeraire. The classical Feller condition is exposed as a diagnostic and is not silently treated as a universal model-validity restriction.

`HestonFourierEuropeanOption` implements deterministic characteristic-function pricing with explicit finite integration bounds, composite-Simpson resolution, stable complex square-root branch semantics, and method-specific evaluation diagnostics. `HestonMonteCarloEuropeanOption(paths, time_steps, seed)` independently uses fresh local RNG state and full-truncation Euler variance dynamics, retaining sampling uncertainty, timestep configuration, variance-scheme identity, and negative raw variance proposals as boundary-pressure evidence.

At `xi = 0`, Heston variance becomes deterministic. M5 handles that boundary exactly through integrated variance and validates the resulting price against the independent Black-Scholes closed form rather than forcing the general stochastic-volatility numerics through a singular formula.

M5 evidence includes parameter/state-domain checks, expiry and zero-spot boundaries, put-call parity, Feller-violating but numerically supported parameters, Fourier convergence/stability, exact `xi=0` reduction, seeded Monte Carlo reproducibility, variance-boundary diagnostics, and Fourier ↔ Monte Carlo agreement for a non-degenerate parameter set with tolerance tied to sampling uncertainty and discretization bias.

Protect:

```text
Heston stochastic law != Heston parameter values != current modeled state
Heston law != Fourier valuation method != Monte Carlo valuation method
Monte Carlo sampling error != Heston time-discretization bias
variance-boundary discretization effect != financial model error
Heston forward valuation != future Heston calibration
```

## Validation evidence

The platform does not rely on plausible-looking prices alone.

M1 establishes analytical benchmarks, put-call parity, bounds, limiting cases, and formula traceability. M2 adds independent valuation convergence, Monte Carlo uncertainty/scaling, and analytic ↔ finite-difference Greek validation. M3 adds dynamic-replication/accounting/no-lookahead/distributional misspecification evidence. M4 adds observation provenance, normalization rejection tests, known-volatility recovery, financial-feasibility and numerical-failure tests, low-Vega conditioning evidence, synthetic smile/term-structure regression evidence, static quote diagnostics, and reproducible derived SPX evidence. M5 adds stochastic-volatility domain semantics, Fourier quadrature/convergence evidence, exact deterministic-variance reduction, positivity-boundary diagnostics, reproducible time-discretized Monte Carlo, and independent Fourier ↔ Monte Carlo cross-validation.

The project keeps distinct:

```text
financial model / misspecification effect
Fourier truncation / quadrature error
complex-function numerical stability
Monte Carlo valuation sampling error
Heston time-discretization bias
variance-boundary discretization effect
finite-difference truncation error
finite-difference cancellation / floating-point error
discrete hedge-rebalancing error
stochastic hedge-replicate variation
transaction-cost effect
observed quote / data-quality uncertainty
inverse-problem conditioning
root-solver failure
```

## Observations vs modeled quantities

The platform preserves:

```text
real world
    ↓
raw observations + provenance
    ↓
normalization / cleaning
    ↓
problem-ready observed information

separately from

modeled state + stochastic law + parameters + probability semantics
```

M4 is the first production consumer of this distinction. `RawUnderlyingObservation` is not an `EquityState`; normalized option prices are not model prices; inferred volatility is not raw market data. M5 remains on the forward-model side of this boundary; M6 will infer new immutable Heston parameter values from explicit targets rather than mutating `HestonLaw`.

## v0.1 direction

```text
mathematical problem architecture + pricing foundation   ← M0A complete
        ↓
Black-Scholes reference specialization                   ← M1 complete
        ↓
independent valuation + sensitivity/Greeks               ← M2 complete
        ├──────────────────────────┐
        ↓                          ↓
dynamic hedging/control        market evidence /
← M3 complete                  implied-vol inference
                               ← M4 complete
        └─────────────┬────────────┘
                      ↓
Heston stochastic volatility + independent valuation     ← M5 complete
        ↓
Heston calibration / inverse problem                     ← M6 next
        ↓
parameter recovery + stability
        ↓
out-of-sample/model-risk validation
        ↓
profile measured bottlenecks
        ↓
targeted C++ acceleration
        ↓
portfolio-quality release
```

## Architecture philosophy

Key protected distinctions include:

```text
financial state != market observation
raw observation != normalized observation != modeled value
state != stochastic law != parameters
contract != cash-flow stream
numeraire != pricing measure
problem != solution method
pricing problem != sensitivity problem != control problem != inverse problem
GBM stochastic law != Monte Carlo method != path simulation
Heston law != Fourier method != Heston Monte Carlo method
Delta sensitivity != hedge policy != realized hedge action
inverse problem != optimizer / root finder
implied volatility != observed volatility
Heston forward valuation != Heston calibration
FinancialContract != Trade != Portfolio
production library != research study != presentation
```

The governing rule is:

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

C++ will be introduced only after profiling identifies numerical hotspots worth accelerating. Python reference implementations remain the correctness authority, with numerical/statistical parity evidence across any future native boundary.

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

The current gate runs Ruff linting, Ruff format checking, strict Pyright, and pytest. GitHub Actions invokes the same `scripts/check_all` entry point so local and hosted checks remain aligned.

## Current non-goals

The repository intentionally still contains no merged production implementation of:

- generic stochastic-control, strategy, execution, trade, portfolio, VaR, or scenario frameworks;
- physical-measure M3 forecasting semantics or nonzero-dividend hedge accounting;
- generic/live market-data-provider infrastructure;
- generic quote-cleaning, staleness, or arbitrage-free surface construction/repair infrastructure;
- generic inverse/inference, prediction, risk, or validation frameworks;
- Heston calibration or generic calibration/optimizer infrastructure;
- generic Fourier/quadrature or stochastic-simulator frameworks;
- discount/dividend curve inference from option chains;
- generic experiment infrastructure; or
- a C++ backend abstraction.

Those capabilities should specialize or consume the existing mathematical architecture only when their milestones provide real quantitative pressure.
