# Validation Cadence and Development Efficiency

## Purpose

This document records the current evidence-based validation cadence for routine development in the Quantitative Finance Research & Validation Platform.

The goal is not to make validation weaker. The goal is to catch the right class of error at the cheapest useful boundary, while preserving the complete merge standard and keeping quantitative/model validation proportional to the work being changed.

Repository truth, the active Issue, and `AGENTS.md` remain authoritative. Re-measure this policy when the codebase or quality gate grows materially.

## Measured baseline

Recent repository history shows that the current CI pipeline is cheap, while avoidable push-by-push cleanup is a real source of iteration cost.

Evidence sampled on 2026-09-08:

- M0A PR #10 produced 15 pull-request CI runs before merge: 14 failed and the final run passed.
- The final green M0A job took about 17 seconds of runner time and about 25 seconds from workflow creation to completion.
- In that green job, checkout plus Python setup plus editable development install consumed about 12 seconds; the complete `./scripts/check_all` gate consumed about 4 seconds.
- Ruff itself was effectively negligible compared with setup/install; Pyright was the largest part of the actual gate, and pytest was still sub-second at the sampled repository size.
- Several M0A commits were explicitly import-order or formatting cleanup.
- An inspected failed M0A run paid the setup/install cost and then failed almost immediately on Ruff `I001`, which Ruff marked auto-fixable.
- M0B PR #14 produced nine pull-request CI runs during a roughly ten-minute PR lifetime even though its sampled run history was green.
- Active M1 PR #15 also encountered an auto-fixable Ruff import-order failure before later checks could run.

PR lifetime is not active implementation time, so these observations must not be read as developer-hour measurements. They show iteration shape: the complete gate is currently inexpensive, while mechanical failures and unnecessary CI-triggering pushes are avoidable.

## Canonical commands

`scripts/fix` already expresses the desired mechanical-cleanup policy:

```text
ruff check . --fix
ruff format .
```

The repository intentionally uses Ruff's safe fixes here. Do not add global unsafe fixes. An unsafe transformation, if ever justified, is a reviewed code change rather than formatting.

`scripts/check_all` remains the complete current software-quality entry point:

```text
ruff check .
ruff format --check .
pyright src tests
pytest -q
```

Issue #7 separately owns cognitive-complexity enforcement. Do not duplicate that implementation here. If it lands as an inexpensive canonical check, it belongs in the normal checkpoint/final gate rather than a separate expensive workflow.

## Validation cadence

### Inner loop

After a coherent Python implementation batch:

```text
./scripts/fix
        +
focused tests for changed behavior
        +
focused quantitative/numerical checks where relevant
        +
broader typing when the changed public/type boundary warrants it
```

Examples include a directly affected test module or `pytest -k` selection. Cheap deterministic checks such as a relevant identity, no-arbitrage property, limiting case, or local numerical invariant belong here when they help debug the work being changed.

Do not use the complete CI workflow as the formatting or first-line debugging loop.

### Repository checkpoint

Before an ordinary PR push or at a coherent implementation checkpoint:

```text
./scripts/check_all
```

The complete current gate is fast enough that a second `--fast` script would add vocabulary without meaningful measured benefit. Batch trivial cleanup before pushing instead of creating a commit/push solely to make CI discover an auto-fixable formatting problem.

A draft PR remains valuable as a durable recovery checkpoint. Keep it current at meaningful checkpoints, not at every tiny edit.

### Final candidate

Before final review:

```text
./scripts/fix
        ↓
./scripts/check_all
        ↓
full required CI
        ↓
ticket-specific quantitative / numerical validation
        ↓
manual verification when the ticket requires it
        ↓
review the exact candidate head
        ↓
squash merge
        ↓
verify main
```

A change to the final candidate head invalidates prior exact-head evidence. Re-run the required final validation on the new head.

When concurrent work is active, re-check `main` before final merge so stale-base or newly conflicting assumptions are caught before the squash merge.

## Agent workflow and recovery behavior

Future ChatGPT/Codex sessions should use this sequence:

1. orient from current repository truth;
2. settle consequential quantitative and public architecture before broad implementation;
3. implement in coherent batches;
4. run `./scripts/fix` proactively after coherent Python changes;
5. use focused tests and focused quantitative checks while developing;
6. use broader typing when public/type boundaries make it useful;
7. avoid using full CI as a formatting/debug loop;
8. run the repository-wide gate at meaningful checkpoints;
9. open a draft PR early as a recovery checkpoint;
10. keep that recovery checkpoint current without unnecessary push churn;
11. batch trivial fixes before pushing;
12. re-check `main` before final merge when concurrent work is active;
13. exact-head validate before squash merge; and
14. verify `main` afterward.

Preserve the existing work allocation policy: ChatGPT owns architecture, mathematical/quantitative contracts, consequential conventions, architecture-sensitive implementation, and review; Codex is appropriate for execution-heavy work behind settled interfaces. Do not delegate merely because a milestone is large.

## Software quality is not the whole quantitative validation program

