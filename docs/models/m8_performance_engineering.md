# M8 — Performance Engineering & Measured Native-Acceleration Decision

## Purpose

M8 asks a deliberately empirical question:

> Where is the platform actually computationally expensive, and is any remaining measured hotspot important enough to justify a Python/C++ boundary?

The answer for the v0.1 workloads is **no C++ yet**.

M8 did find material performance problems, but the dominant costs were removable in the existing Python numerical implementation. After profiling, two narrow Python/NumPy changes reduced every representative heavy workload by at least about 4.6× on the same runner, with the complete M7 study improving by about 5.0× and the 20,000-path Heston Monte Carlo workload by about 27.4×. The remaining absolute latency does not justify the build, binding, packaging, auditability, and parity surface of a native kernel for v0.1.

This is a measured negative native decision, not an unfinished C++ milestone.

## Frozen representative workloads

M7 predeclared the workloads before M8 optimization began:

| Workload | Financial/numerical configuration |
| --- | --- |
| Black-Scholes scalar reference | one `BlackScholesClosedForm` European-option value |
| Heston Fourier scalar reference | one `HestonFourierEuropeanOption`, upper frequency `100`, `256` Simpson intervals |
| Heston Monte Carlo | one `HestonMonteCarloEuropeanOption`, `20,000` paths, `252` timesteps, seed `20260910` |
| Heston training calibration | M7 10-target training set, 3 predeclared starts |
| Heston full-sample stability calibration | all 14 M7 targets, 3 predeclared starts |
| Complete M7 validation study | 10 training / 4 held-out observations, fair Black-Scholes fit plus Heston calibration/stability evidence |

The M7 deterministic fixture is used for benchmark replay. The raw-market acquisition path is intentionally not part of the timing loop.

## Methodology

The durable harness is `scripts/m8_profile_workloads.py`. It records:

- code revision;
- runner/platform/Python/NumPy/SciPy information;
- one warmup sample;
- three measured repetitions;
- `time.perf_counter` wall-clock samples;
- median, min, max, and population standard deviation;
- one `cProfile` execution for each nontrivial workload; and
- structural counts such as paths, timesteps, Gaussian draws, Fourier characteristic-function evaluations, targets, starts, and optimizer evaluations.

`.github/workflows/m8-performance.yml` checks out the frozen M7 baseline and the M8 head on the **same hosted runner**, installs each in its own environment, runs the same harness, and writes a comparison artifact with deterministic/statistical parity checks.

Hosted wall-clock values remain descriptive evidence rather than CI performance thresholds.

## Baseline profile: actual hotspots

### Heston Monte Carlo

The baseline 20,000 × 252 workload contains:

```text
20,000 paths
× 252 timesteps
= 5,040,000 path-step transitions

2 independent normal draws per transition
= 10,080,000 scalar Gaussian draws
```

`cProfile` showed the scalar Python path loop and `random.Random.gauss` dominating the workload. In the same-run baseline profile, the Monte Carlo call took about 10.1 s under profiling, with 10.08 million `gauss` calls alone accounting for about 5.9 s cumulative time.

The root cause was therefore Python scalar-loop/RNG overhead, not a financial-model abstraction problem.

### Heston calibration and M7 validation

Calibration repeatedly priced several strikes sharing the same valuation date, maturity, Heston state/parameters, numeraire, and Fourier grid. The scalar M5 reference recomputed maturity-dependent characteristic-function values separately for every strike.

The baseline full-sample calibration profile executed thousands of scalar Heston Fourier valuations during finite-difference optimizer/Jacobian work. The end-to-end M7 study repeated the same pattern across training and full-sample Heston fits.

The root cause was avoidable repeated numerical work across strikes, not the calibration problem semantics themselves.

## Python/algorithmic optimizations

### 1. Vectorized Heston Monte Carlo path propagation

`HestonMonteCarloEuropeanOption` still owns the same financial method and full-truncation Euler timestep semantics, but path state is propagated across NumPy arrays rather than one Python path at a time.

A fresh local:

```text
numpy.random.Generator(PCG64(seed))
```

owns stochastic generation for each valuation. No ambient global RNG state is consulted.

This changes the concrete random stream relative to the old scalar `random.Random` implementation. Equal integer seeds therefore do **not** mean identical pre-M8 and post-M8 streams. Reproducibility is defined within the current method/revision, while old/new correctness is assessed statistically.

### 2. Stateless maturity-batched Heston Fourier evaluation

`batch_heston_fourier_present_values` groups compatible pricing problems by expiry and computes strike-independent characteristic-function values once per maturity. Strike phases and Simpson aggregation are then evaluated in arrays.

