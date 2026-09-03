# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing, challenging, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Every increase in model or architectural complexity must earn its place through evidence.

## Status

**M0 — Engineering Bootstrap is complete.** The next milestone is **M1 — European options and Black-Scholes reference vertical**. No finance-domain implementation has been added yet.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for M0–M9;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for project-wide quantitative convention decisions and explicitly deferred choices;
- [`docs/development/engineering_principles.md`](docs/development/engineering_principles.md) for the rationale behind the engineering/collaboration system;
- [`docs/decisions/README.md`](docs/decisions/README.md) for ADR policy.

## v0.1 direction

The first flagship release is intended to build one coherent research narrative:

```text
Black-Scholes theory
        ↓
independent valuation
        ↓
numerical cross-validation
        ↓
Greeks / replication
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

The project prefers concrete responsibilities and explicit composition over speculative universal frameworks.

Key distinctions include:

```text
MarketSnapshot != MarketEnvironment
Instrument != Trade != Portfolio
MarketModel != ValuationMethod
financial model != numerical method
model structure != model parameters
calibration problem != numerical optimizer
configuration/request != immutable result
production library != research study != presentation
```

A shared abstraction should normally emerge only after multiple real consumers demonstrate the same responsibility.

## Python/C++ direction

Python owns the reference financial semantics, research orchestration, calibration, validation, and market-data workflows.

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

Additional guards such as coverage thresholds, cognitive-complexity checks, architecture/import contracts, strict docs builds, quantitative contract suites, and benchmark harnesses are added only when real code or architecture gives them something meaningful to enforce.

## Current non-goals

The bootstrap intentionally contains no:

- Black-Scholes implementation;
- `EuropeanOption` domain type;
- generic model/pricer/calibrator/risk hierarchy;
- trade/portfolio/VaR framework;
- market-data client;
- generic experiment engine;
- C++ backend abstraction.

The first finance APIs will be introduced in M1 only when concrete Black-Scholes consumers can pressure-test their design.
