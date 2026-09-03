# Current State

## Status

The repository is in **M0 — Engineering Bootstrap**.

Active durable work unit:

- Issue #1 — Bootstrap repository, quality gates, and architecture guardrails
- Branch: `issue-1-bootstrap`

No finance-domain implementation has been added yet.

## What exists

The bootstrap branch currently establishes:

- a `src/`-layout Python package;
- package metadata in `pyproject.toml`;
- pytest, Ruff, and Pyright configuration;
- a package import smoke test;
- GitHub Actions CI;
- repository ignore rules;
- root agent/navigation guidance;
- development and architecture documentation.

## Deliberately absent

The following do not exist yet and should not be invented during M0:

- `EuropeanOption`;
- Black-Scholes pricing;
- market snapshots/environments;
- model or valuation hierarchies;
- generic calibration/risk/validation interfaces;
- trade/portfolio infrastructure;
- market-data clients;
- experiment frameworks;
- native/C++ backends.

## Immediate objective

Complete Issue #1, verify the exact PR head through CI, squash-merge it, and verify `main`.

Only after M0 is merged should the project begin M1, whose job is to introduce the first concrete finance vertical and let real consumers pressure-test the bootstrap architecture.

## Next milestone

**M1 — European options and Black-Scholes reference vertical**

Expected questions for M1 include:

- what is the smallest correct representation of a European option contract;
- how valuation dates, expiries, day-count conventions, discounting, dividends/financing, and spot should be represented;
- whether a narrow maturity-dependent discount-factor capability is justified immediately;
- how Black-Scholes model structure and its parameters should be separated;
- what immutable result type is warranted by the first real valuation consumer;
- which no-arbitrage and limiting-case checks should become executable validation evidence.

Do not settle those details in advance when implementation evidence can decide them.
