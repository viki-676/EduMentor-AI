import os
os.environ['AI_PROVIDER'] = 'offline'
import pytest
from app import create_app
from models import db, User
from data.seed_questions import seed_question_bank

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        seed_question_bank(db)
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Client logged in as a registered student."""
    with app.app_context():
        user = User(
            username='teststudent',
            email='student@example.com',
            full_name='Test Student',
            learning_path='college',
            degree_or_stream='B.Tech Computer Science'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Log in
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['username'] = 'teststudent'

    return client
