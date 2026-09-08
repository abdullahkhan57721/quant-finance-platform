# AGENTS.md

## Purpose

This repository contains the **Quantitative Finance Research & Validation Platform**.

The platform is validation-first. Its first specialization is **equity derivatives and volatility modeling**. The project should demonstrate quantitative-finance knowledge, mathematical and numerical reasoning, reproducible research, model validation, empirical analysis, and professional Python/C++ engineering.

Two governing principles:

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Foundational mathematical domain distinctions may be represented explicitly from the outset when their distinctness follows from the mathematics. Problem-specific software frameworks and cross-cutting operational abstractions must still earn their place through real behavior and evidence.

ADR 0002 is the current architectural authority for this doctrine. ADR 0001 remains the historical record for the pricing-specific foundation that first motivated it.

## Source of truth

Repository state takes precedence over conversation memory.

Before making consequential changes, orient in this order:

1. this `AGENTS.md`;
2. `docs/development/current_state.md`;
3. `docs/development/roadmap.md`;
4. `docs/architecture/index.md`;
5. `docs/quantitative_conventions.md` when quantitative assumptions or units matter;
6. `docs/development/engineering_principles.md` when workflow/design rationale matters;
7. relevant ADRs under `docs/decisions/`, especially ADR 0002 for current mathematical architecture and ADR 0001 for its pricing-specific history;
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

### Ordinary extraction rule

For ordinary application abstractions, prefer explicit composition and concrete implementations until real consumers expose stable shared responsibilities:

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

Do not create ordinary abstractions merely because future use can be imagined.

### Foundational mathematical architecture

ADR 0002 supersedes the pricing-only formulation of the foundational exception.

Stable mathematical distinctions may be explicit from the outset when they are part of the domain question itself rather than speculative software reuse. The platform organizes quantitative work conceptually as:

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

This taxonomy is architectural. It does **not** require a universal runtime framework.

The platform-wide conceptual execution pattern is:

```text
Problem
   +
supported Method
   ↓
specific immutable Result
```

Do not introduce universal `Problem`, `Method`, or `Result` base classes unless real consumers prove shared software behavior.

The current production pricing specialization is:

```math
\mathfrak P_{\mathrm{price}}
=
(\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

with theoretical valuation under the numeraire-associated pricing measure, while a concrete analytic/numerical method remains separate.

The pricing core currently implements:

```text
state / state space / path
stochastic law
model parameter values
financial contract
cash-flow stream
numeraire
physical- and pricing-measure semantics
PricingProblem
ValuationMethod
ValuationResult
```

The inverse, sensitivity, prediction, control, risk, and validation families remain conceptual until their milestones create real behavior. Do not create empty production classes/packages merely to mirror the taxonomy.

### Protected conceptual distinctions

Protect at least:

```text
financial state != market observation
ModeledState != StochasticLaw
StochasticLaw != model parameters
FinancialContract != CashFlowStream
Numeraire != PricingMeasureSemantics
physical measure P != pricing measure Q^N
problem != solution method
PricingProblem != ValuationMethod
ValuationMethod != ValuationResult
inverse problem != optimizer / root finder
sensitivity problem != differentiation method
prediction problem != pricing problem
control problem != optimizer
risk problem != risk-measure implementation
validation problem != validation method
MarketSnapshot != MarketEnvironment
FinancialContract != Trade != Portfolio
financial model != numerical method
configuration/request != immutable result
production library != research study != presentation
Python financial semantics != accelerated numerical execution
```

Do **not** introduce a universal `FinancialModel` abstraction or a god object that prices, calibrates, predicts, hedges, validates, and measures risk.

Do not define every stochastic law universally through only `drift()` and `diffusion()`; future jump, path-dependent, rough, or non-Markovian models may not fit that ontology cleanly.

Do not implement a generic measure-theory engine or assume an arbitrary `Measure` object can mechanically transform every model between P and Q. Dynamics/parameters under the relevant measure should remain explicit.

Do not create speculative empty packages for future Heston, inference, prediction, control, XVA, rates, market risk, rough volatility, or native backends.

Mathematical generality does not imply universal operational APIs.

## Observation and model boundary

Observed data and modeled quantities must remain distinguishable.

Real-world information flows conceptually as:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information
```

Separately, modeled semantics are composed from:

```text
modeled state
+
stochastic law
+
parameter values
+
probability semantics
```

A specific problem may combine problem-ready observed information with modeled semantics when required.

Do not silently overwrite historical observations with model-generated values. Keep raw observation, normalization, inference/calibration, and model-implied quantity responsibilities separable.

## Dependency guidance

Current foundational pricing direction:

```text
state / cash flows / measures
          ↓
contracts + stochastic-law semantics
          ↓
PricingProblem
          ↓
valuation methods/results
```

Broader conceptual direction:

```text
observations/provenance ──→ normalization / problem-ready information

modeled state / stochastic law / parameters / probability semantics
financial contracts / cash flows / numeraires / conventions
                         ↓
                 specific Problem
                         ↓
                  supported Method
                         ↓
              specific immutable Result
                         ↓
          validation / research / presentation
```

