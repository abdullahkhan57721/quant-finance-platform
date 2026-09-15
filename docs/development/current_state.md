# Current State

## Operational snapshot

The quantitative-finance platform has completed and repository-verified:

```text
M0, M0A, M1, M2, M3, M4, M5, M6, M7, M8, M9
UI1, UI2, UI3, UI4, UI5
```

ADR 0002 remains the mathematical architecture authority. ADR 0003 remains the native PySide6 + Qt Quick/QML authority.

The planned **v0.1 product roadmap is repository-complete**. There is currently no committed READY product milestone.

M9 — Portfolio-Quality v0.1 Release is `MERGED` by the repository state model:

```text
Issue #50       CLOSED / completed
PR #51          squash-merged
verified main   6237ccad3ec27153c294a84da32350b0bd1b12c1
Core CI         success — run 34990451682
Release CI      success — run 34990451746
Desktop CI      success — run 34990451680
```

The merged-main Desktop run rebuilt the standalone Ubuntu proof, passed packaged launch smoke, and uploaded `ui1-linux-desktop-proof` with artifact id `10406156064` and SHA-256 `82f24145db4b168ab1f4c8352087e6be8805f8f5073ab46b245351aab8c42f27`.

At this snapshot GitHub has **no published Release**. Creating the `v0.1.0` tag/release is the remaining post-verification publication operation. It is not a new product milestone and must not be reported as complete until live GitHub state shows the tag/release.

Independent lower-priority maintenance remains:

```text
READY / auxiliary
P2  Issue #7 — Add cognitive-complexity quality gate
```

Issue #7 is not part of the quantitative product dependency chain.

## Execution frontier

### READY — product

None.

The committed v0.1 product roadmap ends at M9. Do not infer an M10 or silently activate a post-v0.1 specialization.

### READY — auxiliary maintenance

- **Issue #7 — cognitive-complexity quality gate**, P2.

### ACTIVE / REVIEW

None recorded after the M9 closeout. Live GitHub state overrides this sentence if new work is subsequently activated.

### BLOCKED

No committed product milestone is BLOCKED because there is no committed post-v0.1 product milestone.

### PAUSED / SUPERSEDED

No future product milestone is currently PAUSED or SUPERSEDED. Historical superseded work remains in Git/Issue/PR history.

## Recommended next execution

A fresh agent should:

1. verify current `main`, open Issues/PRs, and live GitHub Releases;
2. if `v0.1.0` is still absent, treat publication of the already-verified v0.1 release as the remaining release operation rather than creating new product work;
3. if release publication is already complete, either execute auxiliary Issue #7 when desired or stop;
4. before any new product implementation, perform a new planning pass and create durable roadmap/spec entries justified by repository evidence;
5. do not promote rates, XVA, portfolio risk, rough volatility, cross-platform installers, C++, or any other direction to READY merely because M9 is complete.

The deterministic selection/state/worktree rules remain in `docs/development/orchestration.md`.

## v0.1 release contract

The merged and verified v0.1 contract is deliberately evidence-bounded:

- package version `0.1.0`;
- Python **3.12** source installation;
- optional native desktop UI with **PySide6 6.11.2**;
- clean non-editable installation and source-launch smoke on Ubuntu CI;
- deterministic, network-free `scripts/v01_release_check.py` against committed M7/M8 evidence;
- `docs/release/v0.1.md` as the reviewer-facing install, launch, evidence, provenance, demo, and limitation guide; and
- Ubuntu 24.04 x86_64 standalone `pyside6-deploy` artifact as the CI-verified packaged proof.

The repository does **not** claim:

- macOS or Windows installer certification;
- code signing or notarization;
- an automatic update channel;
- universal support for the CI-produced Linux artifact;
- temporal forecasting skill from the M7 holdout;
- global Heston parameter identification;
- historical trading profitability;
- Heston hedge superiority; or
- that a C++ backend is justified for current v0.1 workloads.

Raw SPX source rows remain intentionally outside the repository. Core release verification uses committed derived evidence. `scripts/m7_model_validation.py` remains the authoritative replay path when the separately obtained pinned raw artifact is available.

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

Pinned baseline -> optimized representative heavy-workload evidence:

```text
Heston MC, 20k x 252                 3.3673 s -> 0.1230 s   27.38x
10-target / 3-start calibration      2.2919 s -> 0.4971 s    4.61x
14-target / 3-start calibration      3.2752 s -> 0.5454 s    6.01x
complete M7 validation study         5.4136 s -> 1.0819 s    5.00x
```

Deterministic financial parity checks pass; changed Monte Carlo RNG semantics are validated statistically rather than by equal-stream identity.

**No C++ kernel is retained for v0.1.** The measured post-optimization absolute cost did not justify compiler/binding/cross-platform packaging and parity surface.

Authoritative detail: `docs/models/m8_performance_engineering.md` and `docs/evidence/m8_performance_reference.json`.

## Native Workbench through UI5 / M9

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

UI5 remains the authoritative native product surface. M9 adds release packaging/verification around that product without moving quantitative logic into QML.

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

This document describes **now** and is intentionally less detailed than model/evidence docs.

If it conflicts with executable/live repository truth, use this order:

```text
current main / tests / required CI
        ↓
live PR, Issue, Release, and tag state
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
