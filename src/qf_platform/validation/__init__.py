"""Concrete validation/model-risk specializations supported by the platform."""

from qf_platform.validation.model_comparison import (
    BlackScholesBenchmarkConvergenceError,
    BlackScholesBenchmarkFit,
    BlackScholesHestonValidationConclusion,
    BlackScholesHestonValidationEvidence,
    BlackScholesHestonValidationProblem,
    CrossSectionalBlackScholesHestonValidation,
    HestonParameterStabilityEvidence,
    HestonStartEvidence,
    InvalidBlackScholesHestonValidationProblem,
    ModelResidualEvidence,
    ValidationComputationEvidence,
    ValidationMetrics,
    ValidationModel,
    ValidationPartition,
    predeclared_every_third_evaluation_partition,
    validate_black_scholes_vs_heston,
)

__all__ = [
    "BlackScholesBenchmarkConvergenceError",
    "BlackScholesBenchmarkFit",
    "BlackScholesHestonValidationConclusion",
    "BlackScholesHestonValidationEvidence",
    "BlackScholesHestonValidationProblem",
    "CrossSectionalBlackScholesHestonValidation",
    "HestonParameterStabilityEvidence",
    "HestonStartEvidence",
    "InvalidBlackScholesHestonValidationProblem",
    "ModelResidualEvidence",
    "ValidationComputationEvidence",
    "ValidationMetrics",
    "ValidationModel",
    "ValidationPartition",
    "predeclared_every_third_evaluation_partition",
    "validate_black_scholes_vs_heston",
]
