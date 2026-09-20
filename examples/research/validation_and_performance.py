"""Recompute derived-reference validation; inspect separately recorded M8 timings."""

from qf_platform.application import (
    UI5PerformanceReference,
    UI5ValidationAnalysis,
    canonical_m8_performance_reference,
    make_ui5_reference_validation_request,
    run_ui5_validation,
)


def run_example() -> tuple[UI5ValidationAnalysis, UI5PerformanceReference]:
    # Package-safe derived inputs; this is not a replay from raw vendor rows.
    request = make_ui5_reference_validation_request()
    analysis = run_ui5_validation(request)
    return analysis, canonical_m8_performance_reference()


if __name__ == "__main__":
    analysis, performance = run_example()
    evidence = analysis.evidence
    print(
        "Derived SPX reference, same-date cross-sectional holdout (10 train / 4 held out)"
    )
    print("BS training:", evidence.black_scholes_training_metrics)
    print("Heston training:", evidence.heston_training_metrics)
    print("BS held out:", evidence.black_scholes_evaluation_metrics)
    print("Heston held out:", evidence.heston_evaluation_metrics)
    print("Bounded conclusion:", evidence.conclusion)
    print("Historical timings, not measured by this script:", performance.evidence_kind)
    print("Baseline revision:", performance.baseline_revision)
    print("Optimized revision:", performance.optimized_reference_revision)
    for workload in performance.workloads:
        print(workload.label, workload.optimized_median_seconds, workload.detail)
    print("Native decision:", performance.native_decision)
