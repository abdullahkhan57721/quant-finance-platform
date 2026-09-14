# Repository-Driven Milestone Orchestration

## Purpose

This repository carries the durable state needed to continue development without a large chat-generated milestone prompt.

Use these responsibilities consistently:

```text
AGENTS.md                         standing operating contract
current_state.md                 what is true now / current execution frontier
roadmap.md                       milestone dependency graph and metadata
milestones/<ID>.md               one milestone's durable execution specification
GitHub Issue                     concrete activated work unit
Pull request                     in-progress/review/recovery state
main + tests + CI                executable truth
ADRs / architecture docs         durable architectural decisions
Git history                      historical record
```

A status document is navigation, not an authority above executable repository truth. Always verify live `main`, Issues, PRs, and required CI before acting on prose.

## Milestone states

Use exactly these states unless a later repository decision supersedes them:

| State | Meaning |
| --- | --- |
| `BLOCKED` | The milestone is valid, but at least one required dependency, decision, or external condition is incomplete. |
| `READY` | All required dependencies are `MERGED`; no active/review work duplicates it; it may begin. |
| `ACTIVE` | Implementation has begun in its Issue/branch/worktree. |
| `REVIEW` | Implementation is complete enough for final PR review/validation, but repository-defined completion is not yet satisfied. |
| `MERGED` | The required PR was squash-merged and required post-merge `main` verification completed. Code existing locally or a closed/unmerged PR is not `MERGED`. |
| `PAUSED` | Work intentionally stopped without being invalidated; record the reason and restart condition in the Issue/PR. |
| `SUPERSEDED` | The work is intentionally replaced by another decision/work unit; preserve history and identify the replacement. |

Normal transition:

```text
BLOCKED -> READY -> ACTIVE -> REVIEW -> MERGED
```

Additional transitions:

- `ACTIVE` or `REVIEW` -> `BLOCKED` when a newly discovered prerequisite must land first;
- `ACTIVE` or `REVIEW` -> `PAUSED` when work is intentionally suspended without invalidating it;
- any non-`MERGED` state -> `SUPERSEDED` when repository truth explicitly replaces the work;
- failed validation does not create a new state by itself: keep the milestone `ACTIVE` or `REVIEW`, record the failure in the PR recovery checkpoint, fix it, and revalidate the new exact head.

Do not infer `READY` from code that merely looks finished. Every `depends_on` milestone must be verified `MERGED` by repository-defined completion semantics.

## Deterministic selection policy

At the beginning of a development session:

1. orient from `AGENTS.md` and its required sources;
2. fetch current `main` and inspect open Issues/PRs;
3. reconcile any stale `current_state.md`/`roadmap.md` status against repository truth;
4. form the eligible set:

```text
status == READY
AND every depends_on milestone == MERGED
AND no active/review Issue or PR already owns the same work
```

5. select from that set by:

```text
1. lower numeric priority (P0 before P1 before P2 ...)
2. roadmap order
3. greater dependency-unblocking value
4. lower unstable-shared-contract risk when otherwise equal
```

6. read the selected milestone spec;
7. create or reuse its Issue, branch, worktree, and PR through the normal repository workflow.

If the eligible set is empty, report the concrete blockers rather than inventing work.

## Parallel frontier

Multiple READY milestones may form a parallel frontier only when all of the following hold:

- neither depends on the other;
- shared public contracts are already stable;
- they do not require unresolved architecture from each other;
- they can use separate branches/worktrees;
- likely file overlap is small or explicitly coordinated;
- each work unit has its own Issue and PR.

Do not parallelize merely because two statuses say `READY`.

When safe, report the frontier explicitly, for example:

```text
READY FRONTIER
M3    safe in worktree A
M4    safe in worktree B
UI2   safe only if it consumes already-merged M2 contracts
```

If branches overlap in durable status files, rebase/update from `main` before final validation and reconcile those files from current repository truth.

