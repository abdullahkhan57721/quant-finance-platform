# Changelog

## v0.1.0 — Portfolio-Quality Release

This release consolidates the completed M1–M8 quantitative roadmap and UI1–UI5 native Workbench into one reproducible equity-derivatives/model-validation portfolio.

### Quantitative scope

- European-option Black-Scholes pricing with closed-form, CRR, and seeded Monte Carlo methods;
- analytic and finite-difference Delta, Gamma, Vega, Theta, and Rho;
- discrete dynamic Delta hedging with rebalance, volatility-misspecification, and transaction-cost evidence;
- provenance-bearing option observations, midpoint normalization, and Black-Scholes implied-volatility inference;
- Heston stochastic-volatility pricing with independent Fourier and Monte Carlo methods;
- Heston price-space calibration, multiple-start recovery/stability, and local identifiability diagnostics;
- predeclared same-date Black-Scholes-vs-Heston held-out validation/model-risk evidence; and
- profiling-driven Python/NumPy performance engineering.

### Reference empirical result

On the pinned January 4, 2023 SPX/SPXW sample with a predeclared 10-training / 4-held-out split, Heston reduced held-out price RMSE from approximately `8.412` to `0.671` and relative MAE from approximately `8.27%` to `0.66%` versus the fairly fitted one-volatility Black-Scholes benchmark.

This is a same-date cross-sectional result. It does **not** establish temporal forecasting skill, global Heston parameter identification, trading profitability, universal model superiority, or Heston hedge superiority.

### Performance result

The revision-pinned M8 comparison reports approximately `4.61x–27.38x` improvement across the representative heavy workloads after removing scalar Python/RNG overhead and repeated Heston Fourier work.

A C++ kernel is deliberately **not** part of v0.1: after the measured Python/algorithmic improvements, the remaining representative absolute cost did not justify a compiler/binding/cross-platform packaging and parity surface.

### Native Workbench

The PySide6 + Qt Quick/QML Workbench presents the merged pricing, sensitivity, hedging, implied-volatility, Heston, calibration, validation/model-risk, and performance-evidence workflows downstream of the quantitative core.

### Distribution boundary

The v0.1 release contract is:

- Python 3.12 source installation;
- optional PySide6 6.11.2 desktop dependency;
- source Workbench launch from the installed package; and
- an Ubuntu 24.04 x86_64 standalone `pyside6-deploy` artifact as the CI-verified packaged proof.

v0.1 does **not** claim macOS/Windows installer certification, code signing/notarization, an update channel, or a universally supported binary installer.
