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

Follow `docs/development/validation_cadence.md`. During draft work, leave unfinished items unchecked. Mark genuinely inapplicable items N/A with a reason in the relevant section below.

- [ ] Ran `./scripts/fix` after the final coherent Python changes, or N/A is justified.
- [ ] Ran focused behavioral and quantitative/numerical checks appropriate to the change, or N/A is justified.
- [ ] `./scripts/check_all` passed at the exact candidate head.
- [ ] Full required CI passed on that same candidate head.
- [ ] Ticket-specific quantitative/numerical and manual evidence below is complete or explicitly N/A.
- [ ] Exact candidate head is recorded below; `main` / base freshness was re-checked when concurrent work could affect assumptions.
- [ ] After squash merge, merged `main` was verified. Leave this unchecked until merge actually occurs.

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

Did this PR fire a revisit trigger in `docs/development/validation_cadence.md`, such as materially changing gate cost or creating a distinct validation cost tier? If yes, include evidence and link the follow-up Issue/policy change. If no, say no trigger fired; do not redesign CI speculatively.

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
