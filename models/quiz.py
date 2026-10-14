from datetime import datetime, timezone
from . import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    learning_path = db.Column(db.String(30), nullable=False, index=True)   # 'college' or 'competitive'
    subject_or_category = db.Column(db.String(100), nullable=False, index=True)
    topic = db.Column(db.String(100), nullable=False, index=True)
    difficulty = db.Column(db.String(20), default='Medium', nullable=False) # 'Easy', 'Medium', 'Hard'
    target_exam = db.Column(db.String(50), nullable=True, index=True)      # e.g., 'SSC', 'All'
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)               # 'A', 'B', 'C', or 'D'
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def options(self) -> dict:
        """Returns ordered mapping of non-empty options A through D."""
        opts = {}
        for key, val in [('A', self.option_a), ('B', self.option_b), ('C', self.option_c), ('D', self.option_d)]:
            if val is not None and str(val).strip():
                opts[key] = val
        return opts

    def to_dict(self, include_answer: bool = False) -> dict:
        data = {
            'id': self.id,
            'learning_path': self.learning_path,
            'subject_or_category': self.subject_or_category,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'target_exam': self.target_exam,
            'question_text': self.question_text,
            'options': self.options
        }
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
        return data


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    learning_path = db.Column(db.String(30), nullable=False)
    subject_or_category = db.Column(db.String(100), nullable=False)
    exam_name = db.Column(db.String(50), nullable=True)
    total_questions = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken_seconds = db.Column(db.Integer, default=0, nullable=False)
    time_limit_minutes = db.Column(db.Integer, default=0, nullable=False)  # 0 means untimed
    status = db.Column(db.String(20), default='completed', nullable=False)  # 'completed' | 'timed_out'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    answers = db.relationship('StudentAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'learning_path': self.learning_path,
            'subject_or_category': self.subject_or_category,
            'exam_name': self.exam_name,
            'total_questions': self.total_questions,
            'score': self.score,
            'percentage': round(self.percentage, 2),
            'time_taken_seconds': self.time_taken_seconds,
            'time_limit_minutes': self.time_limit_minutes,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }


class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=True)
    is_correct = db.Column(db.Boolean, nullable=False)

    # Relationship to get question details
    question = db.relationship('Question', lazy=True)


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    topic = db.Column(db.String(100), nullable=False)
    subject_or_category = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    action_plan = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
