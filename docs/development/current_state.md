# Current State

## Operational snapshot

The quantitative-finance platform has completed and repository-verified:

~~~text
M0, M0A, M1, M2, M3, M4, M5, M6, M7, M8, M9
UI1, UI2, UI3, UI4, UI5
F1
~~~

ADR 0002 remains the mathematical architecture authority. ADR 0003 remains the native PySide6 + Qt Quick/QML authority.

The project is **continuing beyond the historical M9 packaging/release milestone**. Publishing a GitHub Release/tag or advancing a semantic version is not a dependency for further development.

The next committed product track is the **F-series finance-facing interface layer**:

~~~text
F1  Research API & Multi-Surface Interface Boundary
F2  Reproducible Jupyter Research Studies
F3  Analyst Interoperability & Structured Exports
F4  Dash/Plotly Internal Analytics Workbench
F5  Multi-Surface Integration & Portfolio Documentation
~~~

## Execution frontier

### READY — product

- **F3 — Analyst Interoperability & Structured Exports**, P1.
- **F4 — Dash/Plotly Internal Analytics Workbench**, P1.

F1 is squash-merged and verified on main. F3/F4 are independent sibling consumers of the merged F1 contracts, but neither is activated by the current F2 work unit.

### BLOCKED — product

- **F5 — Multi-Surface Integration & Portfolio Documentation**, blocked on F2, F3, and F4.

### READY — auxiliary maintenance

- **Issue #7 — cognitive-complexity quality gate**, P2.

Issue #7 is not part of the F-series dependency chain.

### ACTIVE / REVIEW

**F2 — Reproducible Jupyter Research Studies** is in REVIEW in Issue #57 / PR #58 on branch `f2-57-jupyter-studies`.

F2 was selected from the F2/F3/F4 READY frontier by equal-priority roadmap order. It owns notebooks, research-only tooling/dependencies, notebook execution evidence, and the minimum documentation/CI required for those studies. It must not consume unmerged F3/F4 behavior or move quantitative logic into notebook cells.

## Deterministic next execution

A fresh agent asked to continue development should:

1. verify current main and live Issues/PRs;
2. recover F2 Issue #57 and its branch/PR if still open rather than duplicating work;
3. inspect F2 exact-head validation and preserve the human merge gate;
4. keep F3/F4 READY unless live repository truth introduces a blocker or another isolated work unit activates them;
5. keep F5 BLOCKED until F2, F3, and F4 are repository-defined MERGED.

No copied milestone prompt is required.

## F-series target architecture

The goal is not to replace the existing Qt Workbench. It is to make Qt one sibling client of the same quantitative/application semantics:

~~~text
                         quantitative core
                               ↑
                    application/research semantics
                               ↑
        ┌──────────────┬───────┼────────┬──────────────┐
        │              │       │        │              │
     Python         Jupyter   exports   Dash          Qt/QML
   programmatic     research  XLSX/CSV  analytics     desktop
                               /JSON
~~~

Protect:

~~~text
quantitative result/evidence != presentation artifact
research API != duplicate quantitative implementation
notebook != production algorithm location
spreadsheet != pricing/calibration engine
Dash callback != financial-model authority
Qt controller != reusable research API
~~~

F1 verified the existing qf_platform.application/domain packages as the frontend-neutral research seam and deliberately added no duplicate research façade.

## Earned quantitative capability snapshot

### Black-Scholes / M1–M2

European calls/puts, ACT/365F, flat continuously compounded money-market numeraire, Black-Scholes closed form, CRR, seeded Monte Carlo, and analytic/finite-difference Delta, Gamma, Vega, Theta, and Rho.

### Dynamic hedging / M3

Analytic Delta consumed as a hedge-policy input over exact-transition pricing-measure GBM paths with explicit rebalance schedules, stock/cash self-financing accounting, volatility misspecification, proportional transaction costs, and replication-error summaries. These remain model-generated replication experiments, not historical trading backtests.

### Market evidence / M4

Provenance-bearing raw option/underlying observations, explicit midpoint normalization, Black-Scholes implied-volatility inversion with separate bisection, conditioning evidence, static quote diagnostics, and pinned January 4, 2023 SPX evidence showing strike skew and maturity dependence.

### Heston / M5–M6

Explicit Heston state/law/parameter semantics, independent Fourier and seeded full-truncation Euler Monte Carlo valuation, Feller diagnostics, exact deterministic-variance handling at xi=0, cross-method validation, and price-space calibration of (v0, kappa, theta, xi, rho) with multiple starts and local identifiability/conditioning evidence.

### Validation / M7

M7 uses a predeclared same-date cross-sectional holdout over 14 selected SPX/SPXW contracts:

~~~text
10 training
4 held-out evaluation
~~~

Representative held-out evidence:

~~~text
                         Black-Scholes      Heston
price RMSE                   8.412           0.671
half-spread std. RMSE       20.613           1.649
relative MAE                 8.27%            0.66%
~~~

Within that explicit sample and design, Heston materially improves held-out pricing metrics relative to the fairly fitted one-volatility Black-Scholes benchmark. This does not establish temporal generalization, physical-measure forecasting skill, global Heston identification, historical trading profitability, or Heston hedge superiority.

### Performance / M8

Pinned baseline → optimized representative heavy-workload evidence:

~~~text
Heston MC, 20k x 252                 3.3673 s -> 0.1230 s   27.38x
10-target / 3-start calibration      2.2919 s -> 0.4971 s    4.61x
14-target / 3-start calibration      3.2752 s -> 0.5454 s    6.01x
complete M7 validation study         5.4136 s -> 1.0819 s    5.00x
~~~

No C++ kernel is currently justified by the measured representative workloads. Reopen native acceleration only after materially different workloads and new profiling evidence.

## Existing application / presentation boundary

The current durable dependency direction remains:

~~~text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs + committed derived evidence
        ↓
production quantitative core
~~~

The F-series generalizes the set of downstream clients; it does not reverse this dependency direction.

## Historical M9/release work

M9 remains MERGED history and its package/release docs remain valid records of what was implemented at that time.

However:

- there is no current requirement to publish a GitHub Release/tag;
- no future milestone is blocked on release publication;
- the project does not stop at M9;
- future roadmap work does not need to be organized around semantic versions.

Existing package version metadata may remain because Python packaging requires a version field. It is not the project-planning model.

## Deliberately absent from the committed F-series

The repository still does not commit to:

- a REST/FastAPI service;
- a React/TypeScript frontend;
- an Excel add-in;
- live market-data feeds for the default research workflows;
- generic persisted workspace/project infrastructure;
- a universal report engine;
- generic model/plugin registries;
- a C++ backend without new profiling evidence;
- rates, XVA, portfolio-risk, or new stochastic-model families.

These may be considered in a later repository-grounded planning pass. They are not automatic F6+ work.

## Staleness and verification rule

If this document conflicts with executable/live repository truth, use:

~~~text
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
~~~

Correct material stale state as part of the active work unit rather than relying on it blindly.
