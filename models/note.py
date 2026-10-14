from datetime import datetime, timezone
from . import db

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), default='General', nullable=False)
    topic = db.Column(db.String(120), default='General', nullable=False)
    tags = db.Column(db.String(200), default='', nullable=True) # e.g. "python, dsa, tips"
    source = db.Column(db.String(50), default='manual', nullable=False) # 'manual', 'ai_mentor', 'resource'
    is_bookmarked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def get_tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def tags_list(self):
        return self.get_tag_list()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'subject': self.subject,
            'topic': self.topic,
            'tags': self.get_tag_list(),
            'source': self.source,
            'is_bookmarked': self.is_bookmarked,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }
