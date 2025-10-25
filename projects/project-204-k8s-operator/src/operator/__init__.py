"""Operator module - Main entry point for the Kubernetes operator.

This module contains the operator main logic, reconciler, and controller facade.
"""

from .main import main, run_operator
from .reconciler import Reconciler
from .trainingjob_controller import TrainingJobController

__all__ = [
    "main",
    "run_operator",
    "Reconciler",
    "TrainingJobController",
]
