from models import User, Question, QuizAttempt, StudentAnswer, db
from services.quiz_service import get_user_analytics
from services.recommendation import generate_personalized_recommendations

def test_analytics_and_weak_topic_detection(app):
    with app.app_context():
        user = User(username='analyst', email='analyst@test.com', full_name='Analyst User')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        # Add questions
        q1 = Question.query.filter_by(subject_or_category='Python Programming').first()
        q2 = Question.query.filter_by(subject_or_category='Data Structures').first()

        # Attempt with 1 correct and 1 incorrect
        attempt = QuizAttempt(
            user_id=user.id,
            learning_path='college',
            subject_or_category='Python Programming',
            total_questions=2,
            score=1,
            percentage=50.0
        )
        db.session.add(attempt)
        db.session.flush()

        ans1 = StudentAnswer(attempt_id=attempt.id, question_id=q1.id, selected_option=q1.correct_option, is_correct=True)
        # wrong answer for q2
        wrong_opt = 'A' if q2.correct_option != 'A' else 'B'
        ans2 = StudentAnswer(attempt_id=attempt.id, question_id=q2.id, selected_option=wrong_opt, is_correct=False)
        db.session.add_all([ans1, ans2])
        db.session.commit()

        analytics = get_user_analytics(user.id)
        assert analytics['total_quizzes'] == 1
        assert analytics['overall_accuracy'] == 50.0

        # Verify weak topic detection
        recs = generate_personalized_recommendations(user.id)
        assert len(recs['weak_topics']) > 0
        assert recs['weak_topics'][0]['topic'] == q2.topic
        assert len(recs['study_plan']) > 0

def test_dashboard_route_with_analytics(auth_client):
    res = auth_client.get('/dashboard')
    assert res.status_code == 200
    assert b"Student Dashboard" in res.data
    assert b"Predictive Student Performance & Risk Model" in res.data


from unittest.mock import patch

def test_dashboard_ml_prediction_with_real_telemetry(auth_client, app):
    """Verify /dashboard invokes predictor.predict with real telemetry metrics."""
    with app.app_context():
        user = User.query.filter_by(username='teststudent').first()
        q1 = Question.query.filter_by(difficulty='Easy').first()
        q2 = Question.query.filter_by(difficulty='Hard').first()

        # Create attempt with 2 questions and 60 seconds time_taken (30.0s per question)
        attempt = QuizAttempt(
            user_id=user.id,
            learning_path='college',
            subject_or_category='Python Programming',
            total_questions=2,
            score=2,
            percentage=100.0,
            time_taken_seconds=60
        )
        db.session.add(attempt)
        db.session.flush()

        ans1 = StudentAnswer(attempt_id=attempt.id, question_id=q1.id, selected_option='A', is_correct=True)
        ans2 = StudentAnswer(attempt_id=attempt.id, question_id=q2.id, selected_option='B', is_correct=True)
        db.session.add_all([ans1, ans2])
        db.session.commit()

    with patch('ml.performance_predictor.StudentRiskPredictor.predict') as mock_predict:
        mock_predict.return_value = {
            'status': 'On Track',
            'badge': 'success',
            'risk_probability': 12.5,
            'message': 'ML indicator projects strong concept retention.'
        }

        res = auth_client.get('/dashboard')
        assert res.status_code == 200
        assert b"Status: On Track (12.5% Risk)" in res.data

        # Verify real telemetry arguments passed to predict
        mock_predict.assert_called_once()
        kwargs = mock_predict.call_args[1]
        assert kwargs['avg_score'] == 100.0
        assert kwargs['quizzes_count'] == 1
        assert kwargs['time_per_q'] == 30.0
        assert kwargs['difficulty'] == 2  # (1 Easy + 3 Hard) / 2 = 2
        assert 1 <= kwargs['consistency'] <= 10


def test_dashboard_real_end_to_end_prediction(auth_client, app):
    """Verify unmocked end-to-end execution of Scikit-Learn predictor via /dashboard."""
    with app.app_context():
        user = User.query.filter_by(username='teststudent').first()
        q = Question.query.first()
        attempt = QuizAttempt(
            user_id=user.id,
            learning_path='college',
            subject_or_category='Python Programming',
            total_questions=1,
            score=1,
            percentage=100.0,
            time_taken_seconds=40
        )
        db.session.add(attempt)
        db.session.flush()
        ans = StudentAnswer(attempt_id=attempt.id, question_id=q.id, selected_option='A', is_correct=True)
        db.session.add(ans)
        db.session.commit()

    res = auth_client.get('/dashboard')
    assert res.status_code == 200
    assert b"Status:" in res.data
    assert b"% Risk)" in res.data