- Financial contracts must not depend on valuation implementations.
- `PricingProblem` must not depend on valuation implementations.
- Stochastic-law structure must not own calibration/inference orchestration.
- Pricing methods may combine a supported pricing problem with numerical/analytic implementation details.
- Structural validity and implementation capability are distinct; every method need not support every valid problem.
- Market observations/environments must not depend on financial contracts.
- Inference/calibration, risk, sensitivity, control, prediction, and validation may consume valuation capabilities when their concrete problem requires them.
- Validation may invoke other problem/method pairs to gather independent evidence; that does not merge their responsibilities.
- Research/studies orchestrate public library APIs rather than hiding production logic in notebooks.
- UI/presentation must not own core quantitative semantics.
- Numerical infrastructure must not contain finance-domain policy.

These are guardrails, not permission to create every named layer before it has consumers.

## Ownership, mutability, and configuration

Make ownership and mutability explicit at consequential boundaries.

Prefer immutable committed inputs/results where practical. Keep mutable optimizer state, caches, work buffers, and orchestration local to the implementation that owns them.

M0A foundational value objects and the `PricingProblem` / `ValuationResult` contracts are immutable. Concrete model-specific parameter objects should likewise be value-like where appropriate. Calibration later produces parameter values/evidence rather than mutating stochastic-law identity.

The broader Problem → Method → Result doctrine likewise treats completed result/evidence objects as committed outputs. Mutable request/configuration/solver state belongs outside those results.

Do not let UI/notebook state become a core quantitative API. Normalize external or interactive inputs into typed production-library inputs before pricing, inference, sensitivity, prediction, control, risk, or validation logic consumes them.

## Quantitative conventions

`docs/quantitative_conventions.md` is the authority for project-wide quantitative representation decisions.

Do not silently choose or reinterpret day count, compounding, rate units, volatility units, dividend/carry representation, calendars, Greek units/signs, probability semantics, horizons, loss definitions, confidence levels, or similar conventions inside an implementation when the choice crosses a public boundary.

M0A commits the mathematical responsibility taxonomy, pricing semantics, numeraire positivity, Problem → Method → Result separation, and observation/model distinction. It deliberately leaves M1-specific date/day-count/rate/carry/volatility conventions undecided until the concrete specialization requires them.

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

Validation is itself a mathematical problem family, but the production validation framework must remain concrete until real consumers justify shared behavior.

Independent implementations agreeing with each other are useful evidence, but not sufficient by themselves if both could share the same conceptual error.

Every meaningful numerical tolerance should have an explicit reason.

Formula implementations should be traceable to a source or derivation, notation mapping, assumptions, limiting cases, and tests once mathematical model code exists. M0A contains semantic mathematics but no production pricing formula; M1 owns the first full formula traceability evidence.

## Reproducibility and RNG

- Do not use hidden global RNG state in stochastic APIs.
- Prefer explicitly owned generators/configuration.
- Studies should be able to record seed/RNG information, numerical configuration, input provenance, and code version.
- Do not promise identical Python/C++ random streams from equal seeds.
- When strict cross-language kernel parity is needed, feed shared pre-generated random inputs to both implementations.
- Core tests must not depend on live market-data services.

## Performance policy

Profile before optimizing.

Benchmark the layer actually being claimed: pricing kernel, Monte Carlo engine, inference/calibration loop, control solver, portfolio/risk aggregation, and end-to-end research workflow are different workloads.

Prefer reproducible workloads and repeated-run medians. Hosted CI wall-clock timing is noisy; use structural evidence such as valuation counts, objective evaluations, paths, factorizations, or characteristic-function evaluations when it better captures the optimization.

Prefer algorithmic improvements, elimination of repeated work, allocation/data-layout improvements, and clearer numerical formulations before language changes.

Reject minor speedups that materially damage readability, auditability, or numerical trustworthiness.

## Python/C++ direction

Python is the correctness/reference implementation and owns high-level financial semantics, research orchestration, validation, inference/calibration workflows, and market-data handling.

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
mathematical problem architecture + pricing foundation
        ↓
Black-Scholes theory + specialization
        ↓
independent valuation
        ↓
numerical cross-validation
        ↓
Greeks / sensitivity + replication
        ↓
delta-hedging / control experiments
        ↓
real option-market observations
        ↓
implied-volatility inference + smile/skew evidence
        ↓
Heston
        ↓
independent Heston valuation methods
        ↓
calibration / inverse problem
        ↓
parameter recovery + stability
        ↓
out-of-sample/model-risk validation
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

The canonical gate on current `main` covers:

```text
ruff check
ruff format --check
pyright
pytest
```

Issue #7 separately tracks adding a cognitive-complexity guard now that real production code exists.

Use `./scripts/fix` for supported Ruff auto-fixes and formatting.

Do not weaken quality guards merely to merge. Add new guards only when real code or architecture gives them something meaningful to enforce.

Performance changes additionally require profiling/benchmark evidence. Quantitative-model changes additionally require the financial/numerical validation appropriate to that model.
