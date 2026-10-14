from datetime import datetime, timezone
from . import db

class MentorConversation(db.Model):
    __tablename__ = 'mentor_conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(180), default='New Study Chat', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    messages = db.relationship('MentorMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan', order_by='MentorMessage.created_at.asc()')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message_count': self.messages.count(),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }


class MentorMessage(db.Model):
    __tablename__ = 'mentor_messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('mentor_conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    sender = db.Column(db.String(20), nullable=False) # 'user' or 'mentor'
    message_text = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default='beginner', nullable=False) # 'beginner', 'intermediate', 'advanced'
    subject_detected = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def content(self):
        return self.message_text

    @content.setter
    def content(self, val):
        self.message_text = val

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'message_text': self.message_text,
            'content': self.message_text,
            'level': self.level,
            'subject_detected': self.subject_detected,
            'created_at': self.created_at.strftime('%H:%M')
        }
