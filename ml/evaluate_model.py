"""
Read-Only Evaluation Script for EduMentor AI Student Risk Predictor.

DISCLOSURE & TRANSPARENCY:
This evaluation assesses the saved model artifact ('ml/risk_model.joblib')
strictly on synthetic benchmark datasets generated from mathematical distributions.
These metrics DO NOT establish or validate predictive accuracy on real human students.

CONSTRAINTS:
- Strictly read-only evaluation.
- Does not modify, retrain, or overwrite 'ml/risk_model.joblib'.
- Does not alter database records, schemas, or application configurations.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from .dataset import generate_synthetic_student_data
    from .performance_predictor import FEATURE_NAMES, MODEL_FILE
except (ImportError, ValueError):
    from ml.dataset import generate_synthetic_student_data
    from ml.performance_predictor import FEATURE_NAMES, MODEL_FILE


def evaluate_saved_model(split='held_out', n_samples=600, random_seed=42):
    """
    Evaluates the saved risk_model.joblib on a reproducible synthetic test set.

    Args:
        split: 'held_out' (stratified 25% split from seed=42 dataset, N=150)
               or 'independent' (fresh synthetic cohort with independent seed).
        n_samples: Total synthetic dataset size.
        random_seed: Random seed for synthetic dataset generation.

    Returns:
        dict containing accuracy, precision, recall, f1_score,
        confusion_matrix, baseline_accuracy, and academic disclosures.
    """
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"Model artifact not found at {MODEL_FILE}")

    # Load model strictly read-only
    payload = joblib.load(MODEL_FILE)
    model = payload['pipeline']

    if split == 'held_out':
        # Recreate the exact reproducible 25% held-out stratified test split (N=150)
        df = generate_synthetic_student_data(n_samples=n_samples, random_seed=random_seed)
        X = df[FEATURE_NAMES]
        y = df['needs_intervention']
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.25, random_state=random_seed, stratify=y
        )
        dataset_description = f"Reproducible held-out test split (test_size=0.25, seed={random_seed}, N={len(y_test)})"
    else:
        # Generate independent synthetic cohort
        df = generate_synthetic_student_data(n_samples=n_samples, random_seed=random_seed)
        X_test = df[FEATURE_NAMES]
        y_test = df['needs_intervention']
        dataset_description = f"Independent synthetic cohort (seed={random_seed}, N={len(y_test)})"

    # 1. Majority-class Baseline
    baseline = DummyClassifier(strategy='most_frequent')
    baseline.fit(X_test, y_test)
    y_base_pred = baseline.predict(X_test)
    baseline_acc = float(accuracy_score(y_test, y_base_pred))

    # 2. Model Predictions
    y_pred = model.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Class distribution
    class_counts = {
        'class_0_on_track': int(np.sum(y_test == 0)),
        'class_1_at_risk': int(np.sum(y_test == 1))
    }

    results = {
        'split_type': split,
        'dataset_description': dataset_description,
        'test_samples': len(y_test),
        'class_distribution': class_counts,
        'baseline_accuracy': round(baseline_acc, 4),
        'model_accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm,
        'disclosures': {
            'is_synthetic': True,
            'dataset_origin': 'Synthetic benchmark generator (ml/dataset.py)',
            'real_world_applicability': (
                'These metrics are measured strictly on a synthetic benchmark dataset. '
                'They do NOT establish, validate, or claim real-world predictive performance on human students.'
            ),
            'model_artifact_status': 'Loaded read-only; ml/risk_model.joblib is unmodified.'
        }
    }

    return results


def print_evaluation_report(results=None):
    """Print structured text report suitable for CLI evaluation."""
    if results is None:
        results = evaluate_saved_model(split='held_out', n_samples=600, random_seed=42)

    cm = results['confusion_matrix']
    print("=" * 70)
    print("  EduMentor AI -- Student Risk Predictor Read-Only Model Evaluation")
    print("=" * 70)
    print(f"Dataset:              {results['dataset_description']}")
    print(f"Sample Count:         {results['test_samples']} instances")
    print(f"Class Balance:        On-Track (0): {results['class_distribution']['class_0_on_track']} | At-Risk (1): {results['class_distribution']['class_1_at_risk']}")
    print("-" * 70)
    print(f"Baseline Accuracy:    {results['baseline_accuracy'] * 100:.2f}%  (DummyClassifier / Majority Class)")
    print(f"Model Accuracy:       {results['model_accuracy'] * 100:.2f}%")
    print(f"Precision (At-Risk):  {results['precision'] * 100:.2f}%")
    print(f"Recall (At-Risk):     {results['recall'] * 100:.2f}%")
    print(f"F1-Score:             {results['f1_score']:.4f}")
    print("-" * 70)
    print("Confusion Matrix:")
    print(f"  True Negatives (On-Track -> On-Track):  {cm[0][0]:>3}")
    print(f"  False Positives (On-Track -> At-Risk):  {cm[0][1]:>3}")
    print(f"  False Negatives (At-Risk -> On-Track):  {cm[1][0]:>3}  <-- Missed at-risk cases")
    print(f"  True Positives  (At-Risk -> At-Risk):   {cm[1][1]:>3}")
    print("-" * 70)
    print("Scientific Transparency Notice:")
    print(f"  {results['disclosures']['real_world_applicability']}")
    print("=" * 70)


if __name__ == '__main__':
    print_evaluation_report()
