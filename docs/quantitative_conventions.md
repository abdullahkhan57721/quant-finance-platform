# Quantitative Conventions

## Purpose

This document is the authoritative register for project-wide quantitative
representation conventions.

A convention may be **committed**, **explicitly deferred**, or **local to a specific
API/study**. What is not allowed is a consequential convention remaining implicit
across a public boundary.

M1 has resolved the conventions required by the first European-option/Black-Scholes
consumer while deliberately leaving unrelated rates, calendar, market-data, Greek,
and numerical-kernel conventions open.

## Decision statuses

- **Committed** — project-wide rule; public implementations should follow it unless
  superseded by a deliberate repository decision.
- **Deferred** — not yet fixed project-wide; the first real consumer should make the
  decision explicit and update this document if the choice becomes shared.
- **Local** — intentionally specific to one method/study; encode it in that
  API/config/result rather than promoting it globally.

## Committed cross-cutting conventions

### Explicit quantitative meaning at public boundaries

Public quantitative inputs must make their semantic meaning clear through type, field
name, documentation, or configuration.

Avoid APIs where an anonymous float could ambiguously mean one of several conventions,
for example:

```text
0.05
→ 5% simple annual rate?
→ 5% continuously compounded rate?
→ 5 percentage points?
→ a discount-factor-related quantity?
```

This rule does not require a wrapper type for every number. It requires ambiguity to
be removed where it affects correctness.

### No hidden project-wide numerical tolerance

There is no universal magic tolerance for finance/numerical tests.

Every meaningful tolerance should be justified by the evidence type involved, such as
analytical floating-point error, discretization error, Monte Carlo standard error,
optimizer convergence, market quote precision, or backend parity.

### Explicit stochastic ownership

Production stochastic APIs must not depend on ambient global RNG state. Use explicitly
owned/configured RNG state and record seed/RNG information in reproducible studies when
applicable.

Equal integer seeds across Python/C++ are not a contract for identical streams. Use
shared pre-generated random inputs when strict kernel parity is required.

### Observed and model-generated values remain distinguishable

Do not overwrite or silently reinterpret observed market values as model outputs.
Preserve provenance-bearing observations separately from derived/model-generated
quantities whenever both participate in validation or research.

### Reproducible core tests do not depend on live market services

Live data can support research and manual workflows, but core CI tests use deterministic
fixtures, synthetic data, or curated snapshots whose provenance/licensing permits use.

## M1-resolved and still-deferred finance conventions

| Convention | Status | Current decision / guidance |
| --- | --- | --- |
| Contract expiry representation | Committed | European-option expiry is a `datetime.date`. M1 assigns no time-of-day or business-day-adjustment semantics. |
| Valuation date representation | Committed | Valuation-ready market state owns an explicit `datetime.date`. |
| Year-fraction API | Local | M1 exposes `actual_365_fixed_year_fraction(start, end)` for its equity-option reference vertical rather than passing broad anonymous maturity floats. |
| Day-count convention | Local | M1 Black-Scholes/flat discounting use Actual/365 Fixed: actual calendar days divided by exactly 365, including leap years. This is not a universal rates day-count framework. |
| Business-day/calendar handling | Deferred | No adjustment/calendar framework exists. Add one only when a contract/data consumer requires it. |
| Interest-rate representation | Deferred | No project-wide rate object is committed. Black-Scholes valuation consumes discount factors rather than a naked scalar `r`. |
| Compounding convention | Local | `FlatContinuousDiscountCurve` accepts a finite continuously compounded annual rate and computes `exp(-rT)`. Other future discounting implementations need not use that representation. |
| Discount-factor/curve representation | Committed | Valuation may depend on the narrow `DiscountFactorProvider` capability: one valuation date plus maturity-dependent positive finite discount factors. No general rates/curve-building hierarchy is implied. |
| Dividend/carry representation | Local | M1 supplies a second discount-factor provider for deterministic continuous proportional dividend/carry. Discrete cash dividends remain deferred. |
| Spot vs forward input semantics | Local | M1 `MarketEnvironment.spot` is explicitly spot. No forward-input API exists yet. |
| Volatility representation/units | Local | `BlackScholesParameters.annualized_volatility` is non-negative annualized standard deviation in decimal units; `0.20` means 20%. M2 may reveal whether a broader shared volatility contract is warranted. |
| Option type/right encoding | Committed | European call/put rights use `OptionRight`, not booleans or magic strings internally. |
| Price vs present-value terminology | Committed | Core valuation APIs use `present_value` terminology for discounted model values. |
| Greek sign conventions | Deferred | M2 must record each Greek's differentiation variable and sign convention. |
| Greek scaling/units | Deferred | M2 must make per-unit vs percentage-point presentation explicit. |
| Monte Carlo confidence level/reporting | Deferred | M2 should encode this in concrete result/study configuration rather than assume one global level. |
| Array axis/order conventions for numerical kernels | Deferred | Define only when vectorized/compiled kernels create a shared boundary. |
| Market timestamp timezone convention | Deferred | Must become explicit before real-market ingestion in M4. |
| Missing/bad quote policy | Deferred | Preserve raw observations/provenance; M4 normalization/cleaning policy must be explicit and testable. |

## M1 interpretation notes

The committed discount-factor boundary is deliberately narrower than a yield-curve
framework. `FlatContinuousDiscountCurve` is the first concrete provider, not the
project-wide definition of an interest rate or curve.

Likewise, the two M1 discount-factor inputs have distinct economic roles:

```text
risk-free discounting
!=
continuous dividend/carry discounting
```

The shared protocol reflects the same maturity-to-discount-factor responsibility; it
does not claim that financing and dividends are the same market object.

Volatility belongs to `BlackScholesParameters`, not `MarketEnvironment`, so the same
valuation-ready market state is not silently tied to one model's parameterization.

## Decision rules for later milestones

When a milestone encounters a deferred convention:

1. Identify the concrete consumer and why the choice matters.
2. Compare realistic alternatives and failure modes.
3. Decide whether the convention is local or project-wide.
4. Encode the convention so it cannot be silently reinterpreted.
5. Add tests that distinguish the chosen semantics from plausible wrong
   interpretations.
6. Update this register if the choice becomes project-wide.
7. Use an ADR only when the decision is durable, consequential, and not obvious from
   code plus this document.

Do not force a global convention merely to make this table complete.

## Formula traceability convention

Important formula implementations should document or link enough information to
recover:

- the source/reference or project derivation;
- notation mapping from the source into code;
- assumptions and parameter domain;
- units/conventions involved;
- limiting cases or identities used for validation;
- tests that provide independent evidence.

For M1 Black-Scholes, see `docs/models/black_scholes.md`.

## Market-data provenance convention

When real market data arrives, preserve as applicable and legally permitted:

- provider/source;
- as-of timestamp;
- retrieval timestamp;
- raw artifact or content hash;
- normalization/transformation version;
- licensing/redistribution notes.

If raw data cannot be redistributed, prefer a reproducible retrieval/processing recipe
plus deterministic synthetic or curated fixtures over committing restricted data.

## Changing a committed convention

A committed convention can change when evidence justifies it. A change should normally
include the motivation and affected public contracts, migration consequences,
discriminating tests, documentation updates in the same PR, and an ADR when historical
rationale is important.

Repository truth should evolve rather than preserving a bad convention for historical
consistency.
