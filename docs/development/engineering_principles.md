# Engineering Principles

## Purpose

This document records the engineering lessons intentionally carried into the Quantitative Finance Research & Validation Platform from prior repository work, especially Evolution Simulation Engine v0.1.0.

The transfer is about **development discipline**, not domain architecture. Evolution-specific concepts are not templates for finance. The finance repository, its current consumers, tests, and evidence decide what survives.

`AGENTS.md` contains the operating rules. This document explains the reasoning behind them so future agents can apply the principles instead of cargo-culting them.

## 1. Repository truth is collaboration memory

Long chats are useful for exploration but are poor durable state. Fresh sessions should be able to reconstruct the project from the repository.

Use this hierarchy of evidence:

```text
current main / tests / CI
        ↓
AGENTS.md
        ↓
architecture + quantitative conventions
        ↓
ADRs
        ↓
active Issue / PR
        ↓
current-state / roadmap navigation
        ↓
conversation context
```

Conversation memory can help locate a decision. It should not override live repository truth.

## 2. Put information at the right lifetime

Different information changes at different rates. Mixing all of it into one giant project-context document makes important rules hard to find and volatile details go stale.

| Information | Durable home |
| --- | --- |
| Operating rules for agents/contributors | `AGENTS.md` |
| Current architecture and dependency boundaries | `docs/architecture/` |
| Quantitative representation conventions | `docs/quantitative_conventions.md` |
| Why a consequential decision was made | ADR under `docs/decisions/` |
| Concise current orientation | `docs/development/current_state.md` |
| Milestone sequencing | `docs/development/roadmap.md` |
| Exact implementation work unit | GitHub Issue |
| In-progress/recovery state | Pull request |
| Actual behavior | Code and tests |
| Enforced quality | CI |
| Historical evolution | Git history |
| Explanatory/teaching material | Dedicated learning docs |

The point is not more documentation. The point is **less duplicated documentation with clearer ownership**.

## 3. Generalize from pressure, not imagination

A useful architecture loop is:

```text
concrete use case
      ↓
implementation friction
      ↓
identify the exact conflated responsibility
      ↓
separate only what the evidence requires
      ↓
add a discriminating consumer/test
```

The first Black-Scholes vertical should therefore remain concrete enough to reveal real boundaries. Do not invent a universal finance framework because Heston, rates, XVA, or rough volatility might exist later.

At the same time, do not overfit the first use case. When a public contract is proposed, ask:

1. What part is intrinsic to the responsibility?
2. What part exists only because the first example is simple?
3. What future pressure is reasonably foreseeable and expensive to block accidentally?
4. What should remain deliberately deferred until a second real consumer exists?

## 4. Separate concepts that merely happen to coincide

Simple examples make different responsibilities look identical. The project should resist that illusion.

Examples:

```text
market observation != valuation-ready market state
instrument != trade != portfolio
financial model != numerical valuation method
model structure != parameter set
calibration problem != optimizer
pricing result != calibration result != validation result
observed market value != model-generated value
research study != production library != presentation
```

This is not abstraction for abstraction's sake. It prevents one object from accumulating unrelated ownership, mutation, and lifecycle responsibilities.

## 5. Make ownership and mutability explicit

Consequential boundaries should answer:

- Who owns this value?
- Can it change after construction?
- If it changes, is that mutation part of the model or merely orchestration state?
- Is the value observed, derived, configured, calibrated, simulated, or committed evidence?

Prefer immutable completed evidence objects where practical. Calibration work buffers, optimizer state, caches, and simulation scratch arrays may be mutable internally without making committed results mutable.

Configuration/request objects should not double as mutable runtime state or completed results.

## 6. Quantitative conventions are part of correctness

Many finance bugs are not algebra mistakes. They are silent convention mismatches:

- annual vs continuously compounded rates;
- decimal vs percentage volatility;
- calendar days vs business days;
- inconsistent day count;
- spot vs forward interpretation;
- inconsistent dividend/carry treatment;
- Greek scaling/sign conventions;
- hidden unit assumptions.

The project therefore maintains an explicit convention register. A convention can remain deferred, but it may not remain *implicit* at a public boundary.

## 7. Validation is an architectural capability

A price that looks plausible is weak evidence.

Important implementations should accumulate independent evidence such as:

```text
theoretical identities / bounds
        +
known limiting cases
        +
independent numerical formulations
        +
convergence / stability studies
        +
stochastic error analysis
        +
parameter recovery
        +
empirical / out-of-sample evidence
        +
model-risk analysis
```

Do not let one implementation validate itself. Independent implementations can still share a conceptual error, so theoretical and limiting evidence remain important.

Tests should protect mathematical/financial invariants and public semantics rather than incidental internal structure.

## 8. Reproducibility is architecture

Randomness and provenance should enter through explicit boundaries.

For stochastic studies, record as applicable:

- seed and RNG/bit-generator information;
- path counts and discretization;
- numerical method/configuration;
- model and parameter values;
- market-data provenance or fixture identity;
- code revision/software environment;
- tolerances and stopping conditions.

Do not use ambient global RNG state in production stochastic APIs.

For Python/C++ parity, do not require equal integer seeds to produce identical random streams. Use shared pre-generated random inputs when strict kernel parity is the objective.

## 9. Formula provenance should be traceable

When mathematical implementations arrive, important formulas should be traceable through:

```text
reference or derivation
      ↓
project notation mapping
      ↓
implementation
      ↓
assumptions / domain restrictions
      ↓
limiting cases / identities
      ↓
automated tests
```

This is especially valuable in a model-validation portfolio because the code should be auditable by someone who knows the mathematics.

