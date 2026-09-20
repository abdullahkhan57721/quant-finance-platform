# Development Roadmap

## Mission

Build a professional quantitative-finance research and model-validation platform whose first specialization is **equity derivatives and volatility modeling**.

The project is organized around mathematically meaningful problem families and evidence, not a checklist of finance keywords. Foundational mathematical distinctions may be explicit from the outset; operational frameworks must earn their abstractions from concrete consumers.

This file is the **execution graph**. For the current operational snapshot, read current_state.md. For global selection/state/worktree rules, read orchestration.md. Long implementation detail belongs in milestone specs, Issues, model docs, or PRs rather than this graph.

The project does **not** stop at a package/release version. Historical release work remains part of the repository record, but publishing or incrementing a version is not a dependency for continued development.

## State model

Milestones use:

~~~text
BLOCKED  READY  ACTIVE  REVIEW  MERGED  PAUSED  SUPERSEDED
~~~

Precise transition and completion semantics are defined in docs/development/orchestration.md.

MERGED means the required PR was squash-merged and repository-required post-merge main verification completed. A local implementation, green branch, or closed-unmerged PR is not MERGED.

Repository truth and live Issues/PRs override stale status text here.

## Priority

Lower number wins:

~~~text
P0  current critical path
P1  near-term dependent work
P2  independent maintenance or lower-unblocking work
P3  optional/backlog work
~~~

Within equal priority, use roadmap order, dependency-unblocking value, then lower unstable-shared-contract risk.

## Execution graph

| id | title | status | priority | depends_on | parallel_with | blocks | issue | pr | spec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M0 | Engineering Bootstrap | MERGED | P0 | — | — | M0A, M1 | historical pre-index | historical pre-index | history in Git/roadmap |
| M0A | Mathematical Quant-Finance Architecture Foundation | MERGED | P0 | M0 | — | M1 | #9, #11 | #10, #14 | ADR 0001/0002 + history |
| M1 | European Options & Black-Scholes Reference Vertical | MERGED | P0 | M0A | UI1 after contracts stable | M2, UI1 | #5 | #15 | model docs + history |
| M2 | Independent Valuation & Sensitivity/Greeks | MERGED | P0 | M1 | UI1 | M3, M4, UI2 | #19 | #20 | model docs + history |
| M3 | Dynamic Hedging / Control | MERGED | P0 | M2 | M4 | M5, UI3 | #24 | #26 | model docs + history |
| M4 | Market Evidence / Implied-Volatility Inference | MERGED | P0 | M2 | M3 | M5, UI3 | #25 | #27 | model/evidence docs + history |
| M5 | Heston Stochastic Volatility & Independent Valuation | MERGED | P0 | M3, M4 | UI3 after merged inputs | M6, UI4 | #30 | #31 | model docs + history |
| M6 | Heston Calibration / Multi-Parameter Inverse Problem | MERGED | P0 | M5 | UI4 after contracts stable | M7, UI4 | #34 | #35 | model/evidence docs + history |
| M7 | Empirical Validation, Model Risk & BS vs Heston | MERGED | P0 | M6 | UI4 | M8, UI5 | #40 | #41 | model/evidence docs + history |
| M8 | Performance Engineering & Measured Native Decision | MERGED | P0 | M7 | UI5 after evidence contract stable | M9, UI5 | #42 | #45 | model/evidence docs + history |
| UI1 | Native Workbench Architecture & Black-Scholes Vertical | MERGED | P1 | M1 | M2 | UI2 | #18 | #21 | ADR 0003 + native Workbench docs |
| UI2 | Valuation Comparison, Numerical Evidence & Greeks | MERGED | P1 | UI1, M2 | M3, M4 | UI3 | #28 | #29 | native Workbench docs + history |
| UI3 | Dynamic Hedging, Market Evidence & Scalar Inference | MERGED | P1 | UI2, M3, M4 | M5 | UI4 | #32 | #33 | native Workbench docs + history |
| UI4 | Heston Forward Valuation, Calibration & Identifiability | MERGED | P1 | UI3, M5, M6 | M7 | UI5 | #38 | #39 | native Workbench docs + history |
| UI5 | Validation, Model Risk & Product Hardening | MERGED | P1 | UI4, M7, M8 | — | M9 | #43 | #44 | UI5 model/architecture docs |
| M9 | Portfolio-Quality v0.1 Release | MERGED | P3 | M8, UI5 | — | F1 | #50 | #51 | milestones/M9.md; historical release hardening |
| F1 | Research API & Multi-Surface Interface Boundary | MERGED | P0 | M9 | — | F2, F3, F4 | #55 | #56 | milestones/F1.md |
| F2 | Reproducible Jupyter Research Studies | REVIEW | P1 | F1 | F3, F4 | F5 | #57 | #58 | milestones/F2.md |
| F3 | Analyst Interoperability & Structured Exports | ACTIVE | P1 | F1 | F2, F4 | F5 | #59 | — | milestones/F3.md |
| F4 | Dash/Plotly Internal Analytics Workbench | READY | P1 | F1 | F2, F3 | F5 | create on activation | — | milestones/F4.md |
| F5 | Multi-Surface Integration & Portfolio Documentation | BLOCKED | P1 | F2, F3, F4 | — | — | create on activation | — | milestones/F5.md |

