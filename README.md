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

**M4 — Market Evidence / Inverse Problems is active.** M3 and M4 preserve separate ownership of model-generated hedge evidence versus observed-market provenance and implied-volatility inference.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for milestone sequencing;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed, local, and deferred quantitative conventions;
- [`docs/models/black_scholes.md`](docs/models/black_scholes.md) for M1 formula provenance and reference evidence;
- [`docs/models/m2_numerical_methods_and_sensitivities.md`](docs/models/m2_numerical_methods_and_sensitivities.md) for M2 numerical methods, Greeks, uncertainty, and error taxonomy;
- [`docs/models/m3_dynamic_delta_hedging.md`](docs/models/m3_dynamic_delta_hedging.md) for M3 path, policy, accounting, replication, and misspecification evidence;
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

M1 specializes it with:

```text
EquityState / EquityStateSpace
+
BlackScholesLaw + BlackScholesParameters
+
EuropeanOption → terminal CashFlowStream
+
FlatMoneyMarketNumeraire + PricingMeasureSemantics
        ↓
PricingProblem
        +
BlackScholesClosedForm
        ↓
ValuationResult(present_value)
```

The reference vertical uses calendar `datetime.date`, ACT/365F model time, modeled spot, a flat continuously compounded money-market rate, continuous proportional dividend/carry, annualized decimal volatility, explicit call/put rights, and non-negative finite spot/strike domains.

## M2 — independent valuation methods

M2 keeps one financial pricing question while changing the solution method:

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

### CRR/binomial

`CoxRossRubinstein(steps)` has explicit configuration and two deliberately distinguished interpretations:

```text
fixed finite tree
    = discrete-time complete-market model
      when 0 < p < 1

increasing steps
    = numerical approximation toward
      the continuous Black-Scholes limit
```

A valid Black-Scholes problem can therefore be unsupported by a particular coarse tree without becoming an invalid financial problem.

### Monte Carlo

`MonteCarloEuropeanOption(paths, seed)`:

- owns explicit path-count and RNG-seed configuration;
- creates fresh local RNG state for each application;
- samples the exact terminal GBM distribution for the supported European payoff;
- discounts through the same pricing problem's numeraire; and
- returns a specific immutable `MonteCarloValuationResult` containing present value, estimator standard error, a normal-approximation 95% confidence interval, path count, and seed.

The common `ValuationResult` remains narrow. Monte Carlo diagnostics are not optional fields added to every valuation result.

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

The first specialization supports:

```text
Delta = dV/dS
Gamma = d²V/dS²
Vega  = dV/dsigma
Theta = dV/dt
Rho   = dV/dr
```

M2 records the differentiation variable, derivative order, units, scaling, and sign convention explicitly. Vega and Rho are core per-`1.00` decimal sensitivities; Theta is passage of valuation time per ACT/365F model year.

Methods:

```text
AnalyticBlackScholesSensitivity
FiniteDifferenceBlackScholesSensitivity
```

Finite differences use explicit native-unit bumps rather than a project-wide magic epsilon.

## M3 — dynamic hedging as the first control specialization

M3 consumes the existing pricing and sensitivity behavior without redefining either:

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

The path observation grid and hedge schedule are separate. Adjacent Black-Scholes transitions are sampled exactly, so M3 observation dates are not silently treated as Euler timesteps.

For one short European option, the hedge starts with the hedging-model Black-Scholes present value, targets M2 Delta stock units at each explicit rebalance, and finances residual cash with the existing money-market numeraire. The path-level result records trades, cash, financing, optional proportional transaction costs, terminal payoff, terminal hedge value, and replication error separately.

The local terminal sign convention is:

```text
replication error = hedge value - option payoff
                 = hedged short-option terminal P&L
```

M3 evidence includes seeded reproducibility, accounting identities, no-lookahead behavior, 64-seed rebalance-frequency comparisons, explicit generating-versus-hedging volatility misspecification, and transaction-cost drag. Hedge execution currently requires zero continuous dividend yield rather than inventing a hidden dividend-cashflow integration convention.

Protect:

```text
Delta != hedge policy != realized hedge action
financial model != path generation != hedge execution
path observation grid != hedge rebalance schedule
replication error != model error by definition
```

## Validation evidence

The platform does not rely on plausible-looking prices alone.

M1 evidence includes:

- a published Black-Scholes benchmark;
- put-call parity;
- discounted no-arbitrage bounds;
- expiry and deterministic limiting behavior;
- ACT/365F and continuous-compounding discrimination; and
- explicit method-support boundaries.

M2 adds:

- CRR convergence toward the analytical reference;
- finite-tree no-arbitrage support evidence;
- seeded Monte Carlo reproducibility;
- statistical consistency with the analytical reference;
- approximate `O(n^-1/2)` Monte Carlo standard-error scaling;
- analytic call/put Greek reference values;
- analytic ↔ finite-difference cross-validation; and
- a multi-bump study showing finite-difference truncation versus cancellation/floating-point degradation.

M3 adds:

- exact-transition GBM path reproducibility and deterministic zero-volatility behavior;
- direct policy consumption of the M2 analytic Delta;
- self-financing stock/cash identities and explicit cost accounting;
- no-lookahead evidence;
- distributional improvement from approximately monthly to weekly to daily rebalancing on a common path-observation setup;
- volatility-misspecification evidence distinct from discrete-rebalancing error;
- stochastic replicate-integrity checks; and
- explicit rejection of unsupported dividend/carry hedge accounting.

The project keeps distinct:

```text
financial model / misspecification effect
numerical discretization / approximation error
Monte Carlo valuation sampling error
finite-difference truncation error
finite-difference cancellation / floating-point error
discrete hedge-rebalancing error
stochastic hedge-replicate variation
transaction-cost effect
```

## Observations vs modeled quantities

The platform preserves:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information

separately from

modeled state + stochastic law + parameters + probability semantics
```

M1–M3 use valuation-ready/model-generated state. M3 simulated paths are not market observations. Real quote provenance and implied-volatility inference belong to M4 rather than being smuggled into pricing or control objects.

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
                               ← M4 active
        └─────────────┬────────────┘
                      ↓
Heston stochastic volatility
        ↓
independent Heston valuation
        ↓
calibration / inverse problem
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
state != stochastic law != parameters
contract != cash-flow stream
numeraire != pricing measure
problem != solution method
pricing problem != valuation method != result
pricing problem != sensitivity problem != control problem
GBM stochastic law != Monte Carlo method != path simulation
Delta sensitivity != hedge policy != realized hedge action
inverse problem != optimizer / root finder
sensitivity problem != differentiation method
control problem != optimizer
risk problem != risk-measure implementation
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
- live market-data ingestion or option-chain provenance structures until M4 merges;
- implied-volatility inverse-problem structures until M4 merges;
- generic inverse/inference, prediction, risk, or validation frameworks;
- Heston or Heston calibration;
- generic experiment infrastructure; or
- a C++ backend abstraction.

Those capabilities should specialize or consume the existing mathematical architecture only when their milestones provide real quantitative pressure.
