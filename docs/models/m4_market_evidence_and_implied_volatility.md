# M4 Market Evidence and Implied-Volatility Inference

## Purpose

M4 introduces the platform's first production boundary from independently observed
market information into a mathematical inverse problem.

The governing scientific flow is:

```text
real option market
        ↓
raw observations + provenance
        ↓
explicit normalization
        ↓
problem-ready option observation
        ↓
Black-Scholes inverse problem
        +
numerical inverse method
        ↓
implied-volatility result + conditioning evidence
        ↓
strike / maturity evidence
        ↓
empirical pressure against constant volatility
```

This milestone deliberately keeps the following objects distinct:

```text
raw observation
!= normalized observation
!= modeled state
!= Black-Scholes model price
!= implied volatility

inverse financial problem
!= numerical root-finding method
!= completed inverse result
```

Implied volatility is a model-dependent inferred parameter. It is not a directly
observed physical volatility and is not a physical-measure forecast.

## Production boundaries

### Market observations

`qf_platform.market_data` owns observed-data semantics required by this milestone.

`ObservationProvenance` records:

- provider/source identity;
- market/as-of date;
- timezone-aware retrieval timestamp;
- optional timezone-aware observation timestamp when the source preserves one;
- optional SHA-256 of the raw local artifact; and
- licensing/redistribution notes.

`RawOptionQuote` records contract identity/semantics and raw quote fields. Raw quote
objects may contain finite negative or crossed bid/ask values because those values are
observations of bad data. Rejecting or transforming them belongs to normalization, not
to raw evidence construction.

`RawUnderlyingObservation` is an observed market level. It is intentionally not an M1
`EquityState`; the latter is a modeled state used inside a pricing problem.

### Normalization

`normalize_european_option_midpoint` is the first concrete normalization policy. It
requires:

- option and underlying observations for the same underlying and market date;
- European exercise semantics;
- non-AM settlement under the current date-only M1 expiry representation;
- both bid and ask present;
- strictly positive bid and ask;
- a non-crossed market `bid <= ask`; and
- a strictly positive observed underlying level.

The normalized target is

```math
C^{market}_{mid} = \frac{bid + ask}{2}.
```

The resulting `NormalizedOptionObservation` retains both raw observations and records
`m4-midpoint-v1` as its normalization version. Normalization does not overwrite the raw
quote.

M4 does not infer staleness when a source lacks a contract-level timestamp. Absence of
that evidence remains explicit rather than being converted into a false freshness
claim.

## The inverse problem

For fixed observed/model inputs other than volatility, the Black-Scholes forward map is

```math
C = F_{BS}(\sigma).
```

The market supplies a normalized observed target

```math
C^{market}.
```

`BlackScholesImpliedVolatilityProblem` asks for an admissible volatility satisfying

```math
F_{BS}(\sigma_{impl}) = C^{market}.
```

The problem owns:

- the provenance-bearing normalized target;
- observed spot;
- European option contract semantics;
- the existing M1 money-market numeraire/pricing-measure context;
- continuous dividend/carry input;
- the admissible volatility interval; and
- financial feasibility checks.

It does not own a root-search algorithm.

The current admissible default domain is

```text
0.00 <= annualized volatility <= 5.00
```

in annualized decimal-volatility units. The upper endpoint is a local M4 numerical
configuration, not a claim that 500% is a universal economic maximum.

## Financial feasibility before solving

For time to expiry `T > 0`, spot `S`, strike `K`, continuously compounded rate `r`, and
continuous dividend yield `q`, define

```math
S_q = S e^{-qT},
K_r = K e^{-rT}.
```

The European call bounds are

```math
max(S_q - K_r, 0) <= C <= S_q,
```

and the put bounds are

```math
max(K_r - S_q, 0) <= P <= K_r.
```

M4 checks these bounds before numerical root search. A target that is materially
outside them raises `InconsistentObservedPrice` rather than returning a plausible
volatility.

A scale-aware `1e-12` relative comparison tolerance is used only to avoid rejecting a
quote that differs from a theoretical bound by floating-point roundoff. This is a
local financial-bound comparison tolerance, not a project-wide tolerance and not a
license to accept economically meaningful bound violations.

