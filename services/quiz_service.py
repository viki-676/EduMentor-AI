import random
from datetime import datetime, timezone
from models import db, Question, QuizAttempt, StudentAnswer

def get_eligible_questions_query(learning_path, subject_or_category, exam_name=None, difficulty=None):
    """Build query for eligible questions based on filters, supporting topics and subject aliases."""
    target_str = (subject_or_category or '').strip()

    # Topic-to-subject & synonym normalization mapping
    alias_map = {
        'Python Lists': (['Python Programming'], ['Python Lists']),
        'Python Tuples': (['Python Programming'], ['Python Tuples']),
        'Python Dictionaries': (['Python Programming'], ['Python Dictionaries']),
        'Python Sets': (['Python Programming'], ['Python Sets']),
        'Python Functions': (['Python Programming'], ['Python Functions']),
        'Python Loops': (['Python Programming'], ['Python Loops']),
        'Python OOP': (['Python Programming'], ['Python OOP', 'Object-Oriented Programming']),
        'Data Structures and Algorithms': (['Data Structures', 'Data Structures and Algorithms'], ['Data Structures and Algorithms']),
        'Data Structures': (['Data Structures', 'Data Structures and Algorithms'], None),
        'Database Management Systems (DBMS)': (['Database Management Systems (DBMS)', 'DBMS and SQL', 'DBMS'], None),
        'DBMS and SQL': (['Database Management Systems (DBMS)', 'DBMS and SQL', 'DBMS'], ['DBMS and SQL']),
        'DBMS': (['Database Management Systems (DBMS)', 'DBMS and SQL', 'DBMS'], None),
        'English Language and Grammar': (['English Language', 'English Language and Grammar'], ['English Language and Grammar']),
        'English Language': (['English Language', 'English Language and Grammar'], None),
    }

    query = Question.query
    if learning_path:
        query = query.filter_by(learning_path=learning_path)

    if target_str in alias_map:
        subjects, topics = alias_map[target_str]
        if topics:
            # Query targeted at a specific topic
            query = query.filter(
                (Question.topic.in_(topics)) | 
                (Question.subject_or_category == target_str)
            )
        else:
            # Query targeted at a broader subject
            query = query.filter(Question.subject_or_category.in_(subjects))
    else:
        # Direct matching by subject OR topic
        query = query.filter(
            (Question.subject_or_category == target_str) |
            (Question.topic == target_str)
        )

    if difficulty and difficulty.lower() != 'all':
        query = query.filter(Question.difficulty.ilike(difficulty))

    if exam_name and exam_name != 'All':
        query = query.filter(
            (Question.target_exam == exam_name) | 
            (Question.target_exam == 'All') | 
            (Question.target_exam == None)
        )

    return query


def count_eligible_questions(learning_path, subject_or_category, exam_name=None, difficulty=None):
    """Return count of matching questions in the database."""
    return get_eligible_questions_query(learning_path, subject_or_category, exam_name, difficulty).count()


def get_quiz_questions(learning_path, subject_or_category, exam_name=None, limit=5, difficulty=None):
    """
    Fetch questions matching criteria without replacement up to limit.
    Returns (selected_questions, total_available)
    """
    query = get_eligible_questions_query(learning_path, subject_or_category, exam_name, difficulty)
    all_questions = query.all()

    total_available = len(all_questions)
    if total_available == 0:
        # Fallback to general questions for that path if category specific is missing
        fallback_query = Question.query.filter_by(learning_path=learning_path)
        all_questions = fallback_query.all()
        total_available = len(all_questions)

    # Sample without replacement up to limit
    count = min(limit, len(all_questions))
    selected = random.sample(all_questions, count) if count > 0 else []
    return selected, total_available


def submit_quiz_attempt(user_id, learning_path, subject_or_category, exam_name, answers_dict, time_taken_seconds=0, time_limit_minutes=0):
    """
    Process quiz answers, compute score, save attempt and answer records with time limit and status.
    answers_dict format: {'question_id': 'A'|'B'|'C'|'D'}
    Returns (attempt, breakdown)
    """
    question_ids = [int(qid) for qid in answers_dict.keys()]
    questions = Question.query.filter(Question.id.in_(question_ids)).all() if question_ids else []
    question_map = {q.id: q for q in questions}

    total_questions = len(question_ids)
    score = 0
    breakdown = []

    time_spent = max(1, int(time_taken_seconds or 0))
    limit_mins = max(0, int(time_limit_minutes or 0))

    # Evaluate completion status
    status = 'completed'
    if limit_mins > 0 and time_spent > (limit_mins * 60 + 15):
        status = 'timed_out'

    # Create the attempt object
    attempt = QuizAttempt(
        user_id=user_id,
        learning_path=learning_path,
        subject_or_category=subject_or_category,
        exam_name=exam_name,
        total_questions=total_questions,
        score=0,
        percentage=0.0,
        time_taken_seconds=time_spent,
        time_limit_minutes=limit_mins,
        status=status
    )
    db.session.add(attempt)
    db.session.flush() # assign attempt.id

    for qid_str, selected_opt in answers_dict.items():
        qid = int(qid_str)
        q = question_map.get(qid)
        if not q:
            continue

        selected_opt = (selected_opt or '').strip().upper()
        is_correct = (selected_opt == q.correct_option)
        if is_correct:
            score += 1

        student_ans = StudentAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=selected_opt,
            is_correct=is_correct
        )
        db.session.add(student_ans)

        breakdown.append({
            'question_id': q.id,
            'question_text': q.question_text,
            'topic': q.topic,
            'difficulty': q.difficulty,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c,
                'D': q.option_d
            },
            'selected_option': selected_opt,
            'correct_option': q.correct_option,
            'is_correct': is_correct,
            'explanation': q.explanation
        })

    percentage = (score / total_questions * 100.0) if total_questions > 0 else 0.0
    attempt.score = score
    attempt.percentage = round(percentage, 2)
    db.session.commit()

    return attempt, breakdown

