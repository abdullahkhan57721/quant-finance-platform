# Development Roadmap

## Mission

Build a professional quantitative-finance research and model-validation platform whose first specialization is **equity derivatives and volatility modeling**.

The project is organized around mathematically meaningful problem families and evidence, not a checklist of finance keywords. Foundational mathematical distinctions may be explicit from the outset; operational frameworks must earn their abstractions from concrete consumers.

This file is the **execution graph**. For the current operational snapshot, read `current_state.md`. For global selection/state/worktree rules, read `orchestration.md`. Long implementation detail belongs in milestone specs, Issues, model docs, or PRs rather than this graph.

## State model

Milestones use:

```text
BLOCKED  READY  ACTIVE  REVIEW  MERGED  PAUSED  SUPERSEDED
```

Precise transition and completion semantics are defined in `docs/development/orchestration.md`.

`MERGED` means the required PR was squash-merged **and** repository-required post-merge `main` verification completed. A local implementation, green branch, or closed-unmerged PR is not `MERGED`.

Repository truth and live Issues/PRs override stale status text here.

## Priority

Lower number wins:

```text
P0  current critical path / release frontier
P1  near-term dependent work
P2  independent maintenance or lower-unblocking work
P3  optional/backlog work
```

Within equal priority, use roadmap order, dependency-unblocking value, then lower unstable-shared-contract risk.

## Execution graph

| id | title | status | priority | depends_on | parallel_with | blocks | issue | pr | spec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M0 | Engineering Bootstrap | MERGED | P0 | — | — | M0A, M1 | historical pre-index | historical pre-index | history in Git/roadmap |
| M0A | Mathematical Quant-Finance Architecture Foundation | MERGED | P0 | M0 | — | M1 | #9, #11 | #10, #14 | ADR 0001/0002 + history |
| M1 | European Options & Black-Scholes Reference Vertical | MERGED | P0 | M0A | UI1 after contracts stable | M2, UI1 | #5 | #15 | `docs/models/black_scholes.md` + history |
| M2 | Independent Valuation & Sensitivity/Greeks | MERGED | P0 | M1 | UI1 | M3, M4, UI2 | #19 | #20 | `docs/models/m2_numerical_methods_and_sensitivities.md` + history |
| M3 | Dynamic Hedging / Control | MERGED | P0 | M2 | M4 | M5, UI3 | #24 | #26 | `docs/models/m3_dynamic_delta_hedging.md` + history |
| M4 | Market Evidence / Implied-Volatility Inference | MERGED | P0 | M2 | M3 | M5, UI3 | #25 | #27 | M4 model/evidence docs + history |
| M5 | Heston Stochastic Volatility & Independent Valuation | MERGED | P0 | M3, M4 | UI3 after merged inputs | M6, UI4 | #30 | #31 | `docs/models/m5_heston_stochastic_volatility.md` + history |
| M6 | Heston Calibration / Multi-Parameter Inverse Problem | MERGED | P0 | M5 | UI4 after contracts stable | M7, UI4 | #34 | #35 | M6 model/evidence docs + history |
| M7 | Empirical Validation, Model Risk & BS vs Heston | MERGED | P0 | M6 | UI4 | M8, UI5 | #40 | #41 | `docs/models/m7_empirical_validation_and_model_risk.md` + history |
| M8 | Performance Engineering & Measured Native Decision | MERGED | P0 | M7 | UI5 after evidence contract stable | M9, UI5 | #42 | #45 | `docs/models/m8_performance_engineering.md` + history |
| UI1 | Native Workbench Architecture & Black-Scholes Vertical | MERGED | P1 | M1 | M2 | UI2 | #18 | #21 | ADR 0003 + native Workbench docs |
| UI2 | Valuation Comparison, Numerical Evidence & Greeks | MERGED | P1 | UI1, M2 | M3, M4 | UI3 | #28 | #29 | native Workbench docs + history |
| UI3 | Dynamic Hedging, Market Evidence & Scalar Inference | MERGED | P1 | UI2, M3, M4 | M5 | UI4 | #32 | #33 | native Workbench docs + history |
| UI4 | Heston Forward Valuation, Calibration & Identifiability | MERGED | P1 | UI3, M5, M6 | M7 | UI5 | #38 | #39 | native Workbench docs + history |
| UI5 | Validation, Model Risk & Product Hardening | MERGED | P1 | UI4, M7, M8 | — | M9 | #43 | #44 | `docs/models/ui5_validation_model_risk_and_product_hardening.md` + history |
| M9 | Portfolio-Quality v0.1 Release | MERGED | P0 | M8, UI5 | — | planned v0.1 complete | #50 | #51 | [`milestones/M9.md`](milestones/M9.md) |