The scalar `HestonFourierEuropeanOption` remains the readable reference implementation. Both scalar and batched paths share the same narrow `heston_characteristic_function` numerical function; M8 did not duplicate the Heston formula or create a generic backend abstraction.

The batching helper is stateless. There is no cache and therefore no financial-input invalidation problem.

### 3. Calibration uses the batch only inside repeated optimizer residual evaluation

The M6 financial calibration problem, coordinates, target weighting, bounds, optimizer contract, and immutable result types remain unchanged. Repeated optimizer residual-vector evaluation uses the M8 batch path, but final calibration result/residual evidence is reconstructed through the authoritative scalar M6 path.

The exact `xi=0` deterministic-variance Heston boundary falls back to the scalar M5/M6 reference rather than forcing an unsupported fast path. Performance work therefore does not narrow the valid financial problem domain.

## Same-run before/after evidence

Reference comparison: frozen M7 baseline `4d80014786810389c324434d7cccab95cf647803` versus M8 optimized revision `15d3b6c83a16ed660f00e7a6bf085cb57b76c411`, on one GitHub Actions runner with Python 3.12.14, NumPy 2.5.3, and SciPy 1.18.1.

| Workload | Baseline median | Optimized median | Speedup |
| --- | ---: | ---: | ---: |
| Black-Scholes scalar reference | 0.000002083 s | 0.000002272 s | 0.92× |
| Heston Fourier scalar reference | 0.000749 s | 0.000818 s | 0.92× |
| Heston Monte Carlo, 20k × 252 | 3.367340 s | 0.122980 s | **27.38×** |
| 10-target / 3-start calibration | 2.291878 s | 0.497131 s | **4.61×** |
| 14-target / 3-start calibration | 3.275181 s | 0.545352 s | **6.01×** |
| Complete M7 validation study | 5.413631 s | 1.081868 s | **5.00×** |

The two scalar reference workloads were intentionally not optimized; their microsecond/sub-millisecond differences are runner/process noise and are not performance claims.

All four heavy representative workloads became faster. The minimum heavy-workload speedup in the same-run comparison was about **4.61×**.

## Correctness and parity evidence

Deterministic comparison checks all passed for:

- Black-Scholes scalar value;
- scalar Heston Fourier value;
- training-calibration objectives;
- full-sample calibration objectives;
- M7 Black-Scholes evaluation RMSE; and
- M7 Heston evaluation RMSE.

The batched Fourier and batched calibration residual paths also have focused scalar-reference regression tests.

For Heston Monte Carlo, old and new implementations use independent RNG algorithms, so the relevant evidence is statistical rather than streamwise equality:

```text
baseline PV = 88.4228456093
baseline SE = 1.0690186763

optimized PV = 87.1337370597
optimized SE = 1.0686958736

absolute difference = 0.8528 combined standard errors
```

The workload uses the same path count, timestep count, and integer seed configuration, while explicitly not claiming equal random streams.

## Native decision

M8 does **not** introduce C++.

After Python/algorithmic optimization:

- the representative 20,000 × 252 Heston Monte Carlo is about `0.12 s` on the reference same-run environment;
- three-start 10- and 14-target Heston calibration workloads are roughly `0.50–0.55 s`;
- the complete M7 study is roughly `1.08 s`;
- Python remains the financial-semantic and correctness/reference implementation; and
- no backend registry, generic compiled plan, native service layer, or Qt-coupled numerical layer is needed.

A C++ kernel could likely accelerate some remaining numerical work, but that is not sufficient justification. The remaining absolute cost must be weighed against a new compiler/binding/toolchain surface, cross-platform packaging, strict parity obligations, and reduced audit simplicity. For the current v0.1 workloads, that trade is not earned.

Future larger workloads may reopen the question. They must profile again rather than treating this decision as a permanent claim that native acceleration is never useful.

## Reproduction

The primary entry points are:

```text
python scripts/m8_profile_workloads.py ...
python scripts/m8_compare_performance.py ...
```

The `M8 Performance Evidence` workflow performs the same-run baseline/optimized comparison and uploads:

```text
m8-baseline-performance.json
m8-optimized-performance.json
m8-performance-comparison.json
```

`docs/evidence/m8_performance_reference.json` retains the compact M9-facing reference evidence.

## M9 handoff

M9 should present the performance story as:

```text
representative M7 workloads
        ↓
profiled Python bottlenecks
        ↓
remove scalar RNG/path overhead
+
share maturity-invariant Fourier work
        ↓
4.61×–27.38× speedups on heavy workloads
        ↓
parity retained
        ↓
C++ not justified for v0.1
```

The release therefore has **measured performance engineering without an unnecessary native dependency**. If M9 or a later specialization materially scales path counts, surfaces, portfolios, repeated calibrations, or scenario workloads, that new workload must be profiled before reconsidering a narrow compiled kernel.
