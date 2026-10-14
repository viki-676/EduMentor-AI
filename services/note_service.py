"""
Notes management service for personal note-taking, search, tags, and export.
"""

from datetime import datetime, timezone
from models import db, Note, Bookmark

def get_user_notes(user_id, search=None, tag=None, subject=None, search_query=None):
    """Fetch user notes with search and filtering."""
    search = search or search_query
    query = Note.query.filter_by(user_id=user_id)

    if subject and subject != 'All':
        query = query.filter_by(subject=subject)

    if tag and tag.strip():
        term = f"%{tag.strip()}%"
        query = query.filter(Note.tags.ilike(term))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Note.title.ilike(term)) |
            (Note.content.ilike(term)) |
            (Note.topic.ilike(term)) |
            (Note.tags.ilike(term))
        )

    notes = query.order_by(Note.is_bookmarked.desc(), Note.updated_at.desc()).all()
    return notes

def get_note_by_id(user_id, note_id):
    return Note.query.filter_by(id=note_id, user_id=user_id).first()

def create_note(user_id, title, content, subject='General', topic='General', tags='', source='manual'):
    title = (title or '').strip()
    content = (content or '').strip()

    if not title:
        return None, "Note title is required."
    if not content:
        return None, "Note content cannot be empty."

    note = Note(
        user_id=user_id,
        title=title,
        content=content,
        subject=(subject or 'General').strip(),
        topic=(topic or 'General').strip(),
        tags=(tags or '').strip(),
        source=source
    )
    db.session.add(note)
    db.session.commit()
    return note, None

def update_note(user_id, note_id, title, content, subject='General', topic='General', tags=''):
    note = get_note_by_id(user_id, note_id)
    if not note:
        return None, "Note not found or unauthorized."

    title = (title or '').strip()
    content = (content or '').strip()

    if not title:
        return None, "Note title cannot be empty."
    if not content:
        return None, "Note content cannot be empty."

    note.title = title
    note.content = content
    note.subject = (subject or 'General').strip()
    note.topic = (topic or 'General').strip()
    note.tags = (tags or '').strip()
    note.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return note, None

def delete_note(user_id, note_id):
    note = get_note_by_id(user_id, note_id)
    if not note:
        return False, "Note not found."

    Bookmark.query.filter_by(user_id=user_id, item_type='note', item_id=note_id).delete()
    db.session.delete(note)
    db.session.commit()
    return True, None

def toggle_note_bookmark(user_id, note_id):
    note = get_note_by_id(user_id, note_id)
    if not note:
        return False, "Note not found."

    note.is_bookmarked = not note.is_bookmarked
    if note.is_bookmarked:
        bm = Bookmark.query.filter_by(user_id=user_id, item_type='note', item_id=note_id).first()
        if not bm:
            bm = Bookmark(
                user_id=user_id,
                item_type='note',
                item_id=note_id,
                title=note.title,
                subject=note.subject,
                url=f"/notes?id={note.id}"
            )
            db.session.add(bm)
    else:
        Bookmark.query.filter_by(user_id=user_id, item_type='note', item_id=note_id).delete()

    db.session.commit()
    return note.is_bookmarked, None

def export_note_as_markdown(note):
    """Formats note as downloadable Markdown document."""
    lines = [
        f"# {note.title}",
        f"**Subject:** {note.subject or 'General'} | **Topic:** {note.topic or 'General'}",
        f"**Tags:** {note.tags or 'None'}",
        f"**Last Updated:** {note.updated_at.strftime('%Y-%m-%d %H:%M')}",
        "\n---\n",
        note.content or ""
    ]
    return "\n\n".join(lines)

