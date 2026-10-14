import json
from datetime import datetime, timezone, date
from . import db

class StudyPlan(db.Model):
    __tablename__ = 'study_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    goal_title = db.Column(db.String(150), nullable=False) # e.g. "Semester Exam Prep" or "SSC CGL 60-Day Drill"
    target_exam_or_goal = db.Column(db.String(100), nullable=False)
    current_knowledge_level = db.Column(db.String(30), default='Beginner', nullable=False) # 'Beginner', 'Intermediate', 'Advanced'
    daily_hours_available = db.Column(db.Float, default=2.0, nullable=False) # realistic hours per day
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    target_completion_date = db.Column(db.Date, nullable=False)
    preferred_learning_style = db.Column(db.String(50), default='balanced', nullable=False) # 'theory_first', 'practice_heavy', 'balanced'
    subjects_to_cover_json = db.Column(db.Text, nullable=False) # JSON list of subjects
    weak_topics_priority_json = db.Column(db.Text, nullable=True) # JSON list of weak topics
    status = db.Column(db.String(20), default='active', nullable=False) # 'active', 'completed', 'archived'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, **kwargs):
        if 'title' in kwargs and 'goal_title' not in kwargs:
            kwargs['goal_title'] = kwargs.pop('title')
        if 'daily_available_hours' in kwargs and 'daily_hours_available' not in kwargs:
            kwargs['daily_hours_available'] = kwargs.pop('daily_available_hours')
        if 'target_completion_date' not in kwargs:
            from datetime import timedelta
            kwargs['target_completion_date'] = date.today() + timedelta(days=30)
        if 'target_exam_or_goal' not in kwargs:
            kwargs['target_exam_or_goal'] = 'General Study'
        if 'subjects_to_cover_json' not in kwargs:
            kwargs['subjects_to_cover_json'] = json.dumps(['Python Programming'])
        super().__init__(**kwargs)

    @property
    def title(self):
        return self.goal_title

    @title.setter
    def title(self, val):
        self.goal_title = val

    @property
    def daily_available_hours(self):
        return self.daily_hours_available

    @daily_available_hours.setter
    def daily_available_hours(self, val):
        self.daily_hours_available = val

    # Relationships
    tasks = db.relationship('StudyTask', backref='plan', lazy='dynamic', cascade='all, delete-orphan')

    def get_subjects(self):
        try:
            return json.loads(self.subjects_to_cover_json) if self.subjects_to_cover_json else []
        except Exception:
            return []

    def get_weak_topics(self):
        try:
            return json.loads(self.weak_topics_priority_json) if self.weak_topics_priority_json else []
        except Exception:
            return []

    def get_progress_percentage(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter_by(is_completed=True).count()
        return round((completed / total) * 100, 1)


class StudyTask(db.Model):
    __tablename__ = 'study_tasks'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    day_number = db.Column(db.Integer, default=1, nullable=False) # Day 1, 2, ...
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), default='General', server_default='General', nullable=False)
    topic = db.Column(db.String(120), default='General', server_default='General', nullable=False)
    task_type = db.Column(db.String(30), default='study', nullable=False) # 'study', 'practice', 'revision', 'mock_test', 'break'
    duration_minutes = db.Column(db.Integer, default=45, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, **kwargs):
        if 'topic' not in kwargs:
            kwargs['topic'] = 'General'
        if 'subject' not in kwargs:
            kwargs['subject'] = 'General'
        super().__init__(**kwargs)

    @property
    def is_overdue(self):
        if self.is_completed:
            return False
        return self.scheduled_date < date.today()
