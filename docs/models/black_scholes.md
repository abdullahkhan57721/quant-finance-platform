# Black-Scholes Reference Specialization

## Purpose

M1 establishes European equity options under Black-Scholes as the first concrete
specialization of the M0A asset-pricing composition. The production path is:

```text
EquityState / EquityStateSpace
+
BlackScholesLaw + BlackScholesParameters
+
EuropeanOption -> CashFlowStream
+
FlatMoneyMarketNumeraire + PricingMeasureSemantics
        ↓
PricingProblem
        +
BlackScholesClosedForm
        ↓
ValuationResult(present_value)
```

The stochastic law, parameter values, contract, numeraire, pricing-measure semantics,
valuation method, and completed result remain separate responsibilities. In particular,
Black-Scholes closed form is a valuation method for a supported pricing problem; it is
not the stochastic law itself.

## Primary references

- Fischer Black and Myron Scholes, *The Pricing of Options and Corporate
  Liabilities*, Journal of Political Economy 81(3), 1973, pp. 637-654,
  https://doi.org/10.1086/260062.
- Robert C. Merton, *Theory of Rational Option Pricing*, The Bell Journal of
  Economics and Management Science 4(1), 1973, pp. 141-183,
  https://doi.org/10.2307/3003143.

For an independently published numerical check used by the test suite:

- Aleš Kresta, *Applied Quantitative Finance in Python: Selected Theories and
  Examples* (2024), Chapter 5. Its worked example with `S=K=100`, `T=1`,
  continuously compounded `r=0.05`, `q=0`, and `sigma=0.20` reports call and put
  values `10.450583572185565` and `5.573526022256971`.

## Project notation and ownership

For valuation date `V` and expiry `E`:

- `S` — `PricingProblem.current_state.value.spot`;
- `K` — `EuropeanOption.strike`;
- `T` — `actual_365_fixed_year_fraction(V, E)`;
- `sigma` — `BlackScholesParameters.annualized_volatility`;
- `q` — `BlackScholesParameters.continuous_dividend_yield`;
- `N_t` — `PricingProblem.numeraire.value_at(t)`;
- `D_r(V,E) = N_V / N_E` — risk-free discount factor implied by the numeraire;
- `D_q(V,E) = exp(-q T)` — continuous proportional dividend/carry discount factor;
- `Phi` — standard-normal cumulative distribution function.

The concrete M1 money-market account is

```text
N_t = exp(r * ACT365F(reference_date, t)),
```

where `r` is a finite continuously compounded annualized decimal rate. The closed-form
method does not duplicate `r` in `BlackScholesParameters`: it obtains discounting from
the `Numeraire` already owned by the `PricingProblem`.

## Pricing-measure assumptions

Under the money-market pricing measure `Q^B`, M1 uses the standard constant-parameter
GBM / Black-Scholes semantics

```text
dS_t / S_t = (r - q) dt + sigma dW_t^(Q^B)
```

for positive spot. The M0A `StochasticLaw` protocol intentionally remains free of a
universal `drift()` / `diffusion()` API; `BlackScholesLaw` records the concrete law
identity, state-space semantics, and compatible parameter type while the assumptions
and formula are traceable here.

For one terminal European payoff `G(S_E)`, M0A's pricing equation specializes to

```text
V_V = N_V E_V^(Q^B)[G(S_E) / N_E].
```

## Closed-form formula

For positive `S`, `K`, `T`, and `sigma`:

```text
log-forward-moneyness = log(S) - log(K) + log(D_q) - log(D_r)

d1 = [log-forward-moneyness + 0.5 sigma^2 T] / [sigma sqrt(T)]
d2 = d1 - sigma sqrt(T)

call PV = S D_q Phi(d1) - K D_r Phi(d2)
put  PV = K D_r Phi(-d2) - S D_q Phi(-d1)
```

Using differences of logarithms instead of `log(S/K)` avoids avoidable ratio
underflow/overflow at extreme but finite moneyness.

## Contract semantics

`EuropeanOption` owns only terminal contingent cash flows:

```text
call: max(S_E - K, 0)
put:  max(K - S_E, 0)
```

