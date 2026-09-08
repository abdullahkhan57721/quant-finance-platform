# M6 — Heston Calibration and Parameter Recovery

## Status

Implementation in progress on Issue #34.

This document is the M6 recovery/traceability surface and will be completed with the calibrated problem, numerical method, synthetic-recovery evidence, identifiability diagnostics, and market-calibration evidence before merge.

Protect:

```text
Heston stochastic law
!= Heston parameter values
!= current variance state
!= calibrated estimate

calibration problem
!= residual/objective semantics
!= numerical optimizer
!= optimizer configuration/state
!= completed calibration result
```

The first M6 calibration target representation is option-price space. Synthetic targets and normalized market observations remain semantically distinct. Current variance `v0` remains state-like and is estimated alongside the structural Heston parameter values required by the option cross-section; it is not moved into `HestonParameters`.
