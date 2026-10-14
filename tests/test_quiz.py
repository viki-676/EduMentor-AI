from models import Question, QuizAttempt, StudentAnswer, User, db

def test_quiz_view_loads_questions(auth_client):
    response = auth_client.get('/quiz?path=college&subject=Python+Programming')
    assert response.status_code == 200
    assert b"Python Programming" in response.data
    assert b"Question 1 of" in response.data

def test_quiz_submission_and_persistence(auth_client, app):
    with app.app_context():
        q1 = Question.query.filter_by(subject_or_category='Python Programming').first()
        assert q1 is not None
        correct_opt = q1.correct_option
        q1_id = q1.id

    # Submit quiz with correct answer for q1
    res = auth_client.post('/quiz/submit', data={
        'learning_path': 'college',
        'subject': 'Python Programming',
        f'answer_{q1_id}': correct_opt,
        'time_taken_seconds': 45
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Quiz Results" in res.data
    assert b"100.0% Accuracy" in res.data

    # Verify attempt in DB
    with app.app_context():
        attempt = QuizAttempt.query.order_by(QuizAttempt.id.desc()).first()
        assert attempt is not None
        assert attempt.score == 1
        assert attempt.total_questions == 1
        assert attempt.percentage == 100.0

        ans = StudentAnswer.query.filter_by(attempt_id=attempt.id).first()
        assert ans is not None
        assert ans.is_correct is True

def test_private_result_access_control(auth_client, app):
    """Ensure user B cannot inspect user A's private quiz attempt."""
    with app.app_context():
        # Create student B
        user_b = User(username='otherstudent', email='other@example.com', full_name='Other Student')
        user_b.set_password('pass123')
        db.session.add(user_b)
        db.session.commit()

        # Create attempt owned by user B
        attempt_b = QuizAttempt(
            user_id=user_b.id,
            learning_path='college',
            subject_or_category='DBMS',
            total_questions=5,
            score=4,
            percentage=80.0
        )
        db.session.add(attempt_b)
        db.session.commit()
        attempt_b_id = attempt_b.id

    # auth_client is logged in as 'teststudent', NOT 'otherstudent'
    res = auth_client.get(f'/quiz/result/{attempt_b_id}', follow_redirects=True)
    assert b"Unauthorized access" in res.data


def test_quiz_custom_question_count(auth_client):
    """Verify custom question count (e.g. 10 MCQs) renders 10 questions."""
    response = auth_client.get('/quiz?path=college&subject=Python+Programming&count=10')
    assert response.status_code == 200
    assert b"Question 10 of 10" in response.data


def test_quiz_count_clamping_and_insufficient_bank(auth_client):
    """Verify requested count exceeding bank serves total available and warns student."""
    response = auth_client.get('/quiz?path=college&subject=Python+Programming&count=25')
    assert response.status_code == 200
    # Bank has 15 Python questions; should serve 15 and notice student
    assert b"Only 15 questions are available" in response.data or b"Question 15 of 15" in response.data


def test_quiz_submission_with_time_limit_and_timeout(auth_client, app):
    """Verify time_limit_minutes is recorded and timeout status is detected."""
    with app.app_context():
        q = Question.query.filter_by(subject_or_category='Python Programming').first()
        q_id = q.id

    # 5 min limit (300s), but student took 330s (exceeds 5m + 15s buffer)
    res = auth_client.post('/quiz/submit', data={
        'learning_path': 'competitive',
        'subject': 'Quantitative Aptitude',
        'time_limit_minutes': 5,
        'time_taken_seconds': 330,
        f'answer_{q_id}': 'A'
    }, follow_redirects=True)

    assert res.status_code == 200
    with app.app_context():
        attempt = QuizAttempt.query.order_by(QuizAttempt.id.desc()).first()
        assert attempt is not None
        assert attempt.time_limit_minutes == 5
        assert attempt.status == 'timed_out'


def test_quiz_available_count_api(auth_client):
    """Verify available count API endpoint returns accurate count."""
    res = auth_client.get('/api/quiz/available_count?path=college&subject=Python+Programming')
    assert res.status_code == 200
    data = res.get_json()
    assert 'available' in data
    assert data['available'] == 15


from services.quiz_service import get_user_analytics

def test_user_analytics_empty_records(app):
    """Verify analytics defaults for users with zero attempts."""
    with app.app_context():
        user = User(username='empty_student', email='empty@example.com', full_name='Empty Student')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        analytics = get_user_analytics(user.id)
        assert analytics['total_quizzes'] == 0
        assert analytics['overall_accuracy'] == 0.0
        assert analytics['avg_time_per_question'] == 45.0
        assert analytics['avg_difficulty'] == 2


def test_user_analytics_valid_telemetry_and_clamping(app):
    """Verify calculation of avg_time_per_question and avg_difficulty with boundary clamping."""
    with app.app_context():
        user = User(username='telemetry_student', email='telemetry@example.com', full_name='Telemetry Student')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        q_easy = Question.query.filter_by(difficulty='Easy').first()
        q_hard = Question.query.filter_by(difficulty='Hard').first()
        if not q_easy:
            q_easy = Question(learning_path='college', subject_or_category='Python', topic='Basics', difficulty='Easy', question_text='Q1?', option_a='A', option_b='B', option_c='C', option_d='D', correct_option='A', explanation='Exp')
            db.session.add(q_easy)
        if not q_hard:
            q_hard = Question(learning_path='college', subject_or_category='Python', topic='Adv', difficulty='Hard', question_text='Q2?', option_a='A', option_b='B', option_c='C', option_d='D', correct_option='B', explanation='Exp')
            db.session.add(q_hard)
        db.session.commit()

        # 1. Normal attempt: 2 questions, 60s total -> 30.0s per question
        # Easy (1) + Hard (3) -> avg difficulty = (1+3)/2 = 2
        attempt1 = QuizAttempt(
            user_id=user.id, learning_path='college', subject_or_category='Python',
            total_questions=2, score=2, percentage=100.0, time_taken_seconds=60
        )
        db.session.add(attempt1)
        db.session.flush()

        ans1 = StudentAnswer(attempt_id=attempt1.id, question_id=q_easy.id, selected_option='A', is_correct=True)
        ans2 = StudentAnswer(attempt_id=attempt1.id, question_id=q_hard.id, selected_option='B', is_correct=True)
        db.session.add_all([ans1, ans2])
        db.session.commit()

        analytics = get_user_analytics(user.id)
        assert analytics['avg_time_per_question'] == 30.0
        assert analytics['avg_difficulty'] == 2

        # 2. Add ultra-fast attempt to test minimum clamping (10.0s floor)
        # Total questions: 2 + 10 = 12, total time: 60 + 10 = 70s -> 70/12 = 5.8s -> clamped to 10.0s
        attempt_fast = QuizAttempt(
            user_id=user.id, learning_path='college', subject_or_category='Python',
            total_questions=10, score=10, percentage=100.0, time_taken_seconds=10
        )
        db.session.add(attempt_fast)
        db.session.commit()

        analytics_fast = get_user_analytics(user.id)
        assert analytics_fast['avg_time_per_question'] == 10.0

        # 3. Add ultra-slow attempt to test maximum clamping (120.0s ceiling)
        user_slow = User(username='slow_student', email='slow@example.com', full_name='Slow Student')
        user_slow.set_password('pass123')
        db.session.add(user_slow)
        db.session.commit()

        attempt_slow = QuizAttempt(
            user_id=user_slow.id, learning_path='college', subject_or_category='Python',
            total_questions=1, score=1, percentage=100.0, time_taken_seconds=500
        )
        db.session.add(attempt_slow)
        db.session.commit()

        analytics_slow = get_user_analytics(user_slow.id)
        assert analytics_slow['avg_time_per_question'] == 120.0


def test_user_analytics_missing_or_null_data(app):
    """Verify safe fallback to 45.0s and 2 when time or difficulty values are missing/null."""
    with app.app_context():
        user = User(username='null_student', email='null@example.com', full_name='Null Student')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        # Attempt with time_taken_seconds=0
        attempt = QuizAttempt(
            user_id=user.id, learning_path='college', subject_or_category='Python',
            total_questions=2, score=1, percentage=50.0, time_taken_seconds=0
        )
        db.session.add(attempt)
        db.session.flush()

        # Question with unknown difficulty
        q_unknown = Question(
            learning_path='college', subject_or_category='Python', topic='Unknown',
            difficulty='', question_text='Q?', option_a='A', option_b='B', option_c='C', option_d='D',
            correct_option='A', explanation='Exp'
        )
        db.session.add(q_unknown)
        db.session.flush()

        ans = StudentAnswer(attempt_id=attempt.id, question_id=q_unknown.id, selected_option='A', is_correct=True)
        db.session.add(ans)
        db.session.commit()

        analytics = get_user_analytics(user.id)
        # Timing was 0 -> fallback to 45.0
        assert analytics['avg_time_per_question'] == 45.0
        # Difficulty unrecognized -> fallback to 2
        assert analytics['avg_difficulty'] == 2


import re

def test_quiz_view_renders_all_options_and_radio_controls(auth_client, app):
    """Verify that all questions render visible radio inputs, badges, and option text."""
    res = auth_client.get('/quiz?path=college&subject=Python+Programming&count=3')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Verify quiz option container and controls
    assert "quiz-options-group" in html
    assert "quiz-option-wrapper" in html
    assert "quiz-option-label" in html
    assert "option-badge" in html
    assert "option-text" in html

    # Verify radio buttons are rendered with form-check-input and quiz-option-input (not hidden btn-check)
    radio_matches = re.findall(r'<input\s+type="radio"[^>]*class="form-check-input quiz-option-input[^"]*"[^>]*name="answer_(\d+)"[^>]*id="opt_(\d+)_([A-D])"[^>]*value="([A-D])"', html)
    assert len(radio_matches) >= 3 * 4  # 3 questions * 4 options each

    # Verify each radio button has a properly paired label
    for qid, qid2, opt_key, opt_val in radio_matches:
        assert qid == qid2
        assert opt_key == opt_val
        expected_label_for = f'for="opt_{qid}_{opt_key}"'
        assert expected_label_for in html


def test_quiz_view_dark_theme_and_empty_options_handling(auth_client, app):
    """Verify dark theme rendering and safe graceful handling of missing/empty option data."""
    with app.app_context():
        user = User.query.filter_by(username='teststudent').first()
        user.theme_preference = 'dark'
        db.session.commit()

        # Add a question with partial options (only A and B)
        q_partial = Question(
            learning_path='college',
            subject_or_category='Python Programming',
            topic='Edge Cases',
            difficulty='Easy',
            question_text='Is Python interpreted?',
            option_a='Yes, it is bytecode interpreted.',
            option_b='No, it compiles directly to machine code.',
            option_c='   ',
            option_d='',
            correct_option='A',
            explanation='Python compiles to bytecode which runs on the PVM.'
        )
        db.session.add(q_partial)
        db.session.commit()

    res = auth_client.get('/quiz?path=college&subject=Python+Programming&count=50')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Verify dark theme attribute is rendered
    assert 'data-bs-theme="dark"' in html

    # Verify options A and B are rendered
    assert "Yes, it is bytecode interpreted." in html
    assert "No, it compiles directly to machine code." in html


def test_question_model_options_property(app):
    """Verify Question.options property returns ordered dictionary and handles empty options."""
    with app.app_context():
        q_full = Question.query.filter_by(subject_or_category='Python Programming').first()
        assert q_full is not None
        opts = q_full.options
        assert isinstance(opts, dict)
        assert set(opts.keys()) == {'A', 'B', 'C', 'D'}
        assert opts['A'] == q_full.option_a
        assert opts['B'] == q_full.option_b
        assert opts['C'] == q_full.option_c
        assert opts['D'] == q_full.option_d

        # Verify to_dict includes options mapping
        d = q_full.to_dict()
        assert 'options' in d
        assert d['options'] == opts

        # Verify partial question options filtering
        q_sparse = Question(
            learning_path='college', subject_or_category='Test', topic='Test',
            question_text='Sparse?', option_a='Opt A', option_b='Opt B',
            option_c='', option_d=None, correct_option='A', explanation='Exp'
        )
        sparse_opts = q_sparse.options
        assert sparse_opts == {'A': 'Opt A', 'B': 'Opt B'}



