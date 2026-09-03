## Summary

What changed and why?

Closes #

## Architecture / public-contract impact

Describe any new or changed public types, boundaries, dependency direction, ownership/mutability semantics, or explicitly deferred architecture.

If none, say so.

## Quantitative / modeling impact

Describe affected formulas, assumptions, units/conventions, stochastic semantics, market/model distinctions, calibration semantics, or validation claims.

If none, say so.

## Verification

List the exact checks run at the reviewed head.

```text
./scripts/check_all
```

Add model-specific financial/numerical validation when relevant.

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
