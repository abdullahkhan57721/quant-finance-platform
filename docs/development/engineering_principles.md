# Engineering Principles

## Purpose

This document records the engineering lessons intentionally carried into the Quantitative Finance Research & Validation Platform from prior repository work.

The transfer is about **development discipline**, not domain architecture. Finance-specific mathematics, repository consumers, tests, and evidence decide the architecture.

`AGENTS.md` contains operating rules. This document explains the reasoning behind them so future agents can apply the principles instead of cargo-culting them.

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

The point is not more documentation. The point is less duplicated documentation with clearer ownership.

## 3. Generalize from pressure — with one finance-native foundational exception

The ordinary architecture loop remains:

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

For most of the platform, one consumer stays concrete and two real consumers are required before shared extraction is considered.

M0A introduces one deliberate exception, recorded by ADR 0001: the stable mathematical responsibilities of the asset-pricing problem may be represented explicitly before two implemented consumers exist.

That exception is justified because

```text
state
stochastic law
parameters
contract / cash flows
numeraire / pricing measure
pricing problem
valuation method
valuation result
```

are distinct mathematical responsibilities, not merely future software-reuse guesses.

The exception is narrow. It does **not** mean “generalize finance from imagination.” Market-data, calibration, risk, portfolio, validation, studies, rates infrastructure, and native execution still need concrete consumer pressure.

When a public contract is proposed, ask:

1. Is this responsibility part of the accepted foundational pricing mathematics, or an application abstraction?
2. What part is intrinsic to the responsibility?
3. What part exists only because the first example is simple?
4. What future pressure is reasonably foreseeable and expensive to block accidentally?
5. What should remain deliberately deferred until a second real consumer exists?

## 4. Separate concepts that merely happen to coincide

Simple examples make different responsibilities look identical. The project should resist that illusion.

Examples:

```text
state != stochastic law != parameters
contract != realized cash-flow stream
numeraire != pricing measure
pricing problem != valuation method != valuation result
market observation != valuation-ready market state
financial contract != trade != portfolio
calibration problem != optimizer
observed market value != model-generated value
research study != production library != presentation
```

This is not abstraction for abstraction's sake. It prevents one object from accumulating unrelated ownership, mutation, lifecycle, and mathematical responsibilities.

## 5. Make ownership and mutability explicit

Consequential boundaries should answer:

- Who owns this value?
- Can it change after construction?
- If it changes, is that mutation part of the model or merely orchestration state?
- Is the value observed, derived, configured, calibrated, simulated, or committed evidence?

Prefer immutable completed evidence/value objects where practical. M0A uses immutable modeled state, cash flows, pricing problems, and valuation results. Model-specific parameter objects should likewise be value-like where appropriate.

Calibration work buffers, optimizer state, caches, and simulation scratch arrays may be mutable internally without making committed results mutable.

Configuration/request objects should not double as mutable runtime state or completed results.

## 6. Quantitative conventions are part of correctness

Many finance bugs are silent convention mismatches:

- annual vs continuously compounded rates;
- decimal vs percentage volatility;
- calendar days vs business days;
- inconsistent day count;
- spot vs forward interpretation;
- inconsistent dividend/carry treatment;
- Greek scaling/sign conventions;
- hidden unit assumptions.

The project therefore maintains an explicit convention register. A convention can remain deferred, but it may not remain implicit at a public boundary.

M0A commits structural pricing semantics and strictly-positive numeraire values; it deliberately does not pretend those decisions settle M1's dates, rate/compounding, carry, or volatility conventions.

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

M0A's evidence is architectural rather than financial-formula evidence: composition, immutability, compatibility, numeraire validity, P-vs-Q semantics, typing, and dependency direction. M1 adds the first formula-level financial evidence.

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

When mathematical formula implementations arrive, important formulas should be traceable through:

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

M0A defines semantic architecture but no production pricing formula. M1 should be the first concrete demonstration of this traceability chain.

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

The **likely wrong interpretations / traps** section is especially valuable for AI-assisted development because locally plausible implementations can violate the intended architecture, quantitative semantics, scope, or validation strategy while still looking polished.

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

Good candidates:

- independent test expansion around a stable API;
- documentation/report work against committed results;
- data-fixture/provenance work alongside stable downstream consumers;
- numerical-method implementation after model semantics are fixed.

Poor candidates:

- two branches simultaneously redefining the foundational pricing semantics;
- model and calibration work before shared parameter semantics are settled;
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

The intended v0.1 story is approximately:

```text
mathematical pricing foundation
      ↓
Black-Scholes reference specialization
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

The initial gate remains intentionally lean on current `main`: Ruff, formatting, strict Pyright, and pytest.

Issue #7 tracks cognitive complexity now that production finance code exists. Other guards should still be added when justified:

- coverage threshold → once meaningful production code makes the target useful;
- Import Linter / architecture contracts → when broader package boundaries need machine enforcement beyond focused tests;
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

Most observations should remain local. Promote them only when repeated evidence—or, for ADR 0001, stable finance-native mathematics—shows they deserve a longer lifetime.

## 20. Core transfer rule

> Do not copy the old architecture. Copy the discipline that produced a good architecture, then let finance mathematics and evidence correct the discipline where appropriate.

If a principle inherited from earlier work conflicts with stronger finance-domain evidence, update the finance repository explicitly, preserve the historical rationale, and let repository truth win.