Its `cash_flows(path)` implementation is tested independently of valuation. It has no
`.price()`, model, market-data, trade/portfolio, calibration, hedging, or presentation
responsibility.

## M1 quantitative conventions

M1 commits only the conventions needed by this vertical:

- valuation and expiry are `datetime.date` calendar dates, not datetimes;
- model time uses Actual/365 Fixed: actual calendar days divided by exactly 365;
- no business-day adjustment or time-of-day semantics;
- spot is a non-negative finite modeled equity state; zero is an admitted degenerate
  boundary;
- strike is non-negative and finite; zero is an admitted boundary;
- volatility is a non-negative finite annualized decimal standard deviation (`0.20`
  means 20%);
- the risk-free rate in `FlatMoneyMarketNumeraire` is a finite continuously compounded
  annualized decimal rate; negative rates are allowed;
- continuous proportional dividend/carry `q` is a finite continuously compounded
  annualized decimal rate stored with the Black-Scholes parameter values;
- completed pricing output remains `ValuationResult.present_value`.

These choices do not establish a general rates framework, yield-curve hierarchy,
discrete-dividend model, market-observation container, or forward-input API.

## Boundary and limiting cases

The method handles meaningful boundaries explicitly rather than allowing the positive
formula to encounter undefined logarithms or divisions:

- `T = 0`: intrinsic value at valuation/expiry;
- `sigma = 0`: discounted deterministic intrinsic value;
- `S = 0`: call value `0`; put value `K D_r`;
- `K = 0`: call value `S D_q`; put value `0`;
- negative continuously compounded risk-free rates: supported;
- expiry before valuation: structurally constructible contract, but unsupported by the
  M1 closed-form method and rejected through the existing method-support boundary;
- non-finite/domain-invalid inputs: rejected by the value objects or numeraire/result
  validation boundaries.

## Theoretical validation identities

### Put-call parity

For otherwise identical European call and put contracts:

```text
C - P = S D_q - K D_r.
```

Tests exercise this identity across multiple spots, strikes, volatilities, carry rates,
and a negative risk-free-rate case.

### No-arbitrage bounds

For positive finite discount factors:

```text
max(S D_q - K D_r, 0) <= C <= S D_q
max(K D_r - S D_q, 0) <= P <= K D_r
```

The tests compute these bounds independently of the closed-form implementation.

## Numerical reference case

The canonical M1 benchmark is:

```text
S = 100
K = 100
V = 2026-01-01
E = 2027-01-01
T = 1 under Actual/365 Fixed
r = 0.05 continuously compounded
q = 0.00 continuously compounded
sigma = 0.20 annualized decimal volatility
```

Expected values:

```text
call PV = 10.450583572185565
put  PV =  5.573526022256971
```

This numerical check is combined with parity, bounds, limits, contract-level tests, and
convention-discriminating tests so agreement with one example is not treated as
sufficient validation.

## Tolerance rationale

Analytical benchmark/parity checks use an absolute tolerance of `2e-13` for values on
roughly a 100-unit scale. The implementation uses IEEE-754 binary64 Python floats and
standard-library elementary functions. The tolerance allows a small accumulation of
libm rounding while remaining far tighter than economic quote precision.

This is local to deterministic analytical evidence. It is not a future Monte Carlo,
calibration, market-data, or backend-parity tolerance.

## Executable evidence map

- `tests/pricing/test_black_scholes_m1.py` — state/contract domains, terminal cash
  flows, ACT/365F leap-day discrimination, continuous-compounding semantics, negative
  rates, published benchmark values, put-call parity, no-arbitrage bounds, expiry and
  deterministic/degenerate limits, carry direction, and unsupported-problem behavior.
- `tests/pricing/test_dependency_direction.py` — foundational/concrete state, contract,
  law, parameter, date, and numeraire modules remain upstream of pricing-problem and
  valuation implementations.
- existing M0A pricing tests — immutable `PricingProblem` / `ValuationResult`, explicit
  pricing-measure/numeraire association, positive numeraire access, and method
  compatibility semantics.

M2 should add genuinely independent CRR/Monte Carlo and sensitivity evidence rather
than expanding this analytical implementation until it can validate itself by
construction.