Keep these responsibilities distinct even when some cheap quantitative checks run under pytest.

### Software / structural quality

Examples:

- Ruff lint and canonical formatting;
- strict Pyright;
- unit and inexpensive integration tests;
- cognitive-complexity enforcement once Issue #7 lands;
- focused dependency/architecture guards where current code has earned them.

### Quantitative / model validation

Examples, as their concrete models arrive:

- formula/reference traceability;
- theoretical identities and no-arbitrage properties;
- limiting cases;
- convergence and stability;
- stochastic/statistical evidence;
- independent cross-method agreement;
- parameter recovery;
- calibration stability;
- out-of-sample/model-risk evidence;
- Python/C++ parity after a real native implementation exists.

Cheap deterministic quantitative invariants can and should be ordinary tests. Longer Monte Carlo, Heston, calibration, empirical, parameter-recovery, or parity studies should become mandatory only for changes and final candidates to which they are relevant. Do not make an unrelated documentation or UI change pay for every future scientific study.

## Current quality-gate classification

| Guard / evidence | Current classification | Rationale |
| --- | --- | --- |
| `./scripts/fix` | Inner-loop cheap | Prevents mechanical failures before broader validation. |
| Focused pytest / local quantitative checks | Inner-loop cheap | Fast feedback on changed behavior. |
| Ruff lint + format check | Repository checkpoint + final | Cheap and repository-wide. |
| Strict Pyright | Repository checkpoint + final | Currently inexpensive and catches public/type drift. |
| Current pytest suite | Repository checkpoint + final | Currently inexpensive enough to keep in the canonical gate. |
| Cognitive complexity | Repository checkpoint + final once Issue #7 lands | Intended to remain inexpensive; #7 owns implementation. |
| Formula, no-arbitrage, limiting-case checks | Model-specific; ordinary tests when cheap/deterministic | Mathematical evidence should travel with the model it protects. |
| Convergence/stability studies | Model-specific / quantitative | Make mandatory when the numerical method being changed needs them. |
| Stochastic/statistical validation | Model-specific / quantitative | Relevance-aware; deterministic seeds and explicit statistical semantics required. |
| Cross-method validation | Model-specific / quantitative | Valuable after independent methods exist. |
| Parameter recovery / out-of-sample / model-risk studies | Model-specific / quantitative | Future inverse/model-validation milestones must earn their exact policy. |
| Python/C++ parity | Not yet earned | No native implementation exists. |
| Blanket coverage threshold | Not yet earned | Add only when a meaningful target protects real production behavior. |
| Broad architecture/import tooling | Not yet earned beyond focused guards | Add when package-boundary pressure justifies machine enforcement. |
| Strict docs build | Not yet earned | Generated documentation is not yet a supported product surface. |
| Benchmark/profile blocking gate | Not yet earned | Performance policy remains profile-first and workload-specific. |
| Release/package smoke gate | Not yet earned | Add before a supported release surface requires it. |

## CI topology decision

Keep the current GitHub Actions topology simple:

```text
one quality job
→ checkout
→ Python setup with pip cache
→ editable development install
→ ./scripts/check_all
```

Do **not** currently add:

- a draft-fast / final-full workflow split;
- a second `check_all --fast` command;
- multiple jobs that duplicate setup;
- more caching machinery;
- path-trigger complexity for quantitative suites that do not exist yet.

The measured complete gate is too small for those mechanisms to buy meaningful wall-clock time today. Agent/local cadence offers the larger immediate saving.

Reconsider the split only when measurements show that repository-wide tests or earned quantitative guards make the complete checkpoint materially expensive. At that point, preserve a complete final candidate gate and stable required-check semantics, and make model-specific expensive validation relevance-aware.

## Development-efficiency implications

The preferred loop changes from the failure-prone pattern:

```text
edit
→ push
→ CI discovers formatting/type/local behavior issue
→ tiny cleanup push
→ restart setup + CI
```

into:

```text
coherent edit batch
→ fix
→ focused validation
→ complete local checkpoint
→ one meaningful push
→ CI confirms the checkpoint
```

At the current measured size, eliminating even one unnecessary CI rerun saves roughly one full workflow cycle (about 17 seconds of runner execution / about 25 seconds end-to-end in the sampled green M0A run) plus human/agent context switching. More importantly, the workflow reaches Pyright and pytest locally instead of repeatedly stopping at the first mechanical Ruff failure.

This is a cadence optimization, not a lower quality bar.

## Revisit triggers

Re-measure this policy when any of the following becomes true:

- `./scripts/check_all` is no longer a small checkpoint;
- pytest grows into materially different cost tiers;
- Monte Carlo, Heston, calibration, empirical, model-risk, or native parity studies become substantial;
- dependency installation becomes a significant fraction of a much longer workflow;
- CI queue or duplicated setup becomes a demonstrated bottleneck;
- path relevance can be defined from real model/test ownership rather than imagined future packages;
- flaky stochastic tests appear despite deterministic test design.

Prefer measured simplicity until one of those pressures is real.