M4 also requires positive time to expiry and a strictly positive strike for implied
volatility. The exact zero-volatility price remains an admitted boundary when the
observed target equals the deterministic Black-Scholes limit.

## Numerical inverse method

`BisectionImpliedVolatility` is the first numerical method for this inverse problem.
It is deliberately concrete rather than a universal inverse-method framework.

The method:

1. evaluates the Black-Scholes forward map at the configured volatility endpoints;
2. returns an endpoint solution if the price residual already satisfies the configured
   price tolerance;
3. raises `ImpliedVolatilityNotBracketed` if the financially admissible target is not
   bracketed on the configured volatility domain;
4. bisects the volatility interval using monotonicity of European Black-Scholes value
   in volatility;
5. converges on either the configured price-residual criterion or sufficiently narrow
   volatility bracket; and
6. raises `ImpliedVolatilityConvergenceError` only when the bracketed numerical problem
   remains unresolved after the maximum iteration budget.

Default numerical controls are:

```text
price tolerance       = 1e-10 price units
volatility tolerance  = 1e-10 annualized volatility decimals
maximum iterations    = 200
```

These are method-local numerical criteria. They are different from market quote
precision and from the financial no-arbitrage-bound roundoff tolerance.

The forward evaluation itself always reuses the existing M1
`BlackScholesClosedForm`; implied-volatility code does not maintain a second pricing
formula.

## Conditioning evidence

The local first-order relationship is

```math
dC \approx Vega\,d\sigma,
```

so

```math
d\sigma \approx \frac{dC}{Vega}.
```

M4 evaluates Vega at the inferred solution through the already validated M2
`AnalyticBlackScholesSensitivity`. Vega therefore retains the M2 units:

```text
present-value units per 1.00 annualized volatility decimal.
```

`ImpliedVolatilityResult` records:

- inferred annualized volatility;
- model price at the solution;
- residual;
- iterations/function evaluations;
- Vega where the solution lies in the differentiable interior;
- `1 / Vega`, interpreted locally as approximate volatility-decimal change per one
  price unit; and
- the first-order implied-volatility displacement associated with one half of the raw
  bid/ask spread.

This keeps two failure modes separate:

```text
root search failed
!=
root exists but the inverse map is locally poorly conditioned.
```

Deep-wing and near-expiry observations can have low Vega and therefore large inferred
volatility sensitivity to small price perturbations even when bisection converges
perfectly.

## Strike and maturity coordinates

M4 retains strike directly and exposes log-forward-moneyness

```math
k = \log(K/F),
```

with the local flat rate/carry forward convention

```math
F = S e^{(r-q)T}.
```

The rate and carry used in this coordinate are the same explicit inputs used by the
forward pricing map. They are not silently inferred from the option chain.

## Static quote-quality diagnostics

`diagnose_option_strike_slice` provides only the static diagnostics justified by one
same-date, same-expiry, same-underlying, same-right normalized strike slice.

For calls it checks that price is nonincreasing in strike; for puts it checks that
price is nondecreasing. For either right it checks discrete convexity by requiring
adjacent strike secant slopes to be nondecreasing.

The diagnostic:

```text
reports violations
!= repairs quotes
!= interpolates a surface
!= constructs an arbitrage-free volatility surface.
```

Duplicate strikes or incomparable mixed slices are rejected rather than silently
aggregated.

## Deterministic CI evidence

Core CI never retrieves live market data.

`tests/fixtures/m4_synthetic_option_quotes.json` is a deterministic synthetic option
fixture containing deliberate strike and maturity volatility structure. Tests invert
its prices and verify that the intended nonconstant volatility structure is recovered.
This proves the observation -> normalization -> inverse pipeline without representing
synthetic observations as empirical evidence.

Other focused tests cover:

- provenance and timezone validation;
- preservation of raw crossed/nonpositive observations before normalization;
- midpoint, missing-quote, nonpositive-quote and crossed-quote policies;
- European/non-AM support boundaries;
- known-volatility recovery;
- no-arbitrage feasibility failure before solving;
- financially feasible but unbracketed inverse problems;
- deterministic maximum-iteration failure;
- the zero-volatility boundary;
- one-day near-expiry recovery;
- deep-OTM low-Vega conditioning; and
- strike-slice monotonicity/convexity diagnostics.