Issue/PR identifiers above are historical navigation where known; live GitHub state is authoritative.

## Current product frontier

```text
No committed READY product milestone.
```

M9 is repository-defined `MERGED` because PR #51 was squash-merged and the required post-merge Core, Release Verification, and Desktop workflows all succeeded on exact `main` commit:

```text
6237ccad3ec27153c294a84da32350b0bd1b12c1
```

The committed v0.1 product roadmap therefore ends at M9.

Independent repository maintenance remains:

```text
P2  Issue #7 — Add cognitive-complexity quality gate
```

Issue #7 is not a product milestone and does not unlock another quantitative milestone.

## v0.1 publication state

Repository implementation and verification are complete. At the M9 closeout snapshot, live GitHub shows **no published Release**.

Therefore:

```text
M9 repository milestone        MERGED
v0.1.0 tag/release publication pending until live GitHub shows it
```

Publishing the already-verified `v0.1.0` release is a post-verification release operation, not a new roadmap node. Do not report publication as complete from documentation alone; inspect live GitHub Releases/tags.

## Dependency narrative

```text
M0 / M0A
    ↓
M1
    ↓
M2
   ├───────────────┐
   ↓               ↓
  M3              M4
   └───────┬───────┘
           ↓
          M5
           ↓
          M6
           ↓
          M7
           ↓
          M8

M1 -> UI1 -> UI2
             ↓
      M3 + M4 -> UI3
      M5 + M6 -> UI4
      M7 + M8 -> UI5

M8 + UI5
    ↓
   M9
    ↓
planned v0.1 product roadmap complete
```

The earned research story remains:

```text
theory
-> independent numerical evidence
-> sensitivity / replication pressure
-> observed-market falsification pressure
-> richer stochastic-volatility forward model
-> calibrated inverse problem with identifiability evidence
-> predeclared held-out model comparison
-> measured optimization
-> validation-first native presentation/product hardening
-> verified v0.1 release surface
```

## M9 completion boundary

M9 consolidated rather than broadened scope. It consumes the earned M1–M8 and UI1–UI5 evidence stack and leaves:

- package version `0.1.0`;
- a reviewer-facing release guide and changelog;
- clean non-editable install verification;
- deterministic network-free verification of committed M7/M8 release evidence;
- a tested native Workbench source-launch path;
- an Ubuntu 24.04 x86_64 standalone build/packaged-launch proof;
- the bounded M7 same-date held-out Black-Scholes vs Heston comparison;
- the M8 measured Python/NumPy optimization result;
- the explicit M8 decision that C++ is not justified for current v0.1 workloads; and
- no unsupported cross-platform installer/signing claims.

See the durable M9 spec and `docs/release/v0.1.md` for the authoritative release boundary.

## Post-v0.1 directions are not READY milestones

Potential later specializations include rates, XVA/counterparty credit, portfolio market risk, and possibly rough-volatility research after reviewing then-current literature and v0.1 limitations.

These are **directions, not executable milestones**. They have no status, priority, dependency graph entry, or implementation permission until a future planning pass justifies them and creates durable specs from repository evidence.

A fresh agent must not invent an M10 simply because M9 is complete.
