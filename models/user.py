from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    
    # Learning preferences & academic profile
    learning_path = db.Column(db.String(30), default='college', nullable=False)  # 'college' | 'competitive'
    degree_or_stream = db.Column(db.String(80), nullable=True)                  # e.g., 'B.Tech', 'BCA'
    semester = db.Column(db.String(30), nullable=True)                          # e.g., 'Semester 4'
    skill_level = db.Column(db.String(30), default='Beginner', nullable=False)  # 'Beginner', 'Intermediate', 'Advanced'
    study_goals = db.Column(db.Text, nullable=True)                             # e.g. 'Master DSA and crack campus placement'
    preferred_subjects = db.Column(db.Text, nullable=True)                      # e.g. 'Python, DSA, DBMS'
    target_exam = db.Column(db.String(50), nullable=True)                       # e.g., 'SSC', 'Banking', 'GATE'
    theme_preference = db.Column(db.String(20), default='light', nullable=False) # 'light' | 'dark'
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    attempts = db.relationship('QuizAttempt', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    study_plans = db.relationship('StudyPlan', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    mentor_conversations = db.relationship('MentorConversation', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    resource_progress = db.relationship('ResourceProgress', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        """Hash and save the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'learning_path': self.learning_path,
            'degree_or_stream': self.degree_or_stream,
            'semester': self.semester,
            'skill_level': self.skill_level,
            'study_goals': self.study_goals,
            'preferred_subjects': self.preferred_subjects,
            'target_exam': self.target_exam,
            'theme_preference': self.theme_preference,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self) -> str:
        return f'<User {self.username}>'
