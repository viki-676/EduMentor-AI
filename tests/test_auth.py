from models import User, db

def test_user_registration_success(client, app):
    response = client.post('/register', data={
        'full_name': 'Ananya Sen',
        'username': 'ananya',
        'email': 'ananya@example.com',
        'password': 'securepassword',
        'learning_path': 'college',
        'degree_or_stream': 'BCA'
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='ananya').first()
        assert user is not None
        assert user.full_name == 'Ananya Sen'
        assert user.password_hash != 'securepassword'
        assert user.check_password('securepassword') is True

def test_user_registration_duplicate_username(client):
    client.post('/register', data={
        'full_name': 'First User',
        'username': 'firstuser',
        'email': 'first@example.com',
        'password': 'password123',
        'learning_path': 'college'
    })

    # Log out so session is clear for registration form
    client.get('/logout')

    # Attempt duplicate username
    response = client.post('/register', data={
        'full_name': 'Duplicate User',
        'username': 'firstuser',
        'email': 'second@example.com',
        'password': 'password123',
        'learning_path': 'college'
    }, follow_redirects=True)

    assert b"is already registered" in response.data

def test_user_registration_short_password(client):
    response = client.post('/register', data={
        'full_name': 'Short Pass',
        'username': 'shortpass',
        'email': 'short@example.com',
        'password': '123',
        'learning_path': 'college'
    }, follow_redirects=True)

    assert b"Password must be at least 6 characters" in response.data

def test_login_and_logout(client, app):
    with app.app_context():
        u = User(username='loginuser', email='login@example.com', full_name='Login User')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()

    # Successful login
    login_res = client.post('/login', data={
        'username_or_email': 'loginuser',
        'password': 'mypassword'
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Welcome back" in login_res.data

    # Logout
    logout_res = client.get('/logout', follow_redirects=True)
    assert b"logged out" in logout_res.data

def test_unauthenticated_protected_route_redirect(client):
    # Trying to access dashboard without session
    res = client.get('/dashboard', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.location