## Reproducible real-market evidence

The committed derived evidence is
`docs/evidence/m4_spx_implied_volatility_evidence.json`.

The raw research input is pinned as:

```text
repository: IceCurrent/local_volatility_model
commit:     428531599bf3945f5d51691fdd21b1667eb14958
path:       data/data.csv
Git blob:   8d1db0f2710c4707555c8263f9b7f8f527974836
```

The source repository describes the file as an SPX option-chain snapshot containing
bid/ask/IV/Greek columns per quote date, expiry and strike. The raw rows are not
committed into this repository. At the time M4 was produced, the pinned source
repository did not contain a repository license file, so the M4 artifact deliberately
records only derived/model outputs and provenance sufficient to reacquire the source.

The CSV does not encode option exercise style or settlement time. For the selected
non-third-Friday SPX expiries, the research recipe therefore separately records Cboe
SPXW contract semantics: European exercise and PM settlement. This is semantic
enrichment, not a claim that those fields were present in the raw CSV.

The evidence uses the January 4, 2023 SPX observation with spot `3853.39` and two
expiries:

```text
2023-02-03   approximately 30 days
2023-04-28   approximately 114 days
```

The local model inputs are explicitly assumed rather than observed:

```text
continuously compounded flat rate r = 0.045
continuous dividend yield        q = 0.017
ACT/365F time basis
positive non-crossed bid/ask midpoint
OTM put below model forward; OTM call at/above model forward
```

These assumptions matter to absolute implied-volatility levels. The evidence should
not be read as a provider-published volatility surface.

### Observed strike structure

Selected points from the 30-day slice infer approximately:

```text
K=3720 put   23.03%
K=3850 put   21.45%
K=3900 call  20.65%
K=4020 call  19.08%
```

Selected points from the approximately 114-day slice infer approximately:

```text
K=3720 put   23.12%
K=3900 call  21.49%
K=4075 call  19.63%
K=4240 call  18.22%
```

A single constant Black-Scholes volatility therefore cannot reconcile the observed
prices across strike under this explicit input convention. Both slices exhibit the
familiar equity-index downside skew: lower strikes imply materially higher volatility
than higher strikes.

### Maturity structure

The two expiries do not produce one identical strike/moneyness-volatility relation.
This supplies maturity dependence in addition to strike dependence. Because the first
M4 evidence uses simplified flat rate/carry inputs and only two expiries, it motivates
richer volatility dynamics without claiming a fully constructed market surface.

### Quote quality and conditioning

The selected inference points retain M2 Vega and half-spread first-order IV sensitivity.
For example, the 30-day evidence has Vega values around 343--440 in the selected
region, while the 114-day values are around 619--854. Wider bid/ask rows correspond to
larger local IV uncertainty even when the numerical root solve is stable.

The inspected same-right raw midpoint slices are monotone in strike but contain
multiple discrete convexity violations. That is evidence of quote noise/asynchrony or
other data imperfections, not a request for M4 to repair the surface.

## Scientific conclusion

M4 establishes the empirical argument:

```text
Black-Scholes constant sigma
        ↓
observed option prices
        ↓
Black-Scholes inversion
        ↓
sigma_impl(K,T)
        ↓
systematic strike skew + maturity dependence
        ↓
one constant sigma cannot fit the observed option set
```

This does **not** prove that any particular richer model is correct. It creates a
specific model limitation for M5 to address: volatility structure must be able to vary
beyond one constant scalar while preserving independently testable valuation methods.

## M4 limitations carried forward

M4 intentionally does not solve:

- live provider integration or a generic market-data-provider framework;
- intraday quote synchronization or a universal staleness model;
- business-day/calendar infrastructure beyond the existing date-based specialization;
- discount/dividend curve inference from the option chain;
- full put-call-parity forward extraction;
- arbitrage-free interpolation/repair or a generic volatility-surface object;
- physical-measure volatility forecasting;
- Heston or any other stochastic-volatility law;
- Heston calibration; or
- a generic inverse-problem/optimization framework.

Those omissions are part of the evidence boundary, not hidden implementation gaps.
