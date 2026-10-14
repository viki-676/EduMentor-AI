"""
Student Risk & Performance Predictor for EduMentor AI.
Implements a complete Scikit-Learn pipeline with baseline comparison,
clean train/test split to prevent data leakage, and rigorous metrics reporting.
"""

import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from .dataset import generate_synthetic_student_data

MODEL_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, 'risk_model.joblib')

FEATURE_NAMES = [
    'avg_score_past',
    'quizzes_attempted',
    'time_per_question',
    'difficulty_level',
    'consistency_score'
]

DEFAULT_DECISION_THRESHOLD = 0.50


def validate_decision_threshold(threshold):
    """
    Validates that a decision threshold is a number between 0.0 and 1.0.
    Raises:
        ValueError: If threshold is non-numeric, boolean, None, or not in [0.0, 1.0].
    """
    if threshold is None or isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError(f"Decision threshold must be a number between 0.0 and 1.0, got {threshold!r}")
    val = float(threshold)
    if not (0.0 <= val <= 1.0):
        raise ValueError(f"Decision threshold must be between 0.0 and 1.0, got {val}")
    return val


class StudentRiskPredictor:
    """
    Predicts whether a student is 'At Risk' (needs intervention/revision)
    or 'Proficient' (on track) based on practice behavior.
    """

    def __init__(self, decision_threshold=None):
        if decision_threshold is None:
            env_thresh = os.getenv('RISK_DECISION_THRESHOLD')
            if env_thresh is not None:
                try:
                    decision_threshold = float(env_thresh)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid RISK_DECISION_THRESHOLD environment value: {env_thresh!r}")
            else:
                decision_threshold = DEFAULT_DECISION_THRESHOLD

        self.decision_threshold = validate_decision_threshold(decision_threshold)
        self.model = None
        self.metrics = {}
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(MODEL_FILE):
            try:
                saved_payload = joblib.load(MODEL_FILE)
                self.model = saved_payload['pipeline']
                self.metrics = saved_payload['metrics']
                return
            except Exception:
                pass
        # Train and save if not found
        self.train_and_evaluate()

    def train_and_evaluate(self):
        df = generate_synthetic_student_data(n_samples=600, random_seed=42)
        X = df[FEATURE_NAMES]
        y = df['needs_intervention']

        # Clean train/test split to avoid data leakage
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        # 1. Baseline Model (Most Frequent Class)
        baseline = DummyClassifier(strategy='most_frequent')
        baseline.fit(X_train, y_train)
        y_base_pred = baseline.predict(X_test)
        base_accuracy = float(accuracy_score(y_test, y_base_pred))

        # 2. Main ML Pipeline (StandardScaler + LogisticRegression)
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(random_state=42, C=1.0, max_iter=200))
        ])
        pipeline.fit(X_train, y_train)

        # 3. Model Evaluation on Unseen Test Split
        y_pred = pipeline.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        self.model = pipeline
        self.metrics = {
            'baseline_accuracy': round(base_accuracy, 4),
            'model_accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
            'confusion_matrix': cm,
            'test_samples': len(y_test),
            'data_type': 'Synthetic demonstration dataset (clearly labeled for academic evaluation)'
        }

        # Persist model and metrics
        try:
            joblib.dump({'pipeline': self.model, 'metrics': self.metrics}, MODEL_FILE)
        except Exception as e:
            print(f"Warning: could not cache model file: {e}")

        return self.metrics

    def predict(self, avg_score, quizzes_count, time_per_q=45.0, difficulty=2, consistency=5, threshold=None):
        """
        Predict risk category and probability for a given student profile.

        Args:
            avg_score: Historical quiz average (0-100).
            quizzes_count: Number of quizzes taken.
            time_per_q: Average time per question in seconds.
            difficulty: Average difficulty level (1=Easy, 2=Medium, 3=Hard).
            consistency: Study cadence score (1-10).
            threshold: Optional decision threshold override in [0.0, 1.0].
                       Defaults to instance self.decision_threshold (default 0.50).

        Returns:
            dict: {
                'status': 'At Risk' | 'On Track',
                'badge': 'warning' | 'success',
                'risk_probability': float,
                'threshold': float,
                'message': str
            }
        """
        if self.model is None:
            self._load_or_train()

        active_threshold = self.decision_threshold if threshold is None else validate_decision_threshold(threshold)

        import pandas as pd
        input_data = pd.DataFrame(
            [[avg_score, quizzes_count, time_per_q, difficulty, consistency]],
            columns=FEATURE_NAMES
        )
        probabilities = self.model.predict_proba(input_data)[0]
        prob_at_risk = float(probabilities[1])
        risk_prob = float(round(prob_at_risk * 100, 1))

        is_at_risk = (prob_at_risk >= active_threshold)

        if is_at_risk:
            return {
                'status': 'At Risk',
                'badge': 'warning',
                'risk_probability': risk_prob,
                'threshold': active_threshold,
                'message': 'ML indicator signals a need for targeted foundational revision before taking timed mock exams.'
            }
        else:
            return {
                'status': 'On Track',
                'badge': 'success',
                'risk_probability': risk_prob,
                'threshold': active_threshold,
                'message': 'ML indicator projects strong concept retention. Maintain pace and focus on speed.'
            }


_predictor_instance = None

def evaluate_and_train_model(decision_threshold=None):
    """Helper function to obtain or train predictor."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = StudentRiskPredictor(decision_threshold=decision_threshold)
    elif decision_threshold is not None:
        _predictor_instance.decision_threshold = validate_decision_threshold(decision_threshold)
    return _predictor_instance

