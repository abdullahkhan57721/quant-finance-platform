# Black-Scholes Reference Model

## Purpose

M1 establishes Black-Scholes as the platform's first analytical reference model for
European equity options. The implementation is intentionally narrow: it provides a
trusted present-value baseline that later binomial, Monte Carlo, Greek, hedging, and
empirical work can challenge independently.

The production implementation is
`qf_platform.valuation.black_scholes.black_scholes_present_value`.

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

## Project notation

For expiry `E` and valuation date `V`:

- `S` — spot price at `V`;
- `K` — strike;
- `T` — M1 Actual/365 Fixed year fraction from `V` to `E`;
- `sigma` — annualized volatility as a decimal standard deviation;
- `D_r(T)` — risk-free discount factor from `V` to `E`;
- `D_q(T)` — continuous proportional dividend/carry discount factor from `V` to
  `E`;
- `N(x)` — standard-normal cumulative distribution function.

For the concrete M1 flat continuously compounded inputs,

```text
D_r(T) = exp(-r T)
D_q(T) = exp(-q T)
```

but the Black-Scholes valuation function consumes discount factors, not rate scalars.
The compounding choice therefore belongs to the concrete discounting implementation
rather than being hidden inside the valuation API.

For positive `S`, `K`, `T`, and `sigma`:

```text
log-forward-moneyness = log(S/K) + log(D_q(T)) - log(D_r(T))

d1 = [log-forward-moneyness + 0.5 sigma^2 T] / [sigma sqrt(T)]
d2 = d1 - sigma sqrt(T)

call PV = S D_q(T) N(d1) - K D_r(T) N(d2)
put  PV = K D_r(T) N(-d2) - S D_q(T) N(-d1)
```

This is the deterministic continuous-carry form of Black-Scholes-Merton expressed
through discount factors.

## M1 assumptions and scope

The reference vertical assumes:

- European exercise at one calendar expiry date;
- spot input rather than a forward input;
- deterministic risk-free discounting to the option expiry;
- deterministic continuous proportional dividend/carry discounting;
- constant annualized volatility over the option horizon;
- Black-Scholes lognormal diffusion assumptions for the positive-state analytical
  formula;
- no discrete cash-dividend schedule;
- no business-day adjustment or time-of-day expiry semantics;
- Actual/365 Fixed model time for this vertical.

These assumptions are model/reference semantics, not claims that observed option
markets satisfy them.

## Explicit boundary and limiting cases

The production function handles several boundaries directly rather than letting the
main formula encounter undefined logarithms or divisions:

- `T = 0`: ordinary option intrinsic value at valuation/expiry;
- `sigma = 0`: discounted deterministic intrinsic value;
- `S = 0`: call value `0`; put value `K D_r(T)`;
- `K = 0`: call value `S D_q(T)`; put value `0`.

An expiry before the valuation date is invalid for this valuation method. Negative
continuously compounded rates are financially meaningful and are not rejected merely
because many textbook examples use positive rates.

## Theoretical validation identities

### Put-call parity

For otherwise identical European call and put contracts,

```text
C - P = S D_q(T) - K D_r(T)
```

The tests exercise this identity across multiple spots, strikes, volatilities, carry
rates, and a negative risk-free-rate case.

### No-arbitrage bounds

For positive finite discount factors:

```text
max(S D_q(T) - K D_r(T), 0) <= C <= S D_q(T)
max(K D_r(T) - S D_q(T), 0) <= P <= K D_r(T)
```

These bounds are checked separately from the pricing formula.

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

This benchmark is not the sole evidence of correctness: a shared convention error can
make one numerical example look right. It is combined with parity, bounds, limiting
cases, and convention-discriminating tests.

## Tolerance rationale

The analytical benchmark/parity tests use an absolute tolerance of `2e-13` for
values on roughly a 100-unit scale. The implementation uses ordinary IEEE-754 double
precision and standard-library `log`, `sqrt`, `exp`, and `erf`; the tolerance allows a
small accumulation of floating-point/libm rounding while remaining far tighter than
any economically meaningful quote precision.

This tolerance is local to these deterministic analytical checks. It is not a project
Monte Carlo, calibration, market-data, or backend-parity tolerance.

## Executable evidence map

- `tests/market/test_time.py` — Actual/365 Fixed semantics, including leap-year
  discrimination.
- `tests/market/test_discounting.py` — continuous compounding and negative rates.
- `tests/market/test_environment.py` — spot/domain and valuation-date ownership.
- `tests/models/test_black_scholes_parameters.py` — volatility units/domain and
  immutability.
- `tests/valuation/test_black_scholes.py` — published benchmark, put-call parity,
  no-arbitrage bounds, limiting cases, carry direction, expired valuation rejection,
  and discount-factor-domain checks.

M2 should add genuinely independent valuation and Greek methods rather than expanding
this analytical implementation until it can validate itself by construction.
