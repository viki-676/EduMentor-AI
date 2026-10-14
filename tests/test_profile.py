from models import User, db

def test_profile_view_requires_login(client):
    """Unauthenticated users must be redirected to login page."""
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_profile_view_authenticated(auth_client):
    """Authenticated student can view their personal profile and statistics."""
    response = auth_client.get('/profile')
    assert response.status_code == 200
    assert b"Student Profile" in response.data
    assert b"Edit Profile Information" in response.data
    assert b"Test Student" in response.data
    assert b"student@example.com" in response.data


def test_profile_update_success(auth_client, app):
    """Updating profile details updates DB record and redirects with success message."""
    response = auth_client.post('/profile/update', data={
        'full_name': 'Test Student Updated',
        'email': 'student_new@example.com',
        'learning_path': 'competitive',
        'degree_or_stream': 'BCA Honors',
        'target_exam': 'Banking'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Profile details updated successfully!" in response.data
    assert b"Test Student Updated" in response.data

    with app.app_context():
        user = User.query.filter_by(username='teststudent').first()
        assert user.full_name == 'Test Student Updated'
        assert user.email == 'student_new@example.com'
        assert user.learning_path == 'competitive'
        assert user.target_exam == 'Banking'

def test_profile_update_empty_name_fails(auth_client):
    """Updating with blank full name returns validation error."""
    response = auth_client.post('/profile/update', data={
        'full_name': '   ',
        'email': 'student@example.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Full name cannot be empty." in response.data

def test_profile_update_duplicate_email_fails(auth_client, app):
    """Updating email to one already registered by another student is rejected."""
    with app.app_context():
        other = User(username='otheruser', email='other@example.com', full_name='Other Person')
        other.set_password('pass123')
        db.session.add(other)
        db.session.commit()

    response = auth_client.post('/profile/update', data={
        'full_name': 'Test Student',
        'email': 'other@example.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already associated with another account" in response.data

def test_profile_change_password_success(auth_client, app):
    """Changing password with valid credentials succeeds."""
    response = auth_client.post('/profile/change-password', data={
        'current_password': 'password123',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your password has been changed successfully!" in response.data

    with app.app_context():
        user = User.query.filter_by(username='teststudent').first()
        assert user.check_password('newpassword456') is True
        assert user.check_password('password123') is False

def test_profile_change_password_wrong_current(auth_client):
    """Submitting incorrect current password is rejected."""
    response = auth_client.post('/profile/change-password', data={
        'current_password': 'wrongpassword',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Current password is incorrect." in response.data

def test_profile_change_password_mismatched_confirm(auth_client):
    """Mismatched new passwords are rejected."""
    response = auth_client.post('/profile/change-password', data={
        'current_password': 'password123',
        'new_password': 'newpassword456',
        'confirm_password': 'differentpassword789'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"New passwords do not match." in response.data

def test_profile_change_password_too_short(auth_client):
    """Passwords shorter than 6 characters are rejected."""
    response = auth_client.post('/profile/change-password', data={
        'current_password': 'password123',
        'new_password': '123',
        'confirm_password': '123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"New password must be at least 6 characters long." in response.data
