# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

Completed durable work unit:

- Issue #1 — Bootstrap repository, quality gates, and architecture guardrails
- PR #2 — Bootstrap repository, quality gates, and architecture guardrails

No finance-domain implementation has been added yet.

## What exists

The repository establishes:

- a `src/`-layout Python package;
- package metadata in `pyproject.toml`;
- pytest, Ruff, and strict Pyright configuration;
- a package import smoke test;
- GitHub Actions CI running the core quality gate;
- repository ignore rules;
- root agent/navigation guidance;
- the accepted M0–M9 validation-first roadmap;
- architecture, provenance, reproducibility/RNG, validation, and future Python/C++ guardrails.

## Deliberately absent

The following do not exist yet and should not be invented without real consumers:

- `EuropeanOption`;
- Black-Scholes pricing;
- market snapshots/environments;
- model or valuation hierarchies;
- generic calibration/risk/validation interfaces;
- trade/portfolio infrastructure;
- market-data clients;
- experiment frameworks;
- native/C++ backends.

## Next objective

Begin **M1 — European options and Black-Scholes reference vertical** using the normal Issue → branch → PR → CI → squash-merge workflow.

M1 should introduce the first concrete finance vertical and let actual Black-Scholes consumers pressure-test the bootstrap architecture rather than pre-creating a general finance framework.

## M1 design questions

Expected questions include:

- what is the smallest correct representation of a European option contract;
- how valuation dates, expiries, day-count conventions, discounting, dividends/financing, and spot should be represented;
- whether a narrow maturity-dependent discount-factor capability is justified immediately;
- how Black-Scholes model structure and its parameters should be separated;
- what immutable result type is warranted by the first real valuation consumer;
- which no-arbitrage, limiting-case, and numerical checks should become executable validation evidence.

Do not settle those details in advance when implementation evidence can decide them.
