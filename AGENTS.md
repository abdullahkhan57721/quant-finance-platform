# AGENTS.md

## Purpose

This repository contains the **Quantitative Finance Research & Validation Platform**.

The platform is validation-first. Its first specialization is **equity derivatives and volatility modeling**. The project should demonstrate quantitative-finance knowledge, mathematical and numerical reasoning, reproducible research, model validation, empirical analysis, and professional Python/C++ engineering.

Two governing principles:

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Every increase in model or architectural complexity must earn its place through evidence.

## Source of truth

Repository state takes precedence over conversation memory.

Before making consequential changes, orient in this order:

1. this `AGENTS.md`;
2. `docs/development/current_state.md`;
3. `docs/development/roadmap.md`;
4. `docs/architecture/index.md`;
5. the relevant GitHub Issue in full;
6. the current implementation and tests;
7. current open PRs and CI status.

Do not rely on an old chat summary when the repository can answer the question.

## Development workflow

Use the normal durable-work-unit flow:

```text
roadmap milestone
      ↓
GitHub Issue
      ↓
branch
      ↓
implementation
      ↓
PR opened early as recovery checkpoint
      ↓
tests / validation / CI
      ↓
exact-head review
      ↓
squash merge
      ↓
verify main
```

Normally:

```text
1 Issue → 1 branch → 1 PR
```

A long ChatGPT conversation is not a reason to create another Issue. Continue the same work unit in a fresh chat while preserving the Issue, branch, and normally the PR.

Maintain a PR recovery checkpoint when work spans multiple sessions:

```text
Implemented:
Remaining:
Current blocker:
Last verified head:
Last CI result:
Next action:
```

## Architecture rules

Transfer software-design judgment from prior projects, not their domain abstractions.

Prefer explicit composition and concrete implementations until real consumers expose stable shared responsibilities.

Extraction rule:

```text
one consumer
→ keep concrete/local

two real consumers
→ compare semantics

same responsibility
→ consider extracting shared abstraction

different responsibility
→ keep separate
```

Do not create abstractions merely because future use can be imagined.

Protect these conceptual distinctions:

```text
MarketSnapshot != MarketEnvironment
Instrument != Trade != Portfolio
MarketModel != ValuationMethod
MarketModel != CalibrationMethod
MarketModel != RiskMeasure
MarketModel != ValidationMethod
financial model != numerical method
model structure != model parameters
calibration problem != numerical optimizer
configuration/request != immutable result
production library != research study != presentation
Python financial semantics != accelerated numerical execution
```

Do **not** introduce a universal `FinancialModel` abstraction.

Do not create speculative empty packages for future Heston, XVA, rates, market risk, rough volatility, or native backends.

## Dependency guidance

- Instruments must not depend on valuation implementations.
- Market observations/environments must not depend on instruments.
- Model structures must not own calibration orchestration.
- Valuation may combine instruments, market environments, and model information.
- Calibration, risk, and validation may consume valuation capabilities when required.
- Research/studies orchestrate public library APIs rather than hiding production logic in notebooks.
- UI/presentation must not own core quantitative semantics.
- Numerical infrastructure must not contain finance-domain policy.

These are guardrails, not permission to create every named layer before it has consumers.

## Validation philosophy

Correctness requires multiple forms of evidence where applicable:

- software correctness;
- theoretical/no-arbitrage correctness;
- numerical convergence and stability;
- stochastic/statistical correctness;
- cross-method validation;
- calibration and parameter-recovery evidence;
- empirical/out-of-sample evidence;
- model-risk/sensitivity analysis;
- Python/C++ parity;
- performance evidence.

Independent implementations agreeing with each other are useful evidence, but not sufficient by themselves if both could share the same conceptual error.

Every meaningful numerical tolerance should have an explicit reason.

## Reproducibility and RNG

- Do not use hidden global RNG state in stochastic APIs.
- Prefer explicitly owned generators/configuration.
- Studies should be able to record seed/RNG information, numerical configuration, input provenance, and code version.
- Do not promise identical Python/C++ random streams from equal seeds.
- When strict cross-language kernel parity is needed, feed shared pre-generated random inputs to both implementations.

## Python/C++ direction

Python is the correctness/reference implementation and owns high-level financial semantics, research orchestration, validation, calibration workflows, and market-data handling.

C++ should be introduced only after profiling identifies a measured numerical hotspot worth accelerating. Do not create a fake backend abstraction before there are two real implementations.

When native acceleration arrives, keep the binding boundary narrow: domain objects are normalized in Python, numerical primitives cross the boundary, and results return to Python-owned result/validation structures.

## Research direction

Classical foundations come before frontier-model novelty.

The intended v0.1 progression is:

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
Heston
        ↓
independent Heston valuation methods
        ↓
calibration
        ↓
parameter recovery + stability
        ↓
out-of-sample/model-risk comparison
        ↓
profile actual bottlenecks
        ↓
targeted C++ acceleration
```

A modern research-paper replication belongs after the classical platform is mature. Rough volatility is a promising direction, not a pre-committed implementation target.

## Documentation discipline

Update `current_state.md` and `roadmap.md` only when project truth materially changes. Do not churn them for trivial implementation details.

Use architecture documents/ADRs only for durable consequential decisions. Avoid documenting speculative designs as if they were committed architecture.

## Quality gate

For ordinary changes, run the repository’s configured core checks before merge:

```text
ruff check
ruff format --check
pyright
pytest
```

Performance changes additionally require profiling/benchmark evidence. Quantitative-model changes additionally require the financial/numerical validation appropriate to that model.
