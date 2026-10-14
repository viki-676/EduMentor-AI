import pytest
from models import db, Note, Bookmark
from services.note_service import (
    create_note, update_note, delete_note,
    get_user_notes, toggle_note_bookmark, export_note_as_markdown
)

def test_note_crud_lifecycle(app):
    with app.app_context():
        user_id = 1
        # Create
        note, err = create_note(
            user_id=user_id,
            title="Dijkstra's Algorithm Notes",
            content="Greedy approach with min-heap priority queue. Time complexity O((V+E)logV).",
            subject="Data Structures",
            topic="Graphs",
            tags="graphs, algorithms, shortest-path"
        )
        assert err is None
        assert note is not None
        assert note.id is not None
        assert "graphs" in note.tags_list

        # Read & Search
        notes = get_user_notes(user_id, search_query="Dijkstra")
        assert len(notes) == 1
        assert notes[0].title == "Dijkstra's Algorithm Notes"

        # Filter by tag
        tagged_notes = get_user_notes(user_id, tag="shortest-path")
        assert len(tagged_notes) == 1

        # Update
        updated, err = update_note(
            user_id=user_id,
            note_id=note.id,
            title="Dijkstra's Shortest Path",
            content="Updated content with Fibonacci Heap O(E + V log V).",
            tags="graphs, advanced"
        )
        assert err is None
        assert updated.title == "Dijkstra's Shortest Path"

        # Toggle bookmark
        bookmarked, _ = toggle_note_bookmark(user_id, note.id)
        assert bookmarked is True
        bm = Bookmark.query.filter_by(user_id=user_id, item_type="note", item_id=note.id).first()
        assert bm is not None

        # Export
        md_text = export_note_as_markdown(note)
        assert "# Dijkstra's Shortest Path" in md_text
        assert "Fibonacci Heap" in md_text

        # Delete
        ok, _ = delete_note(user_id, note.id)
        assert ok is True
        assert db.session.get(Note, note.id) is None

def test_note_routes_authenticated(auth_client, app):
    # View notebook
    res = auth_client.get('/notes')
    assert res.status_code == 200
    assert b"Personal Study Notebook" in res.data or b"Notes" in res.data

    # Create note via form
    create_res = auth_client.post('/notes/create', data={
        'title': 'Operating System Semaphores',
        'subject': 'Operating Systems',
        'topic': 'Synchronization',
        'tags': 'os, concurrency',
        'content': 'Wait (P) decrements mutex; Signal (V) increments mutex.'
    }, follow_redirects=True)
    assert create_res.status_code == 200
    assert b"Operating System Semaphores" in create_res.data

    # Quick save API
    qs_res = auth_client.post('/api/notes/quick-save', data={
        'title': 'AI Mentor Quick Note',
        'subject': 'Machine Learning',
        'content': 'Gradient descent steps.'
    }, follow_redirects=True)
    assert qs_res.status_code == 200

def test_notes_mobile_responsive_elements(auth_client, app):
    # Test empty state mobile classes
    res = auth_client.get('/notes')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Mobile-friendly Create Note button with full width on small screens
    assert 'w-100 w-md-auto' in html
    # Mobile stacked form columns without overflow
    assert 'col-12 col-md-5' in html
    assert 'col-12 col-sm-6 col-md-3' in html
    assert 'col-12 col-sm-6 col-md-2' in html
    assert 'col-12 col-md-2' in html

    # Create a note and test populated note card mobile responsiveness
    create_res = auth_client.post('/notes/create', data={
        'title': 'Responsive Test Note',
        'content': 'Checking mobile alignment and styling.',
        'subject': 'Web Development'
    }, follow_redirects=True)
    assert create_res.status_code == 200

    res2 = auth_client.get('/notes')
    html2 = res2.data.decode('utf-8')
    assert 'note-action-btn' in html2
    assert 'text-break' in html2
    assert 'col-12 col-md-6 col-xl-4' in html2
