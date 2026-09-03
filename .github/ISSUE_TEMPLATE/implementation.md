---
name: Implementation work unit
about: Plan architecture-sensitive quantitative or engineering implementation
labels: ''
assignees: ''
---

## Goal

What concrete capability should exist when this Issue is complete?

## Why

Why is this work justified now? What observed limitation, roadmap milestone, validation need, or concrete consumer creates the pressure?

## Dependencies

- ...

## Allowed areas

- ...

## Do not touch

- ...

## Quantitative assumptions / conventions

List the project-wide conventions this work depends on and link `docs/quantitative_conventions.md` where relevant.

Call out any convention that is still deferred and must be decided or kept local in this Issue.

## Public-contract impact

What public types, functions, data/result contracts, or cross-subsystem boundaries may be introduced or changed?

If none, say so.

## Ownership / mutability semantics

For consequential inputs, runtime state, caches, stochastic state, and results:

- who owns them;
- whether they are mutable;
- whether mutation is domain semantics or internal orchestration;
- what becomes committed evidence.

## Likely wrong interpretations / traps

List plausible implementations that could satisfy the surface request while violating the intended architecture, quantitative semantics, scope, or validation strategy.

- ...

## Requirements

1. ...

## Non-goals

- ...

## Acceptance criteria

- [ ] ...

## Automated verification

List the exact tests/checks/evidence that should pass.

```text
./scripts/check_all
```

Add model-specific identities, convergence, recovery, stochastic, parity, or benchmark checks when the work requires them.

## Manual verification

State a small public-workflow sanity check.

```text
Scenario:
Action:
Expected:
Observed:
```

Use `Observed: pending` until verification is actually performed.

## Performance evidence

Is performance part of this Issue?

- [ ] No — performance is not a claim/acceptance criterion.
- [ ] Yes — specify reproducible workload, baseline, profiling evidence, target layer, and comparison method.

Do not add performance work based only on intuition.

## Documentation impact

Which durable docs, quantitative conventions, architecture docs, ADRs, examples, or README claims should change in the same PR?

## Follow-up boundary

What related discoveries or future work explicitly belong in separate Issues rather than expanding this one?
