# AGENTS.md

## Purpose

This repository contains the **Quantitative Finance Research & Validation Platform**.

The platform is validation-first. Its first specialization is **equity derivatives and volatility modeling**. The project should demonstrate quantitative-finance knowledge, mathematical and numerical reasoning, reproducible research, model validation, empirical analysis, and professional Python/C++ engineering.

Two governing principles:

> Don’t just implement quantitative models—show how to determine whether they are correct, stable, useful, and trustworthy.

> Foundational mathematical domain distinctions may be represented explicitly from the outset when their distinctness follows from the mathematics. Problem-specific software frameworks and cross-cutting operational abstractions must still earn their place through real behavior and evidence.

ADR 0002 is the current architectural authority for this doctrine. ADR 0001 remains the historical record for the pricing-specific foundation that first motivated it. ADR 0003 governs the native PySide6 + Qt Quick/QML Workbench boundary.

## Source of truth

Repository state takes precedence over conversation memory.

Before making consequential changes, orient in this order:

1. this `AGENTS.md`;
2. `docs/development/current_state.md`;
3. `docs/development/roadmap.md`;
4. `docs/development/orchestration.md` when selecting/continuing roadmap work;
5. the selected milestone specification under `docs/development/milestones/`, when one exists;
6. `docs/architecture/index.md`;
7. `docs/quantitative_conventions.md` when quantitative assumptions or units matter;
8. `docs/development/engineering_principles.md` when workflow/design rationale matters;
9. relevant ADRs under `docs/decisions/`, especially ADR 0002 for current mathematical architecture and ADR 0001 for its pricing-specific history;
10. the relevant GitHub Issue in full;
11. the current implementation and tests;
12. current open PRs, recovery checkpoint, and CI status.

Executable/live repository truth wins over prose when they conflict. Use this practical order:

```text
current main / tests / required CI
        ↓
live PR and Issue state
        ↓
AGENTS.md + durable architecture / conventions / ADRs
        ↓
current_state.md
        ↓
roadmap.md + milestone specs
        ↓
conversation context
```

Do not rely on an old chat summary when the repository can answer the question. If navigation prose is materially stale, correct it in the active work unit after establishing repository truth.

## Repository-driven roadmap orchestration

When asked to **continue development**, **execute the roadmap**, or equivalent, do not wait for a large copied milestone prompt.

Use the repository itself:

1. complete the required orientation above;
2. fetch/verify current `main` and inspect live open Issues/PRs;
3. reconcile stale prose against repository truth;
4. read the execution graph in `docs/development/roadmap.md`;
5. determine the eligible READY set using `docs/development/orchestration.md`;
6. select the highest-priority eligible milestone deterministically;
7. read that milestone's durable specification;
8. verify every dependency is actually repository-defined `MERGED` on current `main`;
9. reuse an existing active Issue/PR when it already owns the work; otherwise create the appropriate Issue;
10. create/use one branch and isolated worktree for the selected milestone by default;
11. implement only the selected milestone's intended scope;
12. validate incrementally using the repository cadence and milestone-specific evidence;
13. run required final/exact-head validation on the actual candidate head;
14. self-review the exact diff for quantitative correctness, architecture, documentation, test quality, and accidental scope expansion;
15. open/update the PR and maintain its recovery checkpoint;
16. do **not** declare the milestone `MERGED` until squash merge and required post-merge `main` verification are complete;
17. when repository truth changes, update `current_state.md`, roadmap metadata, and follow-on states in the appropriate PR;
18. reevaluate the dependency graph before selecting further work.

Milestone states are:

```text
BLOCKED  READY  ACTIVE  REVIEW  MERGED  PAUSED  SUPERSEDED
```

Their precise semantics and transition rules live in `docs/development/orchestration.md`. In particular, `MERGED` is repository-defined completion, not “implementation exists.”

### Deterministic default selection

Unless repository evidence requires a different explicit rule:

```text
eligible =
    status == READY
    AND every depends_on milestone == MERGED
    AND no active/review work unit already owns the same scope

select by:
    1. priority;
    2. roadmap order;
    3. dependency-unblocking value;
    4. lower unstable-shared-contract risk when otherwise equal.
```

If no milestone is eligible, report the concrete blockers instead of inventing work.

### Concurrency and worktrees

Independent READY milestones may run in separate branches/worktrees only when their shared contracts are stable enough to make parallel execution safe.

Do **not** parallelize milestones that:

- depend on one another;
- modify unstable shared public contracts;
- require unresolved architecture from another active milestone;
- would create avoidable high-overlap merge conflicts;
- depend on evidence that is not yet merged and verified.

`parallel_with` in the roadmap is permission to evaluate concurrency, not proof that concurrency is currently safe. Inspect live branches/PRs and file/contract overlap first.

When concurrent work exists, update/reconcile against current `main` before final validation. One milestone per branch/worktree remains the default.

### Human merge gate

Optimize for high autonomy **before merge**, not uncontrolled recursive merging:

```text
select
-> implement
-> test
-> self-review
-> PR
-> exact-head validation
-> ready-to-merge
-> human/repository merge gate
-> squash merge
-> post-merge verification
-> unlock next work
```

Do not weaken repository approval/merge protections. If a future project rule permits automated squash merging under defined conditions, document those conditions centrally before using them.

## Development workflow

Use the normal durable-work-unit flow:

