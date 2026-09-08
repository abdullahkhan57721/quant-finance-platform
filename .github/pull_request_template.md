## Summary

What changed and why?

Closes #

## Architecture / public-contract impact

Describe any new or changed public types, boundaries, dependency direction, ownership/mutability semantics, or explicitly deferred architecture.

If none, say so.

## Quantitative / modeling impact

Describe affected formulas, assumptions, units/conventions, stochastic semantics, market/model distinctions, calibration semantics, or validation claims.

If none, say so.

## Validation cadence checklist

Follow `docs/development/validation_cadence.md`. During draft work, leave incomplete items unchecked and update them only at meaningful checkpoints. For a genuinely inapplicable item, mark it N/A and explain why in the relevant section below.

### Development / checkpoint

- [ ] Ran `./scripts/fix` after the final coherent Python changes, or documented why it is N/A.
- [ ] Ran focused behavioral tests and focused quantitative/numerical checks appropriate to the changed behavior, or documented why they are N/A.

### Final candidate

- [ ] `./scripts/check_all` passed at the exact candidate head.
- [ ] Full required CI passed on that same candidate head.
- [ ] Ticket-specific quantitative/numerical evidence is complete when relevant, or N/A is justified below.
- [ ] Ticket-specific manual verification is complete when useful, or N/A is justified below.
- [ ] The exact reviewed candidate head is recorded below.
- [ ] `main` / base freshness was re-checked when concurrent work could affect this PR's assumptions.

### Post-merge completion

- [ ] Merged `main` was verified after squash merge. Leave this unchecked until the merge actually occurs.

## Verification

List the exact checks run at the reviewed head and record that head explicitly.

```text
Candidate head:
./scripts/check_all
```

Add focused and model-specific financial/numerical validation when relevant.

## Manual verification

```text
Scenario:
Action:
Expected:
Observed:
```

If manual verification is not useful for this change, explain why.

## Performance evidence

If this PR makes a performance claim, include:

- reproducible workload;
- baseline and comparison head;
- profiling evidence identifying the hotspot;
- repeated-run comparison method (prefer medians);
- runtime/memory/structural metrics relevant to the claimed layer;
- readability/auditability tradeoffs.

If performance is not in scope, state that no performance claim is made.

## Validation-cadence / CI-policy impact

Does this PR fire any revisit trigger in `docs/development/validation_cadence.md` (for example by materially changing gate cost or introducing a genuinely different validation cost tier)?

If yes, include the measurement/evidence and link the follow-up Issue or policy change. If no, state that no documented revisit trigger fired. Do not redesign CI speculatively.

## Documentation impact

What durable docs, quantitative conventions, ADRs, examples, or README claims changed? If none, explain why documentation remains accurate.

## Risks / follow-ups

List known limitations, deferred decisions, and follow-up Issues. Do not hide out-of-scope discoveries inside this PR.

## Recovery checkpoint

```text
Implemented:
Remaining:
Current blocker:
Last verified head:
Last CI result:
Next action:
```
