import pytest
from models import db, User, MentorConversation, MentorMessage, Bookmark

def test_practice_hub_view(auth_client):
    res = auth_client.get('/practice')
    assert res.status_code == 200
    assert b"Smart Practice Hub" in res.data
    assert b"Algorithmic Coding Challenges" in res.data

def test_bookmarks_view(auth_client, app):
    with app.app_context():
        bm = Bookmark(
            user_id=1,
            item_type='resource',
            item_id=1,
            title='Sample Bookmarked Topic',
            subtitle='Computer Science',
            target_url='/resources/data-structures-linked-lists'
        )
        db.session.add(bm)
        db.session.commit()
        bm_id = bm.id

    res = auth_client.get('/bookmarks')
    assert res.status_code == 200
    assert b"Saved Topics, Notes" in res.data
    assert b"Sample Bookmarked Topic" in res.data

    # Delete bookmark API
    del_res = auth_client.post(f'/api/bookmarks/{bm_id}/delete')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True

def test_settings_and_theme_persistence(auth_client, app):
    # View settings
    res = auth_client.get('/settings')
    assert res.status_code == 200
    assert b"Platform Preferences" in res.data

    # Update theme to dark
    update_res = auth_client.post('/settings/update', data={
        'theme_preference': 'dark',
        'skill_level': 'advanced',
        'study_goals': 'Top 100 in GATE CS'
    }, follow_redirects=True)
    assert update_res.status_code == 200
    assert b"Settings saved successfully" in update_res.data

    with app.app_context():
        user = User.query.get(1)
        assert user.theme_preference == 'dark'
        assert user.skill_level == 'advanced'
        assert user.study_goals == 'Top 100 in GATE CS'

    # Check that base.html now renders data-bs-theme="dark"
    dash_res = auth_client.get('/dashboard')
    assert b'data-bs-theme="dark"' in dash_res.data

def test_mentor_conversational_threads(auth_client, app):
    # View mentor
    res = auth_client.get('/mentor')
    assert res.status_code == 200
    assert b"Ask Anything AI Study Mentor" in res.data

    # Create new conversation via API
    new_res = auth_client.post('/api/mentor/new')
    assert new_res.status_code == 200
    data = new_res.get_json()
    conv_id = data['conversation_id']
    assert conv_id is not None

    # Chat in this conversation
    chat_res = auth_client.post('/api/mentor/chat', json={
        'message': 'Explain binary search trees and insertion time complexity',
        'level': 'intermediate',
        'conversation_id': conv_id
    })
    assert chat_res.status_code == 200
    chat_data = chat_res.get_json()
    assert 'response' in chat_data
    assert len(chat_data['response']) > 20

    # Clear chat
    clear_res = auth_client.post(f'/api/mentor/clear/{conv_id}')
    assert clear_res.status_code == 200
    assert clear_res.get_json()['success'] is True