Issue/PR identifiers above are historical navigation where known; live GitHub state is authoritative.

## Current product frontier

~~~text
P1 REVIEW
F2 — Reproducible Jupyter Research Studies — Issue #57 / PR #58

P1 ACTIVE
F3 — Analyst Interoperability & Structured Exports — Issue #59

P1 READY
F4 — Dash/Plotly Internal Analytics Workbench
~~~

F1 is squash-merged and post-merge verified on main. F2 was selected first by the deterministic equal-priority roadmap-order rule and is now in final review/validation in PR #58. F3 is ACTIVE in its isolated work unit while F2 completes post-merge verification. F4 remains independently READY.

F5 remains BLOCKED until F2, F3, and F4 are all repository-defined MERGED.

Independent repository maintenance remains:

~~~text
P2  Issue #7 — Add cognitive-complexity quality gate
~~~

Issue #7 is not in the product dependency chain.

## F-series dependency narrative

~~~text
merged quantitative core + application layer + Qt Workbench
                         ↓
                        F1
                research-facing API boundary
                  ┌──────┼──────┐
                  ↓      ↓      ↓
                 F2     F3     F4
              notebooks exports Dash
                  └──────┼──────┘
                         ↓
                        F5
             multi-surface integration
~~~

F2/F3/F4 are candidate parallel work only after F1 is MERGED. The orchestration rule still requires live overlap/shared-contract inspection before running them concurrently.

## F-series architectural intent

The project should become usable through several sibling surfaces without moving financial semantics out of the production core:

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

The Qt Workbench remains valuable, but it is one client rather than the universal entry point.

F1 must audit the existing qf_platform.application surface before inventing another façade. F2–F4 consume the F1 result. F5 integrates the finished surfaces.

## Historical M9 boundary

M9 is complete history. It established packaging/reviewer-facing release hardening around the then-current platform.

It does **not** imply:

- that development is complete;
- that a GitHub Release/tag must be published before new work;
- that future milestones must be framed as semantic versions; or
- that later product work requires a version bump.

Existing package version metadata and release documentation may remain for historical/package-tooling reasons. They are not the current roadmap frontier.

## Deliberately uncommitted later directions

The following are not part of the committed F1–F5 graph:

- REST service / FastAPI;
- React/TypeScript frontend;
- Excel add-in;
- rates;
- XVA/counterparty credit;
- portfolio market-risk infrastructure;
- rough-volatility or other new model families;
- C++ acceleration without new profiling evidence.

A fresh agent must not invent F6 or another quantitative specialization merely because F5 later merges. A new planning pass should establish the next frontier from repository evidence.
