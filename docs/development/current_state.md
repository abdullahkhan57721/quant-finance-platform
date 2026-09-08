# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

M0A now consists of:

1. the implemented mathematical pricing-composition core introduced by PR #10; and
2. the broader platform-wide mathematical problem taxonomy recorded by ADR 0002.

ADR 0002 is the current architectural authority. ADR 0001 remains the historical record for the pricing-specific foundation that was implemented first.

The next finance milestone is **M1 — European Options & Black-Scholes Reference Vertical**, implemented as the first concrete specialization of the M0A pricing core.

## What exists

The repository establishes:

- a `src/`-layout Python package;
- package metadata in `pyproject.toml`;
- pytest, Ruff, and strict Pyright configuration;
- GitHub Actions CI invoking the canonical local quality gate;
- `scripts/fix` and `scripts/check_all` as local quality entry points;
- an evidence-based validation cadence in `docs/development/validation_cadence.md`;
- repository ignore rules and repository-native collaboration guidance;
- the validation-first M0–M9 research roadmap;
- architecture, quantitative-convention, provenance, reproducibility/RNG, validation, and future Python/C++ guardrails;
- `docs/development/engineering_principles.md` for engineering/collaboration rationale;
- `docs/quantitative_conventions.md` as the authority for committed and deliberately deferred quantitative conventions;
- ADR 0001 for the historical pricing-specific foundation and ADR 0002 for the current mathematical problem architecture;
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

## Platform-wide mathematical architecture

M0A also establishes this durable taxonomy:

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS

state / state space
stochastic law
model parameters
probability semantics
physical measure P
pricing measure Q^N
numeraire N
market observations + provenance
financial contracts
cash flows
quantitative conventions

        ↓

PROBLEM FAMILIES

forward / pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation

        ↓

SOLUTION METHODS

analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenario methods / tests

        ↓

SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The platform-wide conceptual pattern is:

```text
Problem + supported Method -> specific immutable Result
```

This is architectural rather than a universal runtime hierarchy. The repository intentionally does **not** contain generic production `InverseProblem`, `SensitivityProblem`, `PredictionProblem`, `ControlProblem`, `RiskProblem`, or `ValidationProblem` frameworks yet. Their first implementations should remain concrete until real consumers establish shared software behavior.

The governing doctrine is:

```text
Foundational mathematical domain distinctions
may be represented explicitly from the outset.

Problem-specific software frameworks
should remain narrow and evidence-driven.

Mathematical generality
does not imply
universal operational APIs.
```

## Observation/model boundary

Observed and modeled quantities remain conceptually separate:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information
```

separately from:

```text
modeled state
+
stochastic law
+
parameter values
+
probability semantics
```

A specific problem may combine problem-ready observed information with model semantics, but raw observations must not be silently overwritten by model-generated or model-implied quantities.

## Foundational pricing boundary

The current pricing architecture reflects:

```math
\mathfrak P_{\mathrm{price}}
=
(\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

and keeps the theoretical pricing question separate from the analytic/numerical method used to evaluate it.

The broader M0A doctrine does **not** waive evidence-driven extraction for operational calibration/inference, sensitivity, prediction, control, risk, validation, market-data, portfolio, research, or native-backend frameworks.

## Quality-tool maturity

The canonical gate remains intentionally lean on current `main`:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

Issue #7 separately tracks a cognitive-complexity guard. Coverage thresholds, Import Linter contracts beyond focused architectural tests, strict docs builds, quantitative contract suites, benchmark/profile infrastructure, and release smoke checks should still be added only when concrete code gives them meaningful enforcement targets.

The current complete gate is also still cheap enough that the repository deliberately does **not** have a second fast/checkpoint command or a draft-fast/final-full CI split. The current development cadence is:

```text
coherent implementation batch
        ↓
./scripts/fix
        ↓
focused behavioral / quantitative validation
        ↓
./scripts/check_all at a meaningful checkpoint
        ↓
full CI for pushed candidates
        ↓
ticket-specific final quantitative/manual evidence
        ↓
exact-head review → squash merge → verify main
```

`scripts/fix` should be used proactively before broader validation and before CI-triggering pushes after coherent Python changes. CI is confirmation of a checkpoint, not the normal formatting/debug loop. See `docs/development/validation_cadence.md` for the measured rationale, quality-gate classification, and future revisit triggers.

## Deliberately absent

The following are still absent from merged project truth until their milestones land:

- `EuropeanOption` and option-right semantics;
- GBM / Black-Scholes stochastic-law specialization;
- money-market-account specialization and concrete M1 rate/carry conventions;
- Black-Scholes closed-form valuation;
- CRR/binomial or Monte Carlo methods;
- Greeks/sensitivity production structures;
- hedging/control production structures;
- inference/calibration production structures;
- prediction frameworks;
- generic risk or validation frameworks;
- market snapshots/environments and live market-data clients;
- trade/portfolio infrastructure;
- Heston;
- native/C++ backends.

## Next objective

Begin revised **M1 — European Options & Black-Scholes Reference Vertical** from current `main`.

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

M1 does **not** need to implement the other problem-family frameworks merely because M0A now names them architecturally.

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

Do not pre-build unrelated rates, inference/calibration, prediction, control, market-data, portfolio, risk, or validation frameworks while answering those questions.
