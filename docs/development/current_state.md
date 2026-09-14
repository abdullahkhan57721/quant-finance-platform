# Current State

## Operational snapshot

The quantitative-finance platform has completed and repository-verified:

```text
M0, M0A, M1, M2, M3, M4, M5, M6, M7, M8
UI1, UI2, UI3, UI4, UI5
```

ADR 0002 remains the mathematical architecture authority. ADR 0003 remains the native PySide6 + Qt Quick/QML authority.

The current product frontier is:

```text
READY
P0  M9 — Portfolio-Quality v0.1 Release
```

M9 is READY because both required predecessors are MERGED:

```text
M8  MERGED
UI5 MERGED
```

Its durable execution specification is `docs/development/milestones/M9.md`.

Independent lower-priority maintenance also exists:

```text
READY / auxiliary
P2  Issue #7 — Add cognitive-complexity quality gate
```

Issue #7 is not part of the product milestone dependency chain. It may run in a separate worktree alongside M9 only if shared development-document edits are coordinated and both branches are reconciled against current `main` before exact-head validation.

At the time this orchestration migration was planned, current `main` had no open product-milestone PR. **Do not treat that sentence as durable live state**: every fresh session must search current open Issues/PRs before starting work. Live repository state overrides this snapshot.

## Execution frontier

### READY

- **M9 — Portfolio-Quality v0.1 Release**, P0.
- **Issue #7 — cognitive-complexity quality gate**, P2 auxiliary maintenance.

### ACTIVE / REVIEW

No product milestone is intentionally recorded here as ACTIVE or REVIEW. If GitHub has an open Issue/PR for M9 or another roadmap item, that live work owns the state and this section must be reconciled rather than duplicated.

### BLOCKED

No committed product milestone is currently BLOCKED.

### PAUSED / SUPERSEDED

No future product milestone is currently PAUSED or SUPERSEDED. Historical superseded work remains in Git/Issue/PR history rather than being rewritten away.

## Recommended next execution

A fresh agent should:

1. verify current `main` and open Issues/PRs;
2. verify M8 and UI5 still satisfy repository-defined `MERGED` completion;
3. if no existing M9 work unit owns the milestone, select M9 as the highest-priority READY milestone;
4. read `docs/development/milestones/M9.md`;
5. activate/reuse the M9 Issue and execute it through the normal repository workflow;
6. do not begin speculative post-v0.1 work merely because M9 is the last committed milestone.

The deterministic selection/state/worktree rules are in `docs/development/orchestration.md`.

## Important temporary constraints

M9 is a release/consolidation milestone, not a scope-expansion milestone.

Preserve these boundaries:

```text
same-date held-out pricing evidence != temporal forecasting
calibration convergence != parameter identification
better held-out Heston pricing != universal model validity
Heston pricing advantage != demonstrated Heston hedge superiority
measured Python optimization != justification for a C++ backend
```

Do not manufacture a native backend for release optics. M8 measured current representative workloads and concluded that a C++ kernel is not justified for v0.1 after Python/NumPy optimization.

Generic saved-study/fork/document infrastructure remains absent because the repository still has no authoritative persisted study/workspace identity. Signing, notarization, installers, and supported-platform guarantees are M9 release-target decisions only to the extent actual release evidence justifies them.

## Mathematical organization

The durable taxonomy remains:

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS
state / state space
stochastic law
parameters
probability / measure semantics
numeraire
market observations + provenance
contracts / cash flows
quantitative conventions
        ↓
PROBLEM FAMILIES
pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation
        ↓
METHODS
analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenarios / tests
        ↓
SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The durable execution pattern is:

```text
Problem + supported Method -> specific immutable Result / Evidence
```

Protect:

```text
financial state != market observation
raw observation != normalized observation != modeled value
state != stochastic law != parameters != calibrated estimate
contract != cash-flow stream
numeraire != pricing measure
pricing != sensitivity != control != inverse != validation
Delta sensitivity != hedge policy != realized hedge action
calibration != validation
training fit != held-out evaluation
model residual != quote width != numerical error
optimizer convergence != parameter identification != model validity
same-date holdout != temporal forecasting
Python financial semantics != accelerated numerical execution
```

## Earned quantitative capability snapshot

### Black-Scholes / M1–M2

European calls/puts, ACT/365F, flat continuously compounded money-market numeraire, Black-Scholes closed form, CRR, seeded Monte Carlo, and analytic/finite-difference Delta, Gamma, Vega, Theta, and Rho.

