# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Pricing Composition Foundation is complete.** It intentionally supersedes the bootstrap rule that foundational pricing semantics must wait for two concrete consumers. The exception is narrow and recorded in ADR 0001.

The next finance milestone is **M1 — European Options & Black-Scholes Reference Vertical**, implemented as the first concrete specialization of the M0A pricing core.

## What exists

The repository establishes:

- a `src/`-layout Python package;
- package metadata in `pyproject.toml`;
- pytest, Ruff, and strict Pyright configuration;
- GitHub Actions CI invoking the canonical local quality gate;
- `scripts/fix` and `scripts/check_all` as local quality entry points;
- repository ignore rules and repository-native collaboration guidance;
- the validation-first M0–M9 research roadmap, now with M0A as a foundational insertion before M1;
- architecture, quantitative-convention, provenance, reproducibility/RNG, validation, and future Python/C++ guardrails;
- `docs/development/engineering_principles.md` for engineering/collaboration rationale;
- `docs/quantitative_conventions.md` as the authority for committed and deliberately deferred quantitative conventions;
- ADR guidance plus ADR 0001 for the foundational pricing-composition decision;
- reusable implementation Issue and pull-request templates.

M0A adds the first finance-domain production semantics under `qf_platform.pricing`:

```text
state space / modeled state / state path
        +
stochastic law + separate parameter values
        +
financial contract → immutable cash-flow stream
        +
strictly-positive numeraire
        +
physical vs numeraire-associated pricing-measure semantics
        ↓
immutable PricingProblem
        +
compatible ValuationMethod
        ↓
immutable ValuationResult(present_value)
```

The core deliberately does not define every stochastic model through drift/diffusion, does not implement a generic change-of-measure engine, and does not make every valuation method support every pricing problem.

## Foundational pricing boundary

The current mathematical architecture reflects

```math
\mathfrak P = (\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

and keeps the theoretical pricing question separate from the analytic/numerical method used to evaluate it.

This foundational exception does **not** waive the ordinary two-consumer extraction discipline for calibration, risk, market data, portfolios, research workflows, native backends, or other application abstractions.

## Quality-tool maturity

The canonical gate remains intentionally lean on current `main`:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

Issue #7 separately tracks a cognitive-complexity guard. Coverage thresholds, Import Linter contracts beyond focused architectural tests, strict docs builds, quantitative contract suites, benchmark/profile infrastructure, and release smoke checks should still be added only when concrete code gives them meaningful enforcement targets.

## Deliberately absent

The following are still absent from merged project truth until their milestones land:

- `EuropeanOption` and option-right semantics;
- GBM / Black-Scholes stochastic-law specialization;
- money-market-account specialization and concrete M1 rate/carry conventions;
- Black-Scholes closed-form valuation;
- CRR/binomial or Monte Carlo methods;
- Greeks, hedging, calibration, model-risk, or generic validation frameworks;
- market snapshots/environments and live market-data clients;
- trade/portfolio infrastructure;
- Heston;
- native/C++ backends.

## Next objective

Begin revised **M1 — European Options & Black-Scholes Reference Vertical** from M0A.

Approximate specialization:

```text
Equity state / path
+
GBM / Black-Scholes stochastic law
+
Black-Scholes parameter values
+
European call/put contract
+
money-market numeraire
+
risk-neutral pricing-measure semantics
        ↓
PricingProblem
        +
Black-Scholes closed-form ValuationMethod
        ↓
ValuationResult
        ↓
parity + bounds + limiting cases + benchmark evidence
```

M1 owns the concrete date/year-fraction, discounting, carry/dividend, spot, volatility, option-right, formula, and theoretical-validation decisions. It should specialize M0A rather than bypassing it or expanding M0A into a universal rates/market-data framework.

## M1 design pressure

Expected questions include:

- the smallest concrete equity state/path representation needed by GBM and a European terminal-payoff contract;
- how calendar expiry, valuation date, year fraction, and day count become explicit M1 semantics;
- how a money-market-account numeraire is specialized without spreading scalar interest-rate assumptions through the pricing core;
- how continuous dividend/carry semantics interact with the chosen state/dynamics/numeraire representation;
- the exact GBM/Black-Scholes stochastic-law and parameter domain under Q;
- how `EuropeanOption.cash_flows(...)` remains contract semantics while the closed-form method owns analytic valuation;
- how the closed-form method advertises compatibility with only the M1 problem family it actually supports;
- which no-arbitrage, limiting-case, and benchmark checks become executable validation evidence.

Do not pre-build unrelated rates, calibration, market-data, portfolio, risk, or validation frameworks while answering those questions.