```text
roadmap milestone/spec
      ↓
GitHub Issue
      ↓
branch / isolated worktree
      ↓
implementation
      ↓
PR opened early as recovery checkpoint
      ↓
tests / validation / CI
      ↓
exact-head review
      ↓
merge gate
      ↓
squash merge
      ↓
verify main
      ↓
update state / reevaluate graph
```

Normally:

```text
1 Issue → 1 branch/worktree → 1 PR
```

Use the repository implementation Issue template for substantial work. Capture the goal, scope boundaries, quantitative assumptions, ownership/mutability semantics, likely wrong interpretations, acceptance criteria, automated verification, and manual verification before architecture-sensitive implementation begins.

A milestone spec is the durable roadmap-level contract. The GitHub Issue is the activated concrete work unit. Do not duplicate all global rules into either one.

A long ChatGPT conversation is not a reason to create another Issue. Continue the same work unit in a fresh session while preserving the Issue, branch/worktree, and normally the PR.

Maintain a PR recovery checkpoint when work spans sessions:

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

The production pricing specialization remains compositional:

```math
\mathfrak P_{\mathrm{price}}
=
(\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

with theoretical valuation under the numeraire-associated pricing measure, while a concrete analytic/numerical method remains separate.

The implemented platform now has concrete pricing, sensitivity, control, inverse/inference, and validation specializations. Their shared mathematical distinctions do not imply a universal cross-family runtime hierarchy.

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

Do not create speculative empty packages for future rates, XVA, market risk, rough volatility, or native backends.

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

The durable conceptual direction is:

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

Foundational value objects and committed pricing/sensitivity/control/inference/validation result/evidence contracts should remain value-like where appropriate. Calibration produces parameter estimates/evidence rather than mutating stochastic-law identity.

Do not let UI/notebook state become a core quantitative API. Normalize external or interactive inputs into typed production-library inputs before quantitative logic consumes them.

## Quantitative conventions

`docs/quantitative_conventions.md` is the authority for project-wide quantitative representation decisions.

Do not silently choose or reinterpret day count, compounding, rate units, volatility units, dividend/carry representation, calendars, Greek units/signs, probability semantics, horizons, loss definitions, confidence levels, calibration objectives/weights, or similar conventions inside an implementation when the choice crosses a public boundary.

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
- Python/C++ parity if a native implementation actually exists;
- performance evidence.

Validation is itself a mathematical problem family, but a universal validation framework still must be earned by repeated concrete operational behavior.

Independent implementations agreeing with each other are useful evidence, but not sufficient by themselves if both could share the same conceptual error.

Every meaningful numerical tolerance should have an explicit reason.

Important formula implementations should remain traceable to a source or derivation, notation mapping, assumptions, limiting cases, and tests.

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

M8 is current evidence that C++ is **not justified for the v0.1 representative workloads** after measured Python/NumPy optimization. Do not add a native backend for optics. Reopen the question only after a materially different workload and fresh profiling justify it.

## Python/C++ direction

Python is the correctness/reference implementation and owns high-level financial semantics, research orchestration, validation, inference/calibration workflows, and market-data handling.

C++ should be introduced only after profiling identifies a measured numerical hotspot worth accelerating. Do not create a fake backend abstraction before there are two real implementations.

If native acceleration later becomes justified, keep the binding boundary narrow: domain objects are normalized in Python, numerical primitives cross the boundary, and results return to Python-owned result/validation structures.

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

## Research direction

Classical foundations come before frontier-model novelty.

The earned v0.1 progression is:

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
held-out/model-risk validation
        ↓
profile actual bottlenecks
        ↓
measured Python/algorithmic optimization
        ↓
validation-first native product hardening
        ↓
portfolio-quality v0.1 release
```

M9 is the committed release frontier. Post-v0.1 directions in the roadmap are not implementation permission until a future planning pass creates justified milestones/specs.

## Documentation discipline

Keep information at the lifetime appropriate to it:

- durable operating rules → `AGENTS.md`;
- roadmap orchestration/state semantics → `docs/development/orchestration.md`;
- current architecture → architecture docs;
- consequential decision rationale → ADRs;
- concise current operational orientation → `current_state.md`;
- milestone dependency graph/status/priority → `roadmap.md`;
- durable per-milestone execution contract → `docs/development/milestones/`;
- exact activated implementation scope → Issue;
- in-progress/recovery/exact-head state → PR;
- behavior → code/tests;
- enforced quality → CI;
- history → Git;
- explanatory rationale → `engineering_principles.md` and learning material.

Update `current_state.md` and `roadmap.md` only when project truth materially changes. Do not churn them for trivial implementation details or volatile SHAs/CI run IDs that belong in the PR.

Use architecture documents/ADRs only for durable consequential decisions. Avoid documenting speculative designs as if they were committed architecture. Supersede an ADR instead of rewriting its historical decision.

Update documentation in the same PR when public contracts, quantitative conventions, durable architecture, or roadmap truth changes.

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

Issue #7 tracks adding a cognitive-complexity guard. Do not describe it as enforced until current `main` actually contains it in the canonical gate.

Use `./scripts/fix` for supported Ruff auto-fixes and formatting.

Do not weaken quality guards merely to merge. Add new guards only when real code or architecture gives them something meaningful to enforce.

Performance changes additionally require profiling/benchmark evidence. Quantitative-model changes additionally require the financial/numerical validation appropriate to that model. Release work additionally requires the clean-install/package/launch/replay evidence claimed by its milestone spec.
