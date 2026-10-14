from datetime import datetime, timezone
from . import db

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    item_type = db.Column(db.String(30), nullable=False, index=True) # 'resource', 'question', 'pyq', 'note'
    item_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), default='General', nullable=False)
    url = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_type', 'item_id', name='uq_user_bookmark'),
    )

    def __init__(self, **kwargs):
        if 'subtitle' in kwargs and 'subject' not in kwargs:
            kwargs['subject'] = kwargs.pop('subtitle')
        if 'target_url' in kwargs and 'url' not in kwargs:
            kwargs['url'] = kwargs.pop('target_url')
        super().__init__(**kwargs)

    @property
    def subtitle(self):
        return self.subject

    @subtitle.setter
    def subtitle(self, val):
        self.subject = val

    @property
    def target_url(self):
        return self.url

    @target_url.setter
    def target_url(self, val):
        self.url = val

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'title': self.title,
            'subject': self.subject,
            'url': self.url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }
