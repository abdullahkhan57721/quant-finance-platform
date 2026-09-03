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
5. `docs/quantitative_conventions.md` when quantitative assumptions or units matter;
6. `docs/development/engineering_principles.md` when workflow/design rationale matters;
7. relevant ADRs under `docs/decisions/`;
8. the relevant GitHub Issue in full;
9. the current implementation and tests;
10. current open PRs, recovery checkpoint, and CI status.

Executable repository truth wins over prose when they conflict: current `main`, tests, and protected CI are authoritative for actual behavior.

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

Use the repository implementation Issue template for substantial work. Capture the goal, scope boundaries, quantitative assumptions, ownership/mutability semantics, likely wrong interpretations, acceptance criteria, automated verification, and manual verification before architecture-sensitive implementation begins.

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

Out-of-scope discoveries normally become follow-up Issues rather than silent expansion of the active work unit.

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

## Ownership, mutability, and configuration

Make ownership and mutability explicit at consequential boundaries.

Prefer immutable committed inputs/results where practical. Keep mutable optimizer state, caches, work buffers, and orchestration local to the implementation that owns them.

Do not let UI/notebook state become a core quantitative API. Normalize external or interactive inputs into typed production-library inputs before valuation, calibration, risk, or validation logic consumes them.

Structural validity and implementation capability are distinct. A financially meaningful object does not imply that every numerical method supports it.

## Quantitative conventions

`docs/quantitative_conventions.md` is the authority for project-wide quantitative representation decisions.

Do not silently choose or reinterpret day count, compounding, rate units, volatility units, dividend/carry representation, calendars, Greek units/signs, or similar conventions inside an implementation when the choice crosses a public boundary.

If a convention is intentionally undecided, keep it explicit/local and update the convention register when a real consumer justifies a project-wide decision.

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

Formula implementations should be traceable to a source or derivation, notation mapping, assumptions, limiting cases, and tests once mathematical model code exists.

## Reproducibility and RNG

- Do not use hidden global RNG state in stochastic APIs.
- Prefer explicitly owned generators/configuration.
- Studies should be able to record seed/RNG information, numerical configuration, input provenance, and code version.
- Do not promise identical Python/C++ random streams from equal seeds.
- When strict cross-language kernel parity is needed, feed shared pre-generated random inputs to both implementations.
- Core tests must not depend on live market-data services.

## Performance policy

Profile before optimizing.

Benchmark the layer actually being claimed: pricing kernel, Monte Carlo engine, calibration loop, portfolio/risk aggregation, and end-to-end research workflow are different workloads.

Prefer reproducible workloads and repeated-run medians. Hosted CI wall-clock timing is noisy; use structural evidence such as valuation counts, objective evaluations, paths, factorizations, or characteristic-function evaluations when it better captures the optimization.

Prefer algorithmic improvements, elimination of repeated work, allocation/data-layout improvements, and clearer numerical formulations before language changes.

Reject minor speedups that materially damage readability, auditability, or numerical trustworthiness.

## Python/C++ direction

Python is the correctness/reference implementation and owns high-level financial semantics, research orchestration, validation, calibration workflows, and market-data handling.

C++ should be introduced only after profiling identifies a measured numerical hotspot worth accelerating. Do not create a fake backend abstraction before there are two real implementations.

When native acceleration arrives, keep the binding boundary narrow: domain objects are normalized in Python, numerical primitives cross the boundary, and results return to Python-owned result/validation structures.

Preserve the readable Python reference and add parity/conformance evidence for the native implementation.

## Agent work allocation

Use ChatGPT primarily for:

- architecture and public-contract design;
- quantitative/modeling tradeoffs;
- consequential convention decisions;
- milestone/roadmap sequencing;
- tightly scoped architecture-sensitive implementation;
- independent PR review and merge decisions.

Use Codex selectively for execution-heavy work behind settled interfaces, such as:

- broad repetitive migrations;
- analogous test matrices;
- mechanical documentation/code updates;
- validation/debug cycles;
- independently parallelizable implementation whose shared contracts are already settled.

Do not delegate architecture-sensitive work merely because it is large. Settle consequential contracts first and encode them in the Issue.

Parallelize only when shared interfaces are stable enough that branches are unlikely to redefine the same public concepts.

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

Keep information at the lifetime appropriate to it:

- durable operating rules → `AGENTS.md`;
- current architecture → architecture docs;
- consequential decision rationale → ADRs;
- concise project orientation → `current_state.md`;
- milestone direction → `roadmap.md`;
- exact implementation scope → Issue;
- in-progress/recovery state → PR;
- behavior → code/tests;
- enforced quality → CI;
- history → Git;
- explanatory rationale → `engineering_principles.md` and learning material.

Update `current_state.md` and `roadmap.md` only when project truth materially changes. Do not churn them for trivial implementation details or volatile SHAs/CI state.

Use architecture documents/ADRs only for durable consequential decisions. Avoid documenting speculative designs as if they were committed architecture. Supersede an ADR instead of rewriting its historical decision.

Update documentation in the same PR when public contracts, quantitative conventions, or durable architecture change.

## Quality gate

For ordinary changes, install development dependencies and run:

```text
./scripts/check_all
```

The canonical gate currently covers:

```text
complexipy cognitive-complexity threshold (production package; maximum 15)
ruff check
ruff format --check
pyright
pytest
```

Use `./scripts/complexity` (or `bash ./scripts/complexity` when executable mode is unavailable) to run the complexity gate independently. Use `./scripts/fix` for supported Ruff auto-fixes and formatting.

Do not weaken quality guards merely to merge. Add new guards only when real code or architecture gives them something meaningful to enforce.

Performance changes additionally require profiling/benchmark evidence. Quantitative-model changes additionally require the financial/numerical validation appropriate to that model.
