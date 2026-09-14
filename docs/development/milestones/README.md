# Milestone Specifications

This directory contains durable specifications for active/future roadmap milestones that need more execution detail than belongs in `roadmap.md`.

Do not create a separate file for every historical milestone merely for symmetry. Completed milestone history may remain in the roadmap, model docs, Issues, PRs, ADRs, and Git history when those already preserve the necessary record.

A milestone spec is a durable execution contract, not a progress log and not a replacement for the concrete GitHub Issue.

Use this structure when applicable:

```text
# <ID> — <Title>

Status
Priority

## Purpose
## Central question
## Dependencies
## Parallelization
## Required orientation
## Scope
## Non-goals
## Architecture constraints
## Deliverables
## Validation
## Acceptance criteria
## Completion procedure
## Follow-on unlocks
```

Global rules such as repository orientation, Issue -> branch -> PR flow, canonical quality gates, exact-head validation, squash merge, post-merge verification, and worktree/concurrency behavior belong in `AGENTS.md` and `docs/development/orchestration.md`. Do not paste them into every milestone spec.

`roadmap.md` is the authoritative execution graph and links to specs. `current_state.md` reports the current frontier. Repository truth and live Issues/PRs override stale prose status.