def get_user_analytics(user_id):
    """
    Calculate comprehensive performance metrics, topic mastery, and timeline data for Chart.js.
    """
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.created_at.asc()).all()

    total_quizzes = len(attempts)
    if total_quizzes == 0:
        return {
            'total_quizzes': 0,
            'overall_accuracy': 0.0,
            'total_questions_attempted': 0,
            'total_correct': 0,
            'recent_attempts': [],
            'topic_performance': {},
            'subject_performance': {},
            'score_timeline': {'labels': [], 'scores': []},
            'weak_topics': [],
            'strong_topics': [],
            'avg_time_per_question': 45.0,
            'avg_difficulty': 2
        }

    total_questions = sum(a.total_questions for a in attempts)
    total_score = sum(a.score for a in attempts)
    overall_accuracy = round((total_score / total_questions * 100.0), 1) if total_questions > 0 else 0.0

    # Calculate avg_time_per_question:
    # Total time_taken_seconds across all attempts divided by total questions attempted,
    # clamped between 10.0 and 120.0 seconds. Defaults to 45.0 when valid timing data is unavailable.
    total_time_taken = sum(int(a.time_taken_seconds or 0) for a in attempts)
    if total_questions > 0 and total_time_taken > 0:
        raw_time_per_q = total_time_taken / total_questions
        avg_time_per_question = round(max(10.0, min(120.0, float(raw_time_per_q))), 1)
    else:
        avg_time_per_question = 45.0

    # Score timeline for Chart.js
    timeline_labels = [f"Quiz #{i+1} ({a.subject_or_category[:12]}..)" for i, a in enumerate(attempts[-10:])]
    timeline_scores = [a.percentage for a in attempts[-10:]]

    # Topic-wise performance calculation from individual answers
    topic_stats = {}
    subject_stats = {}
    diff_ratings = []
    diff_map = {'easy': 1, 'medium': 2, 'hard': 3}

    attempt_ids = [a.id for a in attempts]
    answers = StudentAnswer.query.filter(StudentAnswer.attempt_id.in_(attempt_ids)).all()

    for ans in answers:
        if not ans.question:
            continue

        # Collect question difficulty rating (Easy=1, Medium=2, Hard=3)
        q_diff = ans.question.difficulty
        if q_diff:
            mapped_diff = diff_map.get(str(q_diff).strip().lower())
            if mapped_diff is not None:
                diff_ratings.append(mapped_diff)

        topic = ans.question.topic
        subject = ans.question.subject_or_category

        # Topic breakdown
        if topic not in topic_stats:
            topic_stats[topic] = {'total': 0, 'correct': 0, 'subject': subject}
        topic_stats[topic]['total'] += 1
        if ans.is_correct:
            topic_stats[topic]['correct'] += 1

        # Subject breakdown
        if subject not in subject_stats:
            subject_stats[subject] = {'total': 0, 'correct': 0}
        subject_stats[subject]['total'] += 1
        if ans.is_correct:
            subject_stats[subject]['correct'] += 1

    # Calculate avg_difficulty:
    # Average of mapped difficulty levels rounded to nearest integer. Defaults to 2 if unavailable.
    if diff_ratings:
        avg_difficulty = int(round(sum(diff_ratings) / len(diff_ratings)))
    else:
        avg_difficulty = 2

    # Calculate accuracy per topic
    for topic, data in topic_stats.items():
        data['accuracy'] = round((data['correct'] / data['total'] * 100.0), 1) if data['total'] > 0 else 0.0

    # Calculate accuracy per subject
    for subject, data in subject_stats.items():
        data['accuracy'] = round((data['correct'] / data['total'] * 100.0), 1) if data['total'] > 0 else 0.0

    # Categorize weak (< 60%) vs strong (>= 75%) topics
    weak_topics = sorted(
        [{'topic': k, **v} for k, v in topic_stats.items() if v['accuracy'] < 60.0],
        key=lambda x: x['accuracy']
    )
    strong_topics = sorted(
        [{'topic': k, **v} for k, v in topic_stats.items() if v['accuracy'] >= 75.0],
        key=lambda x: x['accuracy'],
        reverse=True
    )

    recent_attempts = [a.to_dict() for a in reversed(attempts[-5:])]

    return {
        'total_quizzes': total_quizzes,
        'overall_accuracy': overall_accuracy,
        'total_questions_attempted': total_questions,
        'total_correct': total_score,
        'recent_attempts': recent_attempts,
        'topic_performance': topic_stats,
        'subject_performance': subject_stats,
        'score_timeline': {
            'labels': timeline_labels,
            'scores': timeline_scores
        },
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'avg_time_per_question': avg_time_per_question,
        'avg_difficulty': avg_difficulty
    }
