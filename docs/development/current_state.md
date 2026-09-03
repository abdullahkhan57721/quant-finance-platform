# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

The repository also has the durable collaboration/convention layer needed to carry forward the engineering lessons adopted during bootstrap: information-lifetime guidance, an explicit quantitative-convention authority, ADR policy, reusable Issue/PR templates, canonical local quality scripts, and explicit ChatGPT/Codex work allocation.

No finance-domain implementation has been added yet.

## What exists

The repository establishes:

- a `src/`-layout Python package;
- package metadata in `pyproject.toml`;
- pytest, Ruff, and strict Pyright configuration;
- a package import smoke test;
- GitHub Actions CI running the canonical local quality gate;
- `scripts/fix` and `scripts/check_all` as local quality entry points;
- repository ignore rules;
- root agent/navigation guidance;
- the accepted M0–M9 validation-first roadmap;
- architecture, provenance, reproducibility/RNG, validation, and future Python/C++ guardrails;
- `docs/development/engineering_principles.md` for engineering/collaboration rationale;
- `docs/quantitative_conventions.md` as the authority for committed and deliberately deferred quantitative conventions;
- lightweight ADR guidance/template under `docs/decisions/`;
- reusable implementation Issue and pull-request templates with scope, verification, quantitative, ownership, and recovery fields.

## Quality-tool maturity

The initial gate intentionally remains lean:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

Coverage thresholds, cognitive-complexity guards, Import Linter contracts, strict docs builds, quantitative contract suites, benchmark/profile infrastructure, and release smoke checks should be added only when concrete code or architecture gives them something meaningful to enforce.

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

Do not settle those details in advance when implementation evidence can decide them. Use `docs/quantitative_conventions.md` to distinguish decisions that become project-wide from choices that remain local.
