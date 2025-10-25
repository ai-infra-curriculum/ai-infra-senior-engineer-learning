"""Custom Resource Definition (CRD) module for TrainingJob.

Defines the TrainingJob CRD, validation, and default values.
"""

from .defaults import apply_defaults, DEFAULT_TRAINING_CONFIG
from .trainingjob_crd import TrainingJobCRD, get_trainingjob_crd
from .validation import validate_training_job, ValidationError

__all__ = [
    "TrainingJobCRD",
    "get_trainingjob_crd",
    "apply_defaults",
    "DEFAULT_TRAINING_CONFIG",
    "validate_training_job",
    "ValidationError",
]