## Branch/worktree contract

Default to one milestone per branch/worktree.

Branch names should remain short and traceable to the Issue or milestone, for example:

```text
m9-portfolio-release
ui6-...
issue-7-complexity-gate
workflow/48-repo-driven-orchestration
```

Before implementation:

- start from current `main`;
- inspect open PRs for concurrent changes to the same contracts/files;
- do not reuse a stale branch as an implementation base unless the Issue explicitly requires it.

Before final review/merge:

- update/reconcile against current `main` when concurrent work has landed;
- rerun all required validation on the exact candidate head;
- review the exact diff for correctness, architecture, documentation, test quality, and accidental scope expansion;
- do not rely on CI from an earlier head.

After merge:

- verify the squash merge on `main`;
- verify required post-merge CI;
- update `current_state.md`, roadmap metadata, milestone metadata, and follow-on states when repository truth changed;
- close/confirm the Issue as completed;
- clean up the worktree/branch when supported;
- reevaluate the graph before starting anything else.

## Human merge gate

The default autonomy boundary is:

```text
select -> implement -> test -> self-review -> PR -> exact-head validation
       -> ready-to-merge -> human/repository merge gate
       -> post-merge verification -> unlock next work
```

Do not enable recursive/autonomous merging merely to speed the roadmap. If a future repository rule explicitly permits automated squash merging under defined conditions, record those conditions centrally before using them.

## Active PR / duplicate-work rule

An open Issue/PR may make prose stale immediately.

Before creating new work:

- search open PRs and Issues;
- if the intended milestone already has `ACTIVE` or `REVIEW` work, continue/recover that work unit instead of creating a duplicate;
- read its recovery checkpoint and exact-head state;
- if it is abandoned or superseded, update/close it explicitly before replacing it.

## Status-update responsibilities

When repository truth changes materially:

- `current_state.md`: update current merged/active/review/blocked/READY frontier and temporary constraints;
- `roadmap.md`: update status/dependency/Issue/PR/spec metadata and newly unlocked milestones;
- milestone spec: update only if the milestone's durable scope/acceptance contract changed; do not use it as a progress log;
- Issue: concrete scope/acceptance and blockers;
- PR: recovery checkpoint, exact-head validation, review state;
- ADR/architecture docs: only for durable architectural decisions.

Avoid volatile CI run IDs and temporary SHAs in `current_state.md` unless they are needed to explain a current blocker. Those belong in the PR.

## Stale-document rule

If documents disagree:

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
conversation memory
```

Fix stale docs in the active work unit when the discrepancy is material, but do not blindly follow stale status text.

## Scenario checks

### Fresh agent

A fresh agent reading `AGENTS.md`, `current_state.md`, `roadmap.md`, and the selected milestone spec can determine the next work without prior chat context.

### Blocked milestone

`roadmap.md` names the unmet `depends_on` or blocker; the milestone stays `BLOCKED` until repository-defined completion is verified.

### Parallel frontier

`parallel_with` is permission to evaluate concurrency, not proof. The agent must also check live shared-contract and file-overlap risk.

### Existing active PR

Live PR/Issue state overrides a stale `READY` row. Recover the existing work unit rather than duplicating it.

### Merge

A milestone becomes `MERGED` only after squash merge plus required post-merge verification. Then update state/graph and recompute newly READY work.

### Stale documentation

Executable/live repository truth wins; correct the stale navigation text as part of the current work when material.

## Minimal continuation instruction

The repository is designed so this is sufficient:

```text
Continue development from current main.

Use AGENTS.md, current_state.md, roadmap.md, milestone specifications,
Issues/PRs, and repository truth as authoritative.

Determine the highest-priority READY milestone, verify its dependencies,
and execute it through the repository's normal PR and validation workflow.

If multiple independent milestones form a safe parallel frontier, report
that frontier and use isolated worktrees/agents where supported.

Do not rely on prior chat context.
```
