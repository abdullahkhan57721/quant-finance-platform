# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Foundational mathematical distinctions may be explicit from the outset; operational frameworks still need concrete behavior and evidence.

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.** M1 is the first concrete financial specialization of the M0A pricing architecture. The next milestone is **M2 — Independent Valuation and Sensitivity/Greeks**.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for milestone sequencing;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed, local, and deferred quantitative conventions;
- [`docs/models/black_scholes.md`](docs/models/black_scholes.md) for M1 formula provenance, notation, assumptions, limits, and executable evidence;
- [`docs/decisions/0002-mathematical-problem-architecture.md`](docs/decisions/0002-mathematical-problem-architecture.md) for the current mathematical-problem doctrine;
- [`docs/decisions/0001-foundational-pricing-composition.md`](docs/decisions/0001-foundational-pricing-composition.md) for the historical pricing-foundation decision; and
- [`docs/development/engineering_principles.md`](docs/development/engineering_principles.md) for engineering/collaboration rationale.

## Mathematical problem architecture

M0A organizes the platform conceptually as:

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

The conceptual execution pattern is:

```text
Problem + supported Method -> specific immutable Result
```

This does **not** create universal `Problem`, `Method`, or `Result` hierarchies. The pricing family is implemented today; the other problem families receive production abstractions only when concrete milestones create real behavior.

## Mathematical pricing core

M0A makes the general asset-pricing composition explicit:

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
ValuationResult(present_value)
```

The conceptual starting point is:

```math
\mathfrak P_{\mathrm{price}}
=
(\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

while the numerical/analytic method remains separate from the financial pricing problem.

## M1 — first concrete specialization

M1 specializes that architecture as:

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

The responsibility split is deliberate:

```text
state
!= stochastic law
!= model parameter values
!= contract
!= cash flows
!= numeraire
!= pricing-measure semantics
!= valuation method
!= valuation result
```

`BlackScholesClosedForm` is therefore a valuation method for a supported pricing problem; it is not the stochastic law itself.

### M1 quantitative semantics

The first reference vertical uses:

- calendar `datetime.date` valuation/expiry semantics;
- Actual/365 Fixed model time;
- explicit modeled spot rather than forward input;
- a flat money-market numeraire with a finite continuously compounded annualized decimal rate;
- continuous proportional dividend/carry yield;
- annualized decimal volatility (`0.20` means 20%);
- explicit European call/put terminal cash flows;
- non-negative finite spot/strike domains with zero admitted as a degenerate boundary; and
- `ValuationResult.present_value` as the completed analytical pricing output.

The risk-free rate is not duplicated inside `BlackScholesParameters`: discounting is obtained from the numeraire already owned by the `PricingProblem`.

### M1 validation evidence

M1 does not rely on plausible-looking prices alone. Its tests establish:

- a published Black-Scholes benchmark;
- put-call parity;
- discounted no-arbitrage bounds;
- expiry/intrinsic behavior;
- zero-volatility deterministic valuation;
- zero-spot and zero-strike limits;
- Actual/365 Fixed leap-day semantics;
- continuous-compounding discrimination;
- continuous dividend/carry direction;
- negative-rate support;
- domain/immutability constraints; and
- explicit unsupported-problem rejection through the valuation-method support boundary.

See [`docs/models/black_scholes.md`](docs/models/black_scholes.md) for formula traceability and tolerance rationale.

## Observations vs modeled quantities

The platform preserves this boundary:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information

separately:

modeled state + stochastic law + parameters + probability semantics
```

M1's `EquityState.spot` is valuation-ready modeled state, not a provenance-bearing observed quote. Real market observations remain a later market-data concern.

## v0.1 direction

```text
mathematical problem architecture + pricing foundation   ← M0A complete
        ↓
Black-Scholes reference specialization                   ← M1 complete
        ↓
independent valuation + sensitivity/Greeks               ← M2 next
        ↓
delta-hedging / control experiments
        ↓
real option-market observations
        ↓
implied-volatility inference + smile/skew evidence
        ↓
Heston stochastic volatility
        ↓
independent Heston valuation methods
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

The project deliberately does **not** begin as a checklist of pricing, VaR, XVA, rates, and portfolio features. Later specializations should emerge only after the equity-volatility foundation is mature and real consumers justify new operational abstractions.

## Architecture philosophy

The project prefers mathematically meaningful composition over god objects and speculative universal frameworks.

Key distinctions include:

```text
financial state != market observation
state != stochastic law != parameters
contract != cash-flow stream
numeraire != pricing measure
problem != solution method
pricing problem != valuation method != result
inverse problem != optimizer / root finder
sensitivity problem != differentiation method
prediction problem != pricing problem
control problem != optimizer
risk problem != risk-measure implementation
validation problem != validation method
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

Python owns reference financial semantics, research orchestration, inference/calibration, validation, and market-data workflows.

C++ will be introduced only after profiling identifies numerical hotspots worth accelerating. The project will preserve Python correctness/reference implementations and test numerical/statistical equivalence across the native boundary.

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

- CRR/binomial or Monte Carlo valuation;
- Greeks/sensitivity production structures;
- delta-hedging/control studies;
- live market-data ingestion or implied-volatility surfaces;
- generic inverse/inference, prediction, control, risk, or validation frameworks;
- trade/portfolio/VaR/XVA infrastructure;
- Heston or calibration;
- generic experiment infrastructure; or
- a C++ backend abstraction.

Those capabilities should specialize or consume the existing mathematical architecture only when their milestones provide real quantitative pressure.
