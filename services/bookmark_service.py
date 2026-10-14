"""
Unified Bookmarks service for managing saved items across resources, questions, notes, and PYQs.
"""

from models import db, Bookmark

def get_user_bookmarks(user_id, item_type=None):
    """Retrieve all bookmarked items for the student."""
    query = Bookmark.query.filter_by(user_id=user_id)
    if item_type and item_type != 'all':
        query = query.filter_by(item_type=item_type)
    return query.order_by(Bookmark.created_at.desc()).all()

def add_bookmark(user_id, item_type, item_id, title, subject='General', url=''):
    """Add or get bookmark for user."""
    bm = Bookmark.query.filter_by(user_id=user_id, item_type=item_type, item_id=item_id).first()
    if not bm:
        bm = Bookmark(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id,
            title=title.strip() if title else 'Untitled',
            subject=subject.strip() if subject else 'General',
            url=url
        )
        db.session.add(bm)
        db.session.commit()
    return bm

def remove_bookmark(user_id, bookmark_id):
    """Remove a specific bookmark by ID."""
    bm = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if bm:
        db.session.delete(bm)
        db.session.commit()
        return True
    return False
