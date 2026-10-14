from ml.dataset import generate_synthetic_student_data
from ml.performance_predictor import StudentRiskPredictor

def test_synthetic_dataset_structure():
    df = generate_synthetic_student_data(n_samples=100)
    expected_cols = [
        'avg_score_past', 'quizzes_attempted', 'time_per_question',
        'difficulty_level', 'consistency_score', 'needs_intervention'
    ]
    for col in expected_cols:
        assert col in df.columns
    assert len(df) == 100
    assert set(df['needs_intervention'].unique()).issubset({0, 1})

def test_ml_predictor_training_and_metrics():
    predictor = StudentRiskPredictor()
    metrics = predictor.metrics
    assert 'baseline_accuracy' in metrics
    assert 'model_accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1_score' in metrics
    assert 'confusion_matrix' in metrics

    # Predict risk for high-performing vs struggling student
    high_performer = predictor.predict(avg_score=90.0, quizzes_count=20, time_per_q=30.0, difficulty=1, consistency=9)
    assert high_performer['status'] == 'On Track'

    struggling = predictor.predict(avg_score=35.0, quizzes_count=2, time_per_q=90.0, difficulty=3, consistency=1)
    assert struggling['status'] == 'At Risk'
    assert struggling['risk_probability'] > 50.0


import hashlib
from ml.evaluate_model import evaluate_saved_model
from ml.performance_predictor import MODEL_FILE

def test_evaluate_saved_model_held_out_reproducibility():
    """Verify read-only evaluation matches expected held-out metrics on reproducible synthetic split."""
    # Record initial hash to verify artifact is not touched
    with open(MODEL_FILE, 'rb') as f:
        initial_hash = hashlib.sha256(f.read()).hexdigest()

    results = evaluate_saved_model(split='held_out', n_samples=600, random_seed=42)

    assert results['test_samples'] == 150
    assert results['baseline_accuracy'] == 0.7467
    assert results['model_accuracy'] == 0.7667
    assert results['precision'] == 0.56
    assert results['recall'] == 0.3684
    assert results['f1_score'] == 0.4444
    assert results['confusion_matrix'] == [[101, 11], [24, 14]]
    assert results['class_distribution'] == {'class_0_on_track': 112, 'class_1_at_risk': 38}

    # Verify disclosures
    assert results['disclosures']['is_synthetic'] is True
    assert "synthetic benchmark dataset" in results['disclosures']['real_world_applicability'].lower()
    assert "do not establish" in results['disclosures']['real_world_applicability'].lower()

    # Verify file hash is unchanged (read-only verification)
    with open(MODEL_FILE, 'rb') as f:
        final_hash = hashlib.sha256(f.read()).hexdigest()
    assert initial_hash == final_hash


def test_evaluate_saved_model_independent_synthetic_cohort():
    """Verify read-only evaluation executes on an independent unseen synthetic cohort."""
    results = evaluate_saved_model(split='independent', n_samples=300, random_seed=777)

    assert results['test_samples'] == 300
    assert 0.0 <= results['model_accuracy'] <= 1.0
    assert 0.0 <= results['baseline_accuracy'] <= 1.0
    assert 0.0 <= results['f1_score'] <= 1.0
    assert len(results['confusion_matrix']) == 2
    assert results['disclosures']['is_synthetic'] is True


import pytest
from ml.performance_predictor import (
    DEFAULT_DECISION_THRESHOLD, validate_decision_threshold
)

def test_default_decision_threshold_preserved():
    """Verify default decision threshold remains 0.50 and preserves baseline predictions."""
    assert DEFAULT_DECISION_THRESHOLD == 0.50

    predictor = StudentRiskPredictor()
    assert predictor.decision_threshold == 0.50

    # High-performer profile
    high_performer = predictor.predict(
        avg_score=90.0, quizzes_count=20, time_per_q=30.0, difficulty=1, consistency=9
    )
    assert high_performer['status'] == 'On Track'
    assert high_performer['threshold'] == 0.50

    # Struggling profile
    struggling = predictor.predict(
        avg_score=35.0, quizzes_count=2, time_per_q=90.0, difficulty=3, consistency=1
    )
    assert struggling['status'] == 'At Risk'
    assert struggling['threshold'] == 0.50
    assert struggling['risk_probability'] > 50.0


def test_custom_decision_threshold_30_behavior():
    """
    Verify custom threshold 0.30 correctly reclassifies borderline profile.

    NOTE: This threshold is evaluated on synthetic benchmark distributions (ml/dataset.py)
    to study recall/precision trade-offs; it is NOT validated on real human students.
    """
    predictor = StudentRiskPredictor()  # default 0.50

    # Borderline profile whose posterior risk is ~41.6% (between 0.30 and 0.50)
    profile = {
        'avg_score': 60.0,
        'quizzes_count': 5,
        'time_per_q': 55.0,
        'difficulty': 2,
        'consistency': 3
    }

    # At default threshold 0.50: risk_prob 41.6% is below 50% -> 'On Track'
    res_default = predictor.predict(**profile)
    assert res_default['status'] == 'On Track'
    assert res_default['threshold'] == 0.50
    assert 35.0 < res_default['risk_probability'] < 45.0

    # At custom threshold 0.30 via method parameter: 41.6% >= 30.0% -> 'At Risk'
    res_custom = predictor.predict(**profile, threshold=0.30)
    assert res_custom['status'] == 'At Risk'
    assert res_custom['threshold'] == 0.30
    assert res_custom['risk_probability'] == res_default['risk_probability']

    # At instance-level configuration:
    predictor_30 = StudentRiskPredictor(decision_threshold=0.30)
    assert predictor_30.decision_threshold == 0.30
    res_inst = predictor_30.predict(**profile)
    assert res_inst['status'] == 'At Risk'
    assert res_inst['threshold'] == 0.30


def test_decision_threshold_validation_and_invalid_values():
    """Verify threshold boundary validation strictly enforces [0.0, 1.0] and rejects invalid types."""
    # Valid boundaries
    assert validate_decision_threshold(0.0) == 0.0
    assert validate_decision_threshold(1.0) == 1.0
    assert validate_decision_threshold(0.30) == 0.30
    assert validate_decision_threshold(0.5) == 0.5

    # Invalid numeric ranges
    for invalid_val in [-0.5, -0.01, 1.01, 2.0, 100.0]:
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            validate_decision_threshold(invalid_val)

        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            StudentRiskPredictor(decision_threshold=invalid_val)

    # Invalid types
    for invalid_type in ["0.30", "high", None, True, False, [0.5]]:
        with pytest.raises(ValueError):
            validate_decision_threshold(invalid_type)

    # Method-level threshold validation
    predictor = StudentRiskPredictor()
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        predictor.predict(avg_score=70.0, quizzes_count=5, threshold=-0.1)

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        predictor.predict(avg_score=70.0, quizzes_count=5, threshold=1.2)

    with pytest.raises(ValueError):
        predictor.predict(avg_score=70.0, quizzes_count=5, threshold="invalid")