## 10. Performance work needs evidence

Use this order:

```text
reproducible workload
      ↓
profile
      ↓
identify measured hotspot
      ↓
understand repeated work / algorithm
      ↓
optimize the narrow cause
      ↓
re-measure
```

Benchmark the layer being claimed. A pricing kernel, Monte Carlo path loop, calibration objective, and end-to-end research workflow are not interchangeable benchmarks.

Prefer repeated-run medians. Treat hosted CI wall-clock time as noisy. When possible, add structural evidence such as counts of valuations, objective evaluations, paths, factorizations, or characteristic-function evaluations.

Optimize algorithm and repeated work before changing language. A measurable speedup is not automatically worthwhile if it materially reduces readability, auditability, or numerical trustworthiness.

C++ is an earned optimization target, not a project-start architecture requirement. Preserve a readable Python reference and parity/conformance tests when native acceleration arrives.

## 11. Issues are executable specifications

A substantial Issue should make the implementation hard to misunderstand. Useful sections include:

- Goal and why;
- dependencies;
- allowed areas and do-not-touch areas;
- quantitative assumptions/conventions;
- public contracts affected;
- ownership/mutability semantics;
- likely wrong interpretations or traps;
- requirements and non-goals;
- acceptance criteria;
- automated verification;
- manual verification;
- documentation impact;
- follow-up boundary.

The **likely wrong interpretations / traps** section is especially valuable for AI-assisted development because locally plausible implementations can violate the intended architecture while still looking polished.

Out-of-scope discoveries normally become follow-up Issues instead of invisible scope expansion.

## 12. Pull requests are recovery checkpoints

Open PRs early enough that the branch has a durable recovery surface. For work spanning sessions, preserve:

```text
Implemented:
Remaining:
Current blocker:
Last verified head:
Last CI result:
Next action:
```

A completion report should state architecture/API impact, quantitative/modeling impact, exact verification, manual verification, performance evidence when relevant, docs impact, risks/follow-ups, and the recovery checkpoint.

Review and merge the exact head that passed CI.

## 13. Allocate ChatGPT and Codex by work shape

Use ChatGPT where judgment and shared-contract correctness dominate:

- architecture;
- quantitative modeling decisions;
- public APIs;
- roadmap sequencing;
- high-consequence conventions;
- independent review.

Use Codex where execution dominates after interfaces are settled:

- repetitive migrations;
- large analogous test changes;
- debugging/validation loops;
- mechanical updates;
- independently parallelizable implementation.

Do not delegate architecture-sensitive work merely because it is substantial. Settle consequential shared contracts first and encode them in the Issue.

## 14. Parallelize only behind settled interfaces

Parallel work is useful only when coordination cost stays low.

Good candidates:

- independent test expansion around a stable API;
- documentation/report work against committed results;
- data-fixture/provenance work alongside stable downstream consumers;
- numerical-method implementation after model semantics are fixed.

Poor candidates:

- two branches simultaneously inventing the same foundational finance types;
- model and calibration work before their shared parameter semantics are settled;
- C++ work before a measured Python hotspot and native boundary are known.

## 15. Automated tests are primary; manual verification is targeted

Automated verification should protect normal behavior and invariants.

Manual verification should be a small ticket-specific public-workflow sanity check, not a substitute for tests. State:

```text
scenario
→ action
→ expected result
→ observed result
```

Release work should additionally verify clean installation and every command claimed in documentation.

## 16. Presentation stays downstream of committed values

Notebooks, dashboards, reports, and future UI should consume production-library results rather than becoming a second implementation of the model.

If interactive configuration becomes important, normalize active UI state into typed production configuration. Hidden/inactive UI values should not leak into calculations.

Heavy presentation dependencies should remain optional where practical and receive their own smoke tests when introduced.

## 17. Prefer one coherent flagship story

Portfolio quality is improved by a causal, reproducible narrative rather than a large feature checklist.

The intended v0.1 story is approximately:

```text
Black-Scholes reference
      ↓
independent validation
      ↓
replication / hedging evidence
      ↓
real-market smile/skew contradiction
      ↓
Heston
      ↓
calibration + parameter recovery
      ↓
out-of-sample/model-risk comparison
      ↓
measured performance work
```

Empirical claims should be separated from illustrative or synthetic evidence. Do not present model demonstrations as trading-performance claims.

## 18. Add tooling when it has something real to guard

The initial gate is intentionally lean: Ruff, formatting, strict Pyright, and pytest.

Add later guards when justified:

- coverage threshold → once meaningful production code exists and the target measures useful test completeness;
- complexity guard → once nontrivial functions make cognitive complexity measurable;
- Import Linter / architecture contracts → once real package boundaries exist;
- strict docs build → once generated documentation becomes a supported product surface;
- quantitative contract suite → as models create identities/convergence/parameter-recovery contracts;
- benchmark/profile harness → after meaningful numerical workloads exist;
- clean-install/release smoke → before public release.

Do not weaken a guard merely to merge once it has become an intentional invariant.

## 19. Promote lessons deliberately

After consequential milestones, classify new lessons:

```text
local implementation fact
project-wide engineering principle
architecture invariant
quantitative convention
automated test
ADR
documentation update
roadmap change
```

Most observations should remain local. Promote them only when repeated evidence shows that they deserve a longer lifetime.

## 20. Core transfer rule

> Do not copy the old architecture. Copy the discipline that produced a good architecture.

The finance platform should become increasingly finance-native as real Black-Scholes, market-data, Heston, calibration, risk, and research consumers provide evidence. If a principle inherited from Evolution conflicts with stronger finance-domain evidence, update the finance repository and let repository truth win.
