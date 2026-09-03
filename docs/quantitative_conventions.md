# Quantitative Conventions

## Purpose

This document is the authoritative register for project-wide quantitative representation conventions.

A convention may be **committed**, **explicitly deferred**, or **local to a specific API/study**. What is not allowed is a consequential convention remaining implicit across a public boundary.

The project is still pre-M1, so this register intentionally contains more deferred decisions than fixed finance conventions.

## Decision statuses

- **Committed** — project-wide rule; public implementations should follow it unless superseded by a deliberate repository decision.
- **Deferred** — not yet fixed project-wide; the first real consumer should make the decision explicit and update this document if the choice becomes shared.
- **Local** — intentionally specific to one method/study; encode it in that API/config/result rather than promoting it globally.

## Committed cross-cutting conventions

### Explicit quantitative meaning at public boundaries

Public quantitative inputs must make their semantic meaning clear through type, field name, documentation, or configuration.

Avoid APIs where an anonymous float could ambiguously mean one of several conventions, for example:

```text
0.05
→ 5% simple annual rate?
→ 5% continuously compounded rate?
→ 5 percentage points?
→ a discount factor-related quantity?
```

This rule does not require a wrapper type for every number. It requires ambiguity to be removed where it affects correctness.

### No hidden project-wide numerical tolerance

There is no universal magic tolerance for finance/numerical tests.

Every meaningful tolerance should be justified by the evidence type involved, such as:

- analytical floating-point error;
- discretization error;
- Monte Carlo standard error;
- optimizer convergence;
- market quote precision;
- backend parity.

Prefer tolerances derived from the expected error mechanism rather than copied globally.

### Explicit stochastic ownership

Production stochastic APIs must not depend on ambient global RNG state.

Use explicitly owned/configured RNG state. Record seed/RNG information in reproducible studies when applicable.

Equal integer seeds across Python/C++ are **not** a contract for identical random streams. Use shared pre-generated random inputs when strict kernel parity is required.

### Observed and model-generated values remain distinguishable

Do not overwrite or silently reinterpret observed market values as model outputs.

Preserve provenance-bearing observations separately from derived/model-generated quantities whenever both participate in validation or research.

### Reproducible core tests do not depend on live market services

Live data can support research and manual workflows, but core CI tests should use deterministic fixtures, synthetic data, or curated snapshots whose provenance/licensing permits repository use.

## Explicitly deferred finance conventions

These decisions should be settled by the first milestones that create real consumers. Until then, do not spread a local choice across the codebase as if it were canonical.

| Convention | Status | First expected pressure | Guidance until settled |
| --- | --- | --- | --- |
| Contract expiry representation | Deferred | M1 European option | Prefer explicit semantics; architecture currently hypothesizes date-based expiry but has not committed an API. |
| Valuation date representation | Deferred | M1 | Keep explicit wherever maturity/year-fraction depends on it. |
| Year-fraction API | Deferred | M1 | Do not pass anonymous maturity floats across broad public APIs before deciding whether/how dates are converted. |
| Day-count convention | Deferred | M1 | Must be explicit if calendar dates are converted to year fractions. |
| Business-day/calendar handling | Deferred | M1/M4 | Do not invent a full calendar framework until concrete contract/data needs justify it. |
| Interest-rate representation | Deferred | M1 | Do not silently assume scalar `r` is the permanent public representation. |
| Compounding convention | Deferred | M1 | State explicitly wherever rates are accepted. |
| Discount-factor/curve representation | Deferred | M1 | Architecture suggests evaluating a narrow maturity-dependent capability; exact contract is not decided. |
| Dividend/carry representation | Deferred | M1 | Do not silently choose continuous yield vs discrete cash dividends as a universal assumption. |
| Spot vs forward input semantics | Deferred | M1/M4 | Name and document explicitly; do not make them interchangeable. |
| Volatility representation/units | Deferred | M1/M2 | Public APIs must make decimal/percentage and annualization semantics unambiguous once introduced. |
| Option type/right encoding | Deferred | M1 | Exact enum/type naming belongs to the first instrument design. |
| Price vs present-value terminology | Deferred | M1 | Choose terminology with the first valuation result contract and use it consistently. |
| Greek sign conventions | Deferred | M2 | Record each Greek's differentiation variable and sign convention. |
| Greek scaling/units | Deferred | M2 | Make per-unit vs per-1%-point conventions explicit; avoid unexplained presentation scaling in core results. |
| Monte Carlo confidence level/reporting | Deferred | M2 | Encode explicitly in result/study configuration rather than assuming one global reporting level. |
| Array axis/order conventions for numerical kernels | Deferred | M2/M5 | Define only when vectorized/compiled kernels create a shared boundary. |
| Market timestamp timezone convention | Deferred | M4 | Must become explicit before real-market ingestion. |
| Missing/bad quote policy | Deferred | M4 | Preserve raw observations/provenance; normalization/cleaning policy must be explicit and testable. |

## Decision rules for M1 and later

When a milestone encounters a deferred convention:

1. Identify the concrete consumer and why the choice matters.
2. Compare realistic alternatives and failure modes.
3. Decide whether the convention is local or project-wide.
4. Encode the convention in types/configuration/documentation so it cannot be silently reinterpreted.
5. Add tests that distinguish the chosen semantics from plausible wrong interpretations.
6. Update this register if the choice becomes project-wide.
7. Use an ADR only when the decision is durable, consequential, and not obvious from code plus this document.

Do not force a global convention merely to make this table complete.

## Formula traceability convention

Once mathematical model code exists, important formula implementations should document or link enough information to recover:

- the source/reference or project derivation;
- notation mapping from the source into code;
- assumptions and parameter domain;
- units/conventions involved;
- limiting cases or identities used for validation;
- tests that provide independent evidence.

The exact documentation location can vary by subsystem; the traceability requirement is the invariant.

## Market-data provenance convention

When real market data arrives, preserve as applicable and legally permitted:

- provider/source;
- as-of timestamp;
- retrieval timestamp;
- raw artifact or content hash;
- normalization/transformation version;
- licensing/redistribution notes.

If raw data cannot be redistributed, prefer a reproducible retrieval/processing recipe plus deterministic synthetic or curated fixtures over committing restricted data.

## Changing a committed convention

A committed convention can change when evidence justifies it.

A change should normally include:

- the motivation and affected public contracts;
- migration/compatibility consequences;
- tests distinguishing old and new semantics;
- documentation updates in the same PR;
- an ADR when the decision is durable and consequential enough to require historical rationale.

Repository truth should evolve rather than preserving a bad convention for historical consistency.
