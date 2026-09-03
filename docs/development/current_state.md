# Current State

## Status

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

The repository now contains its first concrete finance implementation and theoretical
validation evidence while preserving the bootstrap rule that new abstractions must be
earned by real consumers.

## What exists

The M0 engineering/collaboration foundation remains in place:

- `src/`-layout package and project metadata;
- Ruff, formatting, strict Pyright, Complexipy cognitive-complexity enforcement,
  pytest, and GitHub Actions through `./scripts/check_all`;
- repository workflow/agent rules, architecture guardrails, quantitative-convention
  register, ADR policy, and Issue/PR recovery templates.

M1 adds:

- immutable `EuropeanOption` contracts with explicit `OptionRight` call/put semantics;
- calendar-date expiry and valuation-date semantics;
- M1-local Actual/365 Fixed model time;
- narrow maturity-dependent `DiscountFactorProvider` semantics;
- immutable `FlatContinuousDiscountCurve` as the first concrete discounting provider;
- immutable valuation-ready `MarketEnvironment` containing spot plus distinct
  risk-free and continuous dividend/carry discounting;
- immutable `BlackScholesParameters` with annualized decimal volatility;
- pure analytic `black_scholes_present_value(...)` valuation;
- explicit expiry/zero-volatility/zero-spot/zero-strike handling;
- mathematical traceability in `docs/models/black_scholes.md`;
- executable evidence for published benchmark values, put-call parity,
  no-arbitrage bounds, limiting cases, domain validation, day count, compounding,
  carry direction, and negative rates.

## Boundaries learned from M1

The first vertical resolved several bootstrap hypotheses without creating a general
finance framework:

```text
EuropeanOption
      +
MarketEnvironment
      +
BlackScholesParameters
      ↓
black_scholes_present_value
      ↓
theoretical validation evidence
```

Important current decisions:

- contract expiry is a date rather than an anonymous maturity float;
- valuation-ready discounting crosses the valuation boundary as discount factors,
  while the concrete flat curve owns continuous-compounding semantics;
- volatility is model information, not an intrinsic field of `MarketEnvironment`;
- no `MarketSnapshot` was needed because M1 consumes no observed market data;
- no `BlackScholesModel` object was added merely to wrap one valuation formula;
- no generic `ValuationResult` was added because the first completed consumer only
  requires one scalar present value;
- focused tests and traceability documentation provide M1 validation evidence without
  inventing a generic validation subsystem.

## Quality-tool maturity

The canonical quality gate now covers:

```text
Complexipy cognitive complexity (max 15)
Ruff lint
Ruff format check
strict Pyright
pytest
```

The complexity guard targets production code under `src/qf_platform` and is routed
through the same `./scripts/check_all` entry point used by GitHub Actions.

Coverage thresholds, Import Linter contracts, strict docs builds,
benchmark/profile infrastructure, and native-backend tooling remain deferred until
concrete code or architecture gives them meaningful invariants to enforce.

## Deliberately absent

The following still do not exist and should not be invented without real consumers:

- provenance-bearing `MarketSnapshot` / live market-data clients;
- binomial or Monte Carlo valuation;
- Greeks and finite-difference sensitivities;
- delta-hedging/replication studies;
- implied-volatility inversion and volatility-surface analysis;
- generic model/pricer/validation/risk hierarchies;
- generic valuation-result or experiment frameworks;
- trade/portfolio infrastructure;
- Heston/calibration infrastructure;
- native/C++ backends.

## Next objective

Begin **M2 — Independent Valuation and Greeks** through the normal
Issue → branch → PR → CI → exact-head review → squash-merge workflow.

M2 should use the M1 analytical Black-Scholes path as a reference, then add genuinely
independent CRR/binomial and Monte Carlo valuation plus analytic/numerical Greeks and
convergence evidence. Shared abstractions should be extracted only when those second
consumers demonstrate the same responsibility.