### Dynamic hedging / M3

Analytic Delta consumed as a hedge-policy input over exact-transition pricing-measure GBM paths with explicit rebalance schedules, stock/cash self-financing accounting, volatility misspecification, proportional transaction costs, and replication-error summaries. These are model-generated replication experiments, not historical trading backtests.

### Market evidence / M4

Provenance-bearing raw option/underlying observations, explicit midpoint normalization, Black-Scholes implied-volatility inversion with separate bisection, conditioning evidence, static quote diagnostics, and pinned January 4, 2023 SPX evidence showing strike skew and maturity dependence.

### Heston / M5–M6

Explicit Heston state/law/parameter semantics, independent Fourier and seeded full-truncation Euler Monte Carlo valuation, Feller diagnostics, exact deterministic-variance handling at `xi=0`, cross-method validation, and price-space calibration of `(v0, kappa, theta, xi, rho)` with multiple starts and local identifiability/conditioning evidence.

### Validation / M7

M7 uses a predeclared same-date cross-sectional holdout over 14 selected SPX/SPXW contracts:

```text
10 training
4 held-out evaluation
```

Representative held-out evidence:

```text
                         Black-Scholes      Heston
price RMSE                   8.412           0.671
half-spread std. RMSE       20.613           1.649
relative MAE                 8.27%            0.66%
```

Within that explicit sample and design, Heston materially improves held-out pricing metrics relative to the fairly fitted one-volatility Black-Scholes benchmark. This does not establish temporal generalization, physical-measure forecasting skill, global Heston identification, historical trading profitability, or Heston hedge superiority.

Authoritative detail: `docs/models/m7_empirical_validation_and_model_risk.md` and `docs/evidence/m7_spx_bs_vs_heston_validation_reference.json`.

### Performance / M8

M8 profiled representative M7 workloads and optimized measured Python bottlenecks before considering native acceleration.

Pinned baseline -> optimized heavy-workload evidence:

```text
Heston MC, 20k x 252                 3.3673 s -> 0.1230 s   27.38x
10-target / 3-start calibration      2.2919 s -> 0.4971 s    4.61x
14-target / 3-start calibration      3.2752 s -> 0.5454 s    6.01x
complete M7 validation study         5.4136 s -> 1.0819 s    5.00x
```

Deterministic financial parity checks pass; changed Monte Carlo RNG semantics are validated statistically rather than by equal-stream identity.

**No C++ kernel is retained in M8.** The measured post-optimization absolute cost did not justify compiler/binding/cross-platform packaging and parity surface for v0.1.

Authoritative detail: `docs/models/m8_performance_engineering.md` and `docs/evidence/m8_performance_reference.json`.

## Native Workbench through UI5

The dependency direction remains:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs + committed derived evidence
        ↓
production quantitative core
```

UI5 presents the authoritative M7 validation/model-risk evidence and the revision-pinned M8 performance/parity evidence while preserving the measured no-C++ result. Product hardening includes keyboard navigation, accessibility names, responsive layouts, explicit state boundaries, copyable M7/M8 evidence reporting, process-isolated Qt controller tests, and standalone package/build/launch proof.

Detailed authority: `docs/architecture/native_quant_workbench.md` and `docs/models/ui5_validation_model_risk_and_product_hardening.md`.

## Deliberately absent

The repository intentionally still lacks:

- a generic validation/model-risk engine;
- generic VaR/ES/scenario/portfolio infrastructure;
- physical-measure Heston filtering/forecasting;
- Bayesian Heston inference;
- a generic optimizer/inverse hierarchy;
- arbitrage-free surface construction/repair infrastructure;
- Heston dynamic-hedging evidence;
- a generic model/plugin registry;
- a generic numerical-backend registry;
- a C++ numerical kernel for current v0.1 workloads;
- a generic persisted study/workspace/fork document model; and
- unsupported signed/notarized multi-platform release guarantees.

These absences are not automatic future milestones. Post-v0.1 work must be justified and specified from repository evidence.

## Staleness and verification rule

This document describes **now** and is intentionally less detailed than the roadmap/model docs.

If it conflicts with executable/live repository truth, use this order:

```text
current main / tests / required CI
        ↓
live PR and Issue state
        ↓
AGENTS.md + durable architecture / conventions / ADRs
        ↓
this current-state snapshot
        ↓
roadmap + milestone specs
        ↓
conversation memory
```

Correct material stale state as part of the active work unit rather than relying on it blindly.
