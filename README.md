# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Every increase in model or architectural complexity must earn its place through evidence, with one narrow finance-native exception for foundational pricing semantics.

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Pricing Composition Foundation** establishes the first finance-domain architecture. The next concrete milestone is **M1 — European Options & Black-Scholes Reference Vertical**, implemented as a specialization of M0A.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for milestone sequencing;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed and deferred quantitative conventions;
- [`docs/decisions/0001-foundational-pricing-composition.md`](docs/decisions/0001-foundational-pricing-composition.md) for the M0A architectural decision;
- [`docs/development/engineering_principles.md`](docs/development/engineering_principles.md) for engineering/collaboration rationale.

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

The conceptual starting point is

```math
\mathfrak P = (\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

while the numerical/analytic method remains separate from the financial pricing problem.

This does **not** create a universal finance framework. M0A deliberately omits generic rates, market-data, calibration, risk, portfolio, XVA, validation-study, and native-backend architecture.

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

## v0.1 direction

```text
mathematical pricing foundation
        ↓
Black-Scholes reference specialization
        ↓
independent valuation + Greeks
        ↓
delta-hedging experiments
        ↓
real option-market evidence
        ↓
smile/skew and Black-Scholes deficiencies
        ↓
Heston stochastic volatility
        ↓
independent Heston valuation methods
        ↓
calibration
        ↓
parameter recovery + stability
        ↓
out-of-sample/model-risk comparison
        ↓
profile measured bottlenecks
        ↓
targeted C++ acceleration
        ↓
portfolio-quality release
```

The project deliberately does **not** begin as a checklist of pricing, VaR, XVA, rates, and portfolio features. Later specializations should emerge only after the equity-volatility foundation is mature and real consumers justify new abstractions.

## Validation theme

The platform is expected to accumulate multiple independent forms of evidence:

- software/type/invariant correctness;
- no-arbitrage identities and bounds;
- known analytical/limiting cases;
- independent pricing methods;
- numerical convergence and stability;
- statistical Monte Carlo error analysis;
- analytic vs numerical Greeks;
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
state != stochastic law != parameters
contract != cash-flow stream
numeraire != pricing measure
pricing problem != valuation method != result
MarketSnapshot != MarketEnvironment
FinancialContract != Trade != Portfolio
calibration problem != numerical optimizer
production library != research study != presentation
```

The ordinary two-consumer extraction rule still governs non-foundational application abstractions. ADR 0001 is the narrow exception for asset-pricing semantics.

## Python/C++ direction

Python owns reference financial semantics, research orchestration, calibration, validation, and market-data workflows.

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
- Greeks or delta hedging;
- live market-data ingestion or implied-volatility surfaces;
- generic calibration/risk/validation hierarchy;
- trade/portfolio/VaR/XVA framework;
- Heston;
- generic experiment engine;
- C++ backend abstraction.

Those capabilities should specialize or consume the M0A core only when their milestones provide real quantitative pressure.
