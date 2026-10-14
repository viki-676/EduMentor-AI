from datetime import datetime, timezone
from . import db

class PYQPaper(db.Model):
    __tablename__ = 'pyq_papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False) # e.g. "GATE 2023 Computer Science & IT"
    subject = db.Column(db.String(100), nullable=False, index=True)
    course = db.Column(db.String(80), nullable=False, index=True) # "B.Tech CSE", "BCA", "GATE", "SSC"
    exam_board = db.Column(db.String(100), nullable=False, index=True) # "IIT Kanpur (GATE)", "Anna University", "SSC"
    semester_or_stage = db.Column(db.String(50), nullable=True) # "Semester 5", "Tier 1", "Prelims"
    exam_year = db.Column(db.Integer, nullable=False, index=True)
    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    source_reference = db.Column(db.String(250), nullable=True)
    file_path = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    questions = db.relationship('PreviousYearQuestion', backref='paper', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def exam_name(self):
        return self.exam_board

    @property
    def year(self):
        return self.exam_year

    @property
    def board_or_university(self):
        return self.exam_board

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'course': self.course,
            'exam_board': self.exam_board,
            'semester_or_stage': self.semester_or_stage,
            'exam_year': self.exam_year,
            'is_verified': self.is_verified,
            'source_reference': self.source_reference,
            'question_count': self.questions.count()
        }


class PreviousYearQuestion(db.Model):
    __tablename__ = 'previous_year_questions'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('pyq_papers.id', ondelete='CASCADE'), nullable=True, index=True)
    subject = db.Column(db.String(100), nullable=False, index=True)
    course = db.Column(db.String(80), nullable=True)
    exam_board = db.Column(db.String(100), nullable=True, index=True)
    exam_year = db.Column(db.Integer, nullable=False, index=True)
    topic = db.Column(db.String(120), nullable=False, index=True)
    question_type = db.Column(db.String(30), default='mcq', nullable=False) # 'mcq', 'short_answer', 'long_answer', 'coding', 'numerical'
    difficulty = db.Column(db.String(20), default='Medium', nullable=False) # 'Easy', 'Medium', 'Hard'
    marks = db.Column(db.Integer, default=1, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=True)
    option_b = db.Column(db.Text, nullable=True)
    option_c = db.Column(db.Text, nullable=True)
    option_d = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.Text, nullable=False) # 'A', 'B', 'C', 'D' for MCQ, or model answer
    explanation = db.Column(db.Text, nullable=False)
    suggested_answer_structure = db.Column(db.Text, nullable=True) # breakdown / rubric
    is_repeated_concept = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'subject': self.subject,
            'course': self.course,
            'exam_board': self.exam_board,
            'exam_year': self.exam_year,
            'topic': self.topic,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'marks': self.marks,
            'question_text': self.question_text,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            } if self.question_type == 'mcq' else None,
            'is_repeated_concept': self.is_repeated_concept,
            'is_verified': self.is_verified
        }
