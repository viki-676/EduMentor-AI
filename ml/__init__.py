"""
EduMentor AI Machine Learning Package.
Provides student performance risk classification, evaluation metrics, and model persistence.
"""

from .performance_predictor import (
    StudentRiskPredictor, evaluate_and_train_model,
    DEFAULT_DECISION_THRESHOLD, validate_decision_threshold
)
from .evaluate_model import evaluate_saved_model

__all__ = [
    'StudentRiskPredictor', 'evaluate_and_train_model', 'evaluate_saved_model',
    'DEFAULT_DECISION_THRESHOLD', 'validate_decision_threshold'
]

