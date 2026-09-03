# Quantitative Finance Research & Validation Platform

A **validation-first quantitative-finance research platform** for implementing,
challenging, and empirically evaluating financial models.

The first specialization is **Equity Derivatives & Volatility Modeling**.

> Don’t just implement quantitative models—show how to determine whether they are
> correct, stable, useful, and trustworthy.

> Every increase in model or architectural complexity must earn its place through
> evidence.

## Status

**M1 — European Options & Black-Scholes Reference Vertical is complete.** The next
milestone is **M2 — Independent Valuation and Greeks**.

The first production finance path now represents European calls/puts, valuation-ready
spot/discount/carry inputs, explicit date/model-time semantics, Black-Scholes model
parameters, and analytical present value with theoretical validation evidence.

See:

- [`AGENTS.md`](AGENTS.md) for repository workflow and guardrails;
- [`docs/development/current_state.md`](docs/development/current_state.md) for current
  project truth;
- [`docs/development/roadmap.md`](docs/development/roadmap.md) for M0–M9;
- [`docs/architecture/index.md`](docs/architecture/index.md) for architecture and
  validation policy;
- [`docs/quantitative_conventions.md`](docs/quantitative_conventions.md) for committed,
  local, and deferred quantitative conventions;
- [`docs/models/black_scholes.md`](docs/models/black_scholes.md) for M1 formula
  provenance, notation, assumptions, bounds, limits, and executable-evidence mapping;
- [`docs/development/engineering_principles.md`](docs/development/engineering_principles.md)
  for engineering/collaboration rationale;
- [`docs/decisions/README.md`](docs/decisions/README.md) for ADR policy.

## M1 reference vertical

The first finance path is deliberately concrete:

```text
EuropeanOption
      +
MarketEnvironment
      +
BlackScholesParameters
      ↓
black_scholes_present_value
      ↓
benchmark + parity + bounds + limiting cases
```

M1 uses calendar dates, M1-local Actual/365 Fixed model time, a narrow
maturity-dependent discount-factor capability, concrete flat continuously compounded
risk-free/dividend-carry inputs, spot semantics, and annualized decimal volatility.

The analytical valuation consumes discount factors rather than naked rate scalars. It
does not require a universal finance model hierarchy, a `BlackScholesModel` wrapper, a
provenance-bearing market snapshot, or a generic valuation-result object.

## v0.1 direction

```text
Black-Scholes reference                 ← M1 complete
        ↓
independent valuation + Greeks          ← M2 next
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

The project deliberately does **not** begin as a checklist of pricing, VaR, XVA,
rates, and portfolio features. Later specializations should emerge only after the
equity-volatility foundation is mature and real consumers justify new abstractions.

## Validation theme

The platform accumulates multiple independent forms of evidence. M1 already includes:

- a published analytical benchmark;
- put-call parity;
- discounted no-arbitrage bounds;
- expiry and deterministic/degenerate limiting cases;
- explicit domain validation;
- tests that distinguish ACT/365F from plausible day-count alternatives;
- tests that distinguish continuous from simple compounding;
- continuous dividend/carry and negative-rate cases.

Later milestones add independent numerical pricing, convergence/stability, stochastic
error analysis, Greeks, hedging error, real-market diagnostics, parameter recovery,
calibration/model-risk evidence, Python/C++ parity, and measured performance evidence.

Plausible-looking prices are not sufficient validation.

## Architecture philosophy

The project prefers concrete responsibilities and explicit composition over
speculative universal frameworks.

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

A shared abstraction should normally emerge only after multiple real consumers
demonstrate the same responsibility.

## Python/C++ direction

Python owns reference financial semantics, research orchestration, calibration,
validation, and market-data workflows.

C++ will be introduced only after profiling identifies numerical hotspots worth
accelerating. The project will preserve Python correctness/reference implementations
and test numerical/statistical equivalence across the native boundary.

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

Run the cognitive-complexity gate independently with:

```bash
bash ./scripts/complexity
```

Apply supported Ruff fixes and formatting with:

```bash
./scripts/fix
```

The current gate runs Complexipy cognitive-complexity enforcement for
`src/qf_platform` with a maximum allowed complexity of 15, Ruff linting, Ruff format
checking, strict Pyright, and pytest. GitHub Actions invokes the same
`scripts/check_all` entry point.

## Current non-goals

The repository intentionally still contains no:

- binomial/CRR or Monte Carlo valuation;
- Greeks or finite-difference sensitivities;
- delta-hedging/replication study;
- live option-market ingestion, `MarketSnapshot`, or implied-volatility surface;
- generic model/pricer/calibrator/risk/validation hierarchy;
- trade/portfolio/VaR framework;
- generic experiment engine;
- Heston/calibration implementation;
- C++ backend abstraction.

Those capabilities must be earned by the later roadmap consumers rather than being
pre-created around the first analytical formula.
