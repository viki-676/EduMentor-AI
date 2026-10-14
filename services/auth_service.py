from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from models import db, User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or (request.path and request.path.startswith('/api/')):
                return jsonify({'error': 'Authentication required. Please log in.', 'response': 'Please log in to chat with AI Mentor.'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retrieve the currently logged-in user or None."""
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None

def register_user(username, email, password, full_name, learning_path='college', degree_or_stream=None, target_exam=None):
    """
    Validate and register a new student.
    Returns (user, error_message).
    """
    username = (username or '').strip()
    email = (email or '').strip().lower()
    password = password or ''
    full_name = (full_name or '').strip()

    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters long."

    if not email or '@' not in email or '.' not in email:
        return None, "Please provide a valid email address."

    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters long."

    if not full_name:
        return None, "Please enter your full name."

    # Check uniqueness
    if User.query.filter_by(username=username).first():
        return None, f"Username '{username}' is already registered."

    if User.query.filter_by(email=email).first():
        return None, f"Email '{email}' is already registered."

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        learning_path=learning_path or 'college',
        degree_or_stream=degree_or_stream,
        target_exam=target_exam
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    return new_user, None

def authenticate_user(username_or_email, password):
    """
    Authenticate student with username or email.
    Returns (user, error_message).
    """
    identifier = (username_or_email or '').strip()
    password = password or ''

    if not identifier or not password:
        return None, "Please fill in all credentials."

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return None, "Invalid username/email or password."

    return user, None


def update_user_profile(user_id, full_name, email, degree_or_stream=None, target_exam=None, learning_path=None, semester=None, skill_level=None, study_goals=None, preferred_subjects=None, theme_preference=None):
    """
    Update student profile details with validation.
    Returns (user, error_message).
    """
    user = db.session.get(User, user_id)
    if not user:
        return None, "User not found."

    full_name = (full_name or '').strip()
    email = (email or '').strip().lower()

    if not full_name:
        return None, "Full name cannot be empty."

    if not email or '@' not in email or '.' not in email:
        return None, "Please provide a valid email address."

    # Verify email uniqueness across other users
    existing_email = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_email:
        return None, f"Email '{email}' is already associated with another account."

    user.full_name = full_name
    user.email = email
    if degree_or_stream is not None:
        user.degree_or_stream = degree_or_stream
    if target_exam is not None:
        user.target_exam = target_exam
    if learning_path in ('college', 'competitive'):
        user.learning_path = learning_path
    if semester is not None:
        user.semester = semester
    if skill_level is not None:
        user.skill_level = skill_level
    if study_goals is not None:
        user.study_goals = study_goals
    if preferred_subjects is not None:
        user.preferred_subjects = preferred_subjects
    if theme_preference in ('light', 'dark'):
        user.theme_preference = theme_preference

    db.session.commit()
    return user, None



def change_user_password(user_id, current_password, new_password, confirm_password):
    """
    Verify current password and set new password.
    Returns (success_bool, error_message).
    """
    user = db.session.get(User, user_id)
    if not user:
        return False, "User not found."

    if not current_password or not new_password or not confirm_password:
        return False, "All password fields are required."

    if not user.check_password(current_password):
        return False, "Current password is incorrect."

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    if new_password != confirm_password:
        return False, "New passwords do not match."

    if current_password == new_password:
        return False, "New password must be different from current password."

    user.set_password(new_password)
    db.session.commit()
    return True, None


def reset_user_password(username_or_email, new_password):
    """
    Reset user password using verified username or email identifier.
    Returns (success_bool, message).
    """
    identifier = (username_or_email or '').strip()
    new_password = new_password or ''

    if not identifier:
        return False, "Please provide your username or registered email address."

    if not new_password or len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user:
        return False, "No student account found with the provided username or email."

    user.set_password(new_password)
    db.session.commit()
    return True, f"Password successfully updated for @{user.username}. You may now log in with your new credentials."


