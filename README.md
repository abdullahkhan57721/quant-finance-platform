# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Foundational mathematical distinctions may be explicit from the outset; operational frameworks still need concrete behavior and evidence.

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation** establishes the platform-wide mathematical problem taxonomy and the first production pricing-domain architecture. The next concrete milestone is **M1 — European Options & Black-Scholes Reference Vertical**, implemented as a specialization of M0A.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for milestone sequencing;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed and deferred quantitative conventions;
- [`docs/decisions/0002-mathematical-problem-architecture.md`](docs/decisions/0002-mathematical-problem-architecture.md) for the current M0A architectural doctrine;
- [`docs/decisions/0001-foundational-pricing-composition.md`](docs/decisions/0001-foundational-pricing-composition.md) for the historical pricing-foundation decision;
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

## Observations vs modeled quantities

M0A also establishes this boundary:

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

Observed information must remain distinguishable from modeled and model-implied quantities.

## Next specialization: M1

M1 should approximately compose:

```text
Equity state / path
+
GBM / Black-Scholes stochastic law
+
Black-Scholes parameters
+
European call/put contract
+
money-market numeraire
+
risk-neutral pricing semantics
        ↓
PricingProblem
        +
Black-Scholes closed-form ValuationMethod
        ↓
ValuationResult
        ↓
parity + bounds + limiting cases + benchmark evidence
```

M1 still owns the concrete date/year-fraction, day-count, rate/compounding, dividend/carry, spot, volatility, option-right, and formula-traceability decisions.

M1 does not need to implement generic inference, sensitivity, prediction, control, risk, or validation frameworks merely because M0A names those mathematical families.

## v0.1 direction

```text
mathematical problem architecture + pricing foundation
        ↓
Black-Scholes reference specialization
        ↓
independent valuation + sensitivity/Greeks
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

## Validation theme

The platform is expected to accumulate multiple independent forms of evidence:

- software/type/invariant correctness;
- no-arbitrage identities and bounds;
- known analytical/limiting cases;
- independent pricing methods;
- numerical convergence and stability;
- statistical Monte Carlo error analysis;
- analytic vs numerical sensitivities/Greeks;
- delta-hedging/replication error;
- implied-volatility and real-market diagnostics;
- synthetic parameter recovery;
- calibration residuals and stability;
- out-of-sample/model-risk analysis;
- Python/C++ parity;
- profiling, runtime, memory, and scaling evidence.

Plausible-looking prices are not sufficient validation.

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
MarketSnapshot != MarketEnvironment
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

The current `main` gate runs Ruff linting, Ruff format checking, strict Pyright, and pytest. GitHub Actions invokes the same `scripts/check_all` entry point so local and hosted checks remain aligned.

## Current non-goals

The repository intentionally still contains no merged production implementation of:

- European option specialization or Black-Scholes pricing;
- CRR/binomial or Monte Carlo valuation;
- Greeks/sensitivity framework or delta hedging;
- live market-data ingestion or implied-volatility surfaces;
- generic inverse/inference, prediction, control, risk, or validation framework;
- trade/portfolio/VaR/XVA framework;
- Heston;
- generic experiment engine;
- C++ backend abstraction.

Those capabilities should specialize or consume the M0A architecture only when their milestones provide real quantitative pressure.
