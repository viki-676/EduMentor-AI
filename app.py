import os
from dotenv import load_dotenv
load_dotenv()
from datetime import date, datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from config import config_by_name
from models import (
    db, User, Question, QuizAttempt, StudentAnswer, Recommendation,
    LearningResource, ResourceProgress, Note, StudyPlan, StudyTask,
    PYQPaper, PreviousYearQuestion, Bookmark, MentorConversation, MentorMessage
)
from models.learning import COLLEGE_SUBJECTS, COMPETITIVE_EXAMS, COMPETITIVE_CATEGORIES
from data.seed_questions import seed_question_bank
from data.seed_resources import seed_learning_resources
from data.seed_notes import seed_sample_notes_for_user
from data.seed_pyqs import seed_pyq_papers
from services.auth_service import (
    login_required, get_current_user, register_user, authenticate_user,
    update_user_profile, change_user_password, reset_user_password
)
from services.quiz_service import (
    get_quiz_questions, submit_quiz_attempt, get_user_analytics,
    count_eligible_questions
)
from services.recommendation import generate_personalized_recommendations
from services.ai_mentor import get_mentor_response
from services.llm_provider import get_active_provider, get_provider_status
from services.resource_service import (
    get_resources, get_resource_by_slug, get_resource_categories, get_learning_sections,
    toggle_resource_progress, normalize_category
)
from services.note_service import (
    get_user_notes, get_note_by_id, create_note, update_note, delete_note, toggle_note_bookmark
)
from services.planner_service import (
    generate_study_plan, get_active_plan, get_today_tasks, toggle_task,
    reschedule_overdue, create_task, delete_task
)
from services.pyq_service import (
    get_pyq_papers, get_paper_details, get_pyq_filters, search_pyq_questions,
    evaluate_pyq_practice, extract_text_from_pdf, parse_and_create_pyq_paper
)
from services.bookmark_service import get_user_bookmarks, add_bookmark, remove_bookmark
from ml.performance_predictor import StudentRiskPredictor
from sqlalchemy import text


def calculate_user_streak(user_id):
    """Accurately calculates consecutive active days (quizzes or completed tasks)."""
    attempt_dates = set(
        row[0].date() for row in db.session.query(QuizAttempt.created_at).filter_by(user_id=user_id).all()
    )
    task_dates = set(
        row[0] for row in db.session.query(StudyTask.scheduled_date).filter_by(user_id=user_id, is_completed=True).all()
    )
    all_dates = attempt_dates.union(task_dates)
    if not all_dates:
        return 0

    today = date.today()
    streak = 0
    curr = today
    if curr not in all_dates:
        curr = today - timedelta(days=1)

    while curr in all_dates:
        streak += 1
        curr -= timedelta(days=1)
    return streak


def resolve_config_name(config_name=None):
    """
    Safely resolve environment configuration name.
    Checks explicit parameter, FLASK_CONFIG, FLASK_ENV, ENVIRONMENT, ENV,
    RENDER cloud environment flag, and FLASK_DEBUG setting.
    Ensures production mode disables Flask debug mode even if FLASK_ENV is not set.
    """
    if config_name and config_name != 'default':
        return config_name

    env_val = (
        os.environ.get('FLASK_CONFIG') or
        os.environ.get('FLASK_ENV') or
        os.environ.get('ENVIRONMENT') or
        os.environ.get('ENV') or
        ''
    ).lower().strip()

    if env_val in ('production', 'prod'):
        return 'production'
    elif env_val in ('testing', 'test'):
        return 'testing'
    elif env_val in ('development', 'dev'):
        return 'development'

    # Auto-detect Render hosting environment (RENDER=true is automatically set by Render)
    if os.environ.get('RENDER') == 'true' or os.environ.get('RENDER_SERVICE_ID'):
        return 'production'

    # If FLASK_DEBUG is explicitly turned off (0, false, no), treat as production
    flask_debug = os.environ.get('FLASK_DEBUG', '').lower().strip()
    if flask_debug in ('0', 'false', 'no'):
        return 'production'

    return 'development'


def create_app(config_name='default'):
    target_config = resolve_config_name(config_name)
    app = Flask(__name__)
    config_cls = config_by_name.get(
        target_config,
        config_by_name['production' if 'prod' in target_config else 'development']
    )
    app.config.from_object(config_cls)

    # Production safety enforcement: explicitly ensure DEBUG and TESTING are disabled in production
    flask_debug = os.environ.get('FLASK_DEBUG', '').lower().strip()
    if target_config in ('production', 'prod') or flask_debug in ('0', 'false', 'no'):
        app.config['DEBUG'] = False
        app.debug = False
        app.config['TESTING'] = False

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)

    # Initialize predictor with optional app configuration (default: 0.50)
    risk_threshold = app.config.get('RISK_DECISION_THRESHOLD', None)
    predictor = StudentRiskPredictor(decision_threshold=risk_threshold)

    with app.app_context():
        db.create_all()

        # Database schema migrations for existing SQLite databases
        try:
            with db.engine.connect() as conn:
                user_cols = [col[1] for col in conn.execute(text("PRAGMA table_info(users);")).fetchall()]
                if 'semester' not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN semester VARCHAR(30);"))
                if 'skill_level' not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN skill_level VARCHAR(30) DEFAULT 'Beginner';"))
                if 'study_goals' not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN study_goals TEXT;"))
                if 'preferred_subjects' not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN preferred_subjects TEXT;"))
                if 'theme_preference' not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN theme_preference VARCHAR(20) DEFAULT 'light';"))

                quiz_cols = [col[1] for col in conn.execute(text("PRAGMA table_info(quiz_attempts);")).fetchall()]
                if 'time_limit_minutes' not in quiz_cols:
                    conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN time_limit_minutes INTEGER DEFAULT 0;"))
                if 'status' not in quiz_cols:
                    conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN status VARCHAR(20) DEFAULT 'completed';"))

                conn.commit()
        except Exception as e:
            app.logger.warning(f"Schema compatibility notice: {e}")

        # Seed core knowledge bases & question catalogs
        seed_question_bank(db)
        seed_learning_resources(db)
        seed_pyq_papers(db)

    # Context processor to inject user, navigation counts, and catalogs
    @app.context_processor
    def inject_global_data():
        current_user = get_current_user()
        provider_name, provider_key = get_active_provider()

        today_tasks_count = 0
        bookmarks_count = 0
        active_plan_info = None

        if current_user:
            today_tasks_count = StudyTask.query.filter_by(
                user_id=current_user.id,
                scheduled_date=date.today(),
                is_completed=False
            ).count()
            bookmarks_count = Bookmark.query.filter_by(user_id=current_user.id).count()
            active_plan_info = StudyPlan.query.filter_by(user_id=current_user.id, status='active').first()

        return {
            'current_user': current_user,
            'college_subjects': COLLEGE_SUBJECTS,
            'competitive_exams': COMPETITIVE_EXAMS,
            'competitive_categories': COMPETITIVE_CATEGORIES,
            'today_tasks_count': today_tasks_count,
            'bookmarks_count': bookmarks_count,
            'active_plan': active_plan_info,
            'ai_provider': provider_name,
            'has_live_llm': bool(provider_key)
        }

    # =========================================================================
    # CORE ROUTES: LANDING & AUTH
    # =========================================================================

    @app.route('/')
    def index():
        current_user = get_current_user()
        total_questions = Question.query.count()
        total_resources = LearningResource.query.count()
        total_pyqs = PreviousYearQuestion.query.count()
        college_questions = Question.query.filter_by(learning_path='college').count()
        competitive_questions = Question.query.filter_by(learning_path='competitive').count()

        # Dynamic counts per subject/category
        subject_counts = {
            'Python Programming': Question.query.filter_by(learning_path='college', subject_or_category='Python Programming').count(),
            'Data Structures': Question.query.filter_by(learning_path='college', subject_or_category='Data Structures').count(),
            'DBMS': Question.query.filter(
                Question.learning_path == 'college',
                Question.subject_or_category.in_(['Database Management Systems (DBMS)', 'DBMS'])
            ).count(),
            'Quantitative Aptitude': Question.query.filter_by(learning_path='competitive', subject_or_category='Quantitative Aptitude').count(),
            'Logical Reasoning': Question.query.filter_by(learning_path='competitive', subject_or_category='Logical Reasoning').count(),
            'English Language': Question.query.filter_by(learning_path='competitive', subject_or_category='English Language').count(),
            'General Awareness': Question.query.filter_by(learning_path='competitive', subject_or_category='General Awareness').count(),
        }

        return render_template(
            'index.html',
            current_user=current_user,
            total_questions=total_questions,
            total_resources=total_resources,
            total_pyqs=total_pyqs,
            college_questions=college_questions,
            competitive_questions=competitive_questions,
            subject_counts=subject_counts
        )

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            full_name = request.form.get('full_name')
            learning_path = request.form.get('learning_path', 'college')
            degree_or_stream = request.form.get('degree_or_stream')
            target_exam = request.form.get('target_exam')

            if confirm_password and password != confirm_password:
                flash("Passwords do not match. Please ensure both passwords match.", 'danger')
                return render_template('auth/register.html', form=request.form)

            user, error = register_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                learning_path=learning_path,
                degree_or_stream=degree_or_stream,
                target_exam=target_exam
            )

            if error:
                flash(error, 'danger')
                return render_template('auth/register.html', form=request.form)

            # Pre-seed starter notes for the new student
            seed_sample_notes_for_user(db, user.id)

            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome to EduMentor AI, {user.full_name}! Your account has been initialized.", 'success')

            if user.learning_path == 'competitive':
                return redirect(url_for('competitive_path'))
            return redirect(url_for('college_path'))

        return render_template('auth/register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username_or_email = request.form.get('username_or_email')
            password = request.form.get('password')
            remember = request.form.get('remember')

            user, error = authenticate_user(username_or_email, password)
            if error:
                flash(error, 'danger')
                return render_template('auth/login.html', username_or_email=username_or_email)

            if remember in ('on', 'true', '1'):
                session.permanent = True

            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.full_name}!", 'success')

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            return redirect(url_for('dashboard'))

        return render_template('auth/login.html')

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            identifier = request.form.get('username_or_email')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password and confirm_password and new_password != confirm_password:
                flash("Passwords do not match. Please re-enter identical passwords.", 'danger')
                return render_template('auth/forgot_password.html', username_or_email=identifier)

            success, msg = reset_user_password(identifier, new_password)
            if success:
                flash(msg, 'success')
                return redirect(url_for('login'))
            else:
                flash(msg, 'danger')
                return render_template('auth/forgot_password.html', username_or_email=identifier)

        return render_template('auth/forgot_password.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash("You have been successfully logged out.", 'info')
        return redirect(url_for('index'))

    # =========================================================================
    # LEARNING PATHS (PRESERVED)
    # =========================================================================

    @app.route('/paths')
    @login_required
    def select_path():
        user = get_current_user()
        return render_template('paths/select_path.html', user=user)

    @app.route('/paths/update', methods=['POST'])
    @login_required
    def update_path():
        user = get_current_user()
        new_path = request.form.get('learning_path', 'college')
        degree = request.form.get('degree_or_stream')
        exam = request.form.get('target_exam')

        user.learning_path = new_path
        if degree:
            user.degree_or_stream = degree
        if exam:
            user.target_exam = exam

        db.session.commit()
        flash(f"Updated path preference to {'College Learning' if new_path == 'college' else 'Competitive Exam Preparation'}.", 'success')

        if new_path == 'competitive':
            return redirect(url_for('competitive_path'))
        return redirect(url_for('college_path'))

    @app.route('/college')
    @login_required
    def college_path():
        user = get_current_user()
        return render_template('paths/college_dashboard.html', user=user)

    @app.route('/competitive')
    @login_required
    def competitive_path():
        user = get_current_user()
        selected_exam = request.args.get('exam', user.target_exam or 'SSC')
        return render_template('paths/competitive_dashboard.html', user=user, selected_exam=selected_exam)

    # =========================================================================
    # STUDENT DASHBOARD
    # =========================================================================

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = get_current_user()
        analytics = get_user_analytics(user.id)
        recs = generate_personalized_recommendations(user.id)

        # Streak calculation
        streak_days = calculate_user_streak(user.id)

        # ML Risk Prediction using real student telemetry
        ml_prediction = None
        if analytics['total_quizzes'] > 0:
            avg_score = analytics['overall_accuracy']
            q_count = analytics['total_quizzes']
            time_per_q = analytics.get('avg_time_per_question', 45.0)
            difficulty = analytics.get('avg_difficulty', 2)
            consistency = max(1, min(10, int(streak_days if streak_days > 0 else 1)))
            ml_prediction = predictor.predict(
                avg_score=avg_score,
                quizzes_count=q_count,
                time_per_q=time_per_q,
                difficulty=difficulty,
                consistency=consistency
            )
        ml_metrics = predictor.metrics

        # Today's Study Planner tasks
        today_tasks = get_today_tasks(user.id)
        active_plan_obj = get_active_plan(user.id)

        # Recommended learning resources based on weak topics
        weak_topics = analytics.get('weak_topics', [])
        recommended_resources = []
        if weak_topics:
            top_weak = weak_topics[0]['topic']
            recommended_resources = LearningResource.query.filter(
                (LearningResource.topic.ilike(f"%{top_weak}%")) |
                (LearningResource.subject.ilike(f"%{top_weak}%"))
            ).limit(3).all()

        if not recommended_resources:
            if user.learning_path == 'competitive':
                recommended_resources = LearningResource.query.filter(
                    (LearningResource.category.ilike('%Mathematics and Aptitude%')) |
                    (LearningResource.subject.ilike('%Quantitative Aptitude%'))
                ).limit(3).all()

            if not recommended_resources:
                recommended_resources = LearningResource.query.order_by(LearningResource.order_index.asc()).limit(3).all()

        # Recent AI Mentor conversations
        recent_chats = MentorConversation.query.filter_by(user_id=user.id).order_by(MentorConversation.updated_at.desc()).limit(3).all()

        # Quick summary stats
        notes_count = Note.query.filter_by(user_id=user.id).count()
        pyqs_count = PreviousYearQuestion.query.count()

        return render_template(
            'dashboard/student_dashboard.html',
            user=user,
            analytics=analytics,
            recommendations=recs,
            ml_prediction=ml_prediction,
            ml_metrics=ml_metrics,
            streak_days=streak_days,
            today_tasks=today_tasks,
            active_plan=active_plan_obj,
            recommended_resources=recommended_resources,
            recent_chats=recent_chats,
            notes_count=notes_count,
            pyqs_count=pyqs_count
        )

    # =========================================================================
    # AI MENTOR (CONVERSATIONAL & MULTI-DISCIPLINARY)
    # =========================================================================

    @app.route('/mentor')
    @login_required
    def mentor_view():
        user = get_current_user()
        analytics = get_user_analytics(user.id)
        conv_id = request.args.get('c', type=int)

        # Get or create active conversation
        active_conv = None
        if conv_id:
            active_conv = MentorConversation.query.filter_by(id=conv_id, user_id=user.id).first()

        if not active_conv:
            active_conv = MentorConversation.query.filter_by(user_id=user.id).order_by(MentorConversation.updated_at.desc()).first()

        conversations = MentorConversation.query.filter_by(user_id=user.id).order_by(MentorConversation.updated_at.desc()).all()
        messages = active_conv.messages.all() if active_conv else []

        provider_status = get_provider_status()

        return render_template(
            'mentor/mentor_view.html',
            user=user,
            analytics=analytics,
            conversations=conversations,
            active_conversation=active_conv,
            messages=messages,
            ai_provider=provider_status.get('status_badge', 'Live AI'),
            is_live_ai=provider_status.get('is_live', False),
            provider_status=provider_status
        )

    @app.route('/api/mentor/status', methods=['GET'])
    @login_required
    def mentor_status():
        return jsonify(get_provider_status())

    @app.route('/api/mentor/chat', methods=['POST'])
    @login_required
    def mentor_chat():
        user = get_current_user()
        data = request.get_json() or {}
        query = data.get('message', '').strip()
        level = data.get('level', 'beginner').lower()
        conv_id = data.get('conversation_id')

        if not query:
            return jsonify({'response': "Please enter a question or topic for AI Mentor."})

        # Generate response (Live LLM or Deep Offline Knowledge Engine)
        response_text = get_mentor_response(
            user_id=user.id,
            query_text=query,
            level=level,
            conversation_id=conv_id
        )

        # Return latest active conversation ID
        latest_conv = MentorConversation.query.filter_by(user_id=user.id).order_by(MentorConversation.updated_at.desc()).first()
        conv_id_res = latest_conv.id if latest_conv else None
        conv_title = latest_conv.title if latest_conv else 'Chat'

        return jsonify({
            'response': response_text,
            'conversation_id': conv_id_res,
            'title': conv_title
        })

    @app.route('/api/mentor/new', methods=['POST'])
    @login_required
    def mentor_new_chat():
        user = get_current_user()
        conv = MentorConversation(user_id=user.id, title='New Study Session')
        db.session.add(conv)
        db.session.commit()
        return jsonify({'conversation_id': conv.id, 'title': conv.title})

    @app.route('/api/mentor/clear/<int:conv_id>', methods=['POST'])
    @login_required
    def mentor_clear_chat(conv_id):
        user = get_current_user()
        conv = MentorConversation.query.filter_by(id=conv_id, user_id=user.id).first()
        if conv:
            MentorMessage.query.filter_by(conversation_id=conv.id).delete()
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Conversation not found'}), 404

    # =========================================================================
    # LEARNING RESOURCES LIBRARY
    # =========================================================================

    @app.route('/resources')
    @login_required
    def resources_catalog():
        user = get_current_user()
        section = (request.args.get('section', '') or request.args.get('path', '')).strip()
        category = normalize_category(request.args.get('category', 'All'))
        difficulty = (request.args.get('difficulty', 'All') or 'All').strip()
        search = (request.args.get('q', '') or '').strip()

        # Synchronize section if track name passed in category
        if category in ['Competitive Exam Preparation', 'Competitive', 'Competitive Prep']:
            section = 'competitive'
        elif category in ['College Semester Learning', 'College Learning', 'College']:
            section = 'college'

        categories = get_resource_categories()
        section_counts = get_learning_sections()
        resources_list = get_resources(
            category=category,
            section=section,
            difficulty=difficulty,
            search=search,
            user_id=user.id
        )

        total_count = len(resources_list)
        completed_count = sum(1 for r in resources_list if r.get('is_completed'))

        return render_template(
            'resources/resource_list.html',
            user=user,
            categories=categories,
            resources=resources_list,
            selected_category=category,
            selected_section=section,
            selected_difficulty=difficulty,
            search_query=search,
            total_count=total_count,
            completed_count=completed_count,
            section_counts=section_counts
        )

    @app.route('/resources/<slug>')
    @login_required
    def resource_detail(slug):
        user = get_current_user()
        resource, prev_res, next_res = get_resource_by_slug(slug, user_id=user.id)
        if not resource:
            flash("Learning resource not found.", 'warning')
            return redirect(url_for('resources_catalog'))

        prog = ResourceProgress.query.filter_by(user_id=user.id, resource_id=resource.id).first()
        is_completed = prog.is_completed if prog else False
        is_bookmarked = prog.is_bookmarked if prog else False

        related_resources = [r for r in [prev_res, next_res] if r]
        return render_template(
            'resources/resource_detail.html',
            user=user,
            resource=resource,
            prev_resource=prev_res,
            next_resource=next_res,
            related_resources=related_resources,
            is_completed=is_completed,
            is_bookmarked=is_bookmarked
        )

    @app.route('/api/resources/<int:resource_id>/toggle', methods=['POST'])
    @login_required
    def resource_toggle_api(resource_id):
        user = get_current_user()
        data = request.get_json() or {}
        field = data.get('field', 'completed')
        new_val = toggle_resource_progress(user.id, resource_id, field)
        return jsonify({'success': True, 'field': field, 'value': new_val})

    # =========================================================================
    # MY NOTES
    # =========================================================================

    @app.route('/notes')
    @login_required
    def notes_view():
        user = get_current_user()
        search = request.args.get('q', '')
        tag = request.args.get('tag', '')
        subject = request.args.get('subject', 'All')

        notes_list = get_user_notes(user.id, search=search, tag=tag, subject=subject)
        all_notes = Note.query.filter_by(user_id=user.id).all()
        subjects = sorted(list({n.subject for n in all_notes if n.subject}))

        # Extract all distinct tags
        all_tags = set()
        for n in all_notes:
            all_tags.update(n.get_tag_list())

        return render_template(
            'notes/notes_list.html',
            user=user,
            notes=notes_list,
            subjects=subjects,
            tags=sorted(list(all_tags)),
            all_tags=sorted(list(all_tags)),
            search_query=search,
            selected_tag=tag,
            selected_subject=subject
        )

    @app.route('/notes/create', methods=['POST'])
    @login_required
    def note_create():
        user = get_current_user()
        title = request.form.get('title')
        content = request.form.get('content')
        subject = request.form.get('subject', 'General')
        topic = request.form.get('topic', 'General')
        tags = request.form.get('tags', '')

        note, error = create_note(
            user_id=user.id,
            title=title,
            content=content,
            subject=subject,
            topic=topic,
            tags=tags,
            source='manual'
        )

        if error:
            flash(error, 'danger')
        else:
            flash("Note created successfully!", 'success')

        return redirect(url_for('notes_view'))

    @app.route('/notes/<int:note_id>/edit', methods=['POST'])
    @login_required
    def note_edit(note_id):
        user = get_current_user()
        title = request.form.get('title')
        content = request.form.get('content')
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        tags = request.form.get('tags')

        note, error = update_note(
            user_id=user.id,
            note_id=note_id,
            title=title,
            content=content,
            subject=subject,
            topic=topic,
            tags=tags
        )

        if error:
            flash(error, 'danger')
        else:
            flash("Note updated successfully!", 'success')

        return redirect(url_for('notes_view'))

    @app.route('/notes/<int:note_id>/delete', methods=['POST'])
    @login_required
    def note_delete(note_id):
        user = get_current_user()
        ok, err = delete_note(user.id, note_id)
        if ok:
            flash("Note deleted successfully.", 'info')
        else:
            flash(err or "Failed to delete note.", 'danger')
        return redirect(url_for('notes_view'))

    @app.route('/notes/<int:note_id>/toggle-bookmark', methods=['POST'])
    @login_required
    def note_toggle_bookmark(note_id):
        user = get_current_user()
        val, err = toggle_note_bookmark(user.id, note_id)
        return jsonify({'success': True, 'is_bookmarked': val})

    @app.route('/notes/<int:note_id>/export')
    @login_required
    def note_export(note_id):
        user = get_current_user()
        note = get_note_by_id(user.id, note_id)
        if not note:
            flash("Note not found.", 'danger')
            return redirect(url_for('notes_view'))

        md_text = (
            f"# {note.title}\n\n"
            f"**Subject:** {note.subject} | **Topic:** {note.topic}\n"
            f"**Tags:** {note.tags or 'None'}\n"
            f"**Created:** {note.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"---\n\n"
            f"{note.content}\n"
        )
        safe_filename = "".join(c for c in note.title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')[:30] or "note"

        return Response(
            md_text,
            mimetype="text/markdown",
            headers={"Content-disposition": f"attachment; filename={safe_filename}.md"}
        )

    @app.route('/api/notes/quick-save', methods=['POST'])
    @login_required
    def api_note_quick_save():
        user = get_current_user()
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()

        title = data.get('title', 'Saved Note')
        content = data.get('content', '')
        subject = data.get('subject', 'General')
        topic = data.get('topic', 'General')
        tags = data.get('tags', 'quick-save')
        source = data.get('source', 'ai_mentor')

        note, error = create_note(
            user_id=user.id,
            title=title,
            content=content,
            subject=subject,
            topic=topic,
            tags=tags,
            source=source
        )

        if error:
            if request.is_json:
                return jsonify({'success': False, 'error': error}), 400
            flash(error, 'danger')
            return redirect(request.referrer or url_for('notes_view'))

        if request.is_json:
            return jsonify({'success': True, 'note_id': note.id, 'title': note.title})

        flash("Note saved to your notebook!", 'success')
        return redirect(request.referrer or url_for('notes_view'))

    # =========================================================================
    # SMART STUDY PLANNER
    # =========================================================================

    @app.route('/planner')
    @login_required
    def planner_view():
        user = get_current_user()
        active_plan_obj = get_active_plan(user.id)

        all_plans = StudyPlan.query.filter_by(user_id=user.id).order_by(StudyPlan.created_at.desc()).all()
        today = date.today()

        tasks = []
        today_tasks = []
        overdue_tasks = []

        if active_plan_obj:
            tasks = active_plan_obj.tasks.order_by(StudyTask.scheduled_date.asc(), StudyTask.id.asc()).all()
            today_tasks = [t for t in tasks if t.scheduled_date == today]
            overdue_tasks = [t for t in tasks if not t.is_completed and t.scheduled_date < today]

        # Analytics for weak topic pre-fill
        analytics = get_user_analytics(user.id)
        suggested_weak = [w['topic'] for w in analytics.get('weak_topics', [])]

        return render_template(
            'planner/planner_view.html',
            user=user,
            plan=active_plan_obj,
            all_plans=all_plans,
            tasks=tasks,
            today_tasks=today_tasks,
            overdue_tasks=overdue_tasks,
            today=today,
            suggested_weak=suggested_weak
        )

    @app.route('/planner/new')
    @login_required
    def planner_wizard():
        user = get_current_user()
        analytics = get_user_analytics(user.id)
        suggested_weak = [w['topic'] for w in analytics.get('weak_topics', [])]
        return render_template('planner/planner_wizard.html', user=user, suggested_weak=suggested_weak)

    @app.route('/planner/generate', methods=['POST'])
    @login_required
    def planner_generate():
        user = get_current_user()
        goal_title = request.form.get('goal_title', 'My Study Plan')
        target_goal = request.form.get('target_exam_or_goal', 'College & Placement Prep')
        knowledge_level = request.form.get('current_knowledge_level', 'Beginner')
        daily_hours = float(request.form.get('daily_hours_available', 2.0))
        target_date = request.form.get('target_completion_date')
        learning_style = request.form.get('preferred_learning_style', 'balanced')

        subjects = request.form.getlist('subjects')
        if not subjects:
            subjects = ['Python Programming', 'Data Structures', 'DBMS']

        weak_topics_raw = request.form.get('weak_topics', '')
        weak_topics = [t.strip() for t in weak_topics_raw.split(',') if t.strip()]

        if not target_date:
            target_date = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')

        plan = generate_study_plan(
            user_id=user.id,
            goal_title=goal_title,
            target_exam_or_goal=target_goal,
            knowledge_level=knowledge_level,
            daily_hours=daily_hours,
            target_date=target_date,
            subjects=subjects,
            weak_topics=weak_topics,
            learning_style=learning_style
        )

        flash(f"Personalized study plan '{plan.goal_title}' created with {plan.tasks.count()} tasks!", 'success')
        return redirect(url_for('planner_view'))

    @app.route('/planner/tasks/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def planner_task_toggle(task_id):
        user = get_current_user()
        val, err = toggle_task(task_id, user.id)
        if err:
            return jsonify({'success': False, 'error': err}), 404
        return jsonify({'success': True, 'is_completed': val})

    @app.route('/planner/tasks/<int:task_id>/reschedule', methods=['POST'])
    @login_required
    def planner_task_reschedule(task_id):
        user = get_current_user()
        task = StudyTask.query.filter_by(id=task_id, user_id=user.id).first()
        if not task:
            flash("Task not found.", 'danger')
            return redirect(url_for('planner_view'))

        # Move to tomorrow
        task.scheduled_date = date.today() + timedelta(days=1)
        db.session.commit()
        flash("Task rescheduled for tomorrow.", 'info')
        return redirect(url_for('planner_view'))

    @app.route('/planner/tasks/create', methods=['POST'])
    @login_required
    def planner_task_create():
        user = get_current_user()
        plan_id = request.form.get('plan_id', type=int)
        title = request.form.get('title')
        subject = request.form.get('subject', 'General')
        topic = request.form.get('topic', 'General')
        task_type = request.form.get('task_type', 'study')
        scheduled_date = request.form.get('scheduled_date')
        duration = request.form.get('duration_minutes', 30)

        task, error = create_task(
            user_id=user.id,
            plan_id=plan_id,
            title=title,
            subject=subject,
            topic=topic,
            task_type=task_type,
            scheduled_date=scheduled_date,
            duration_minutes=duration
        )

        if error:
            flash(error, 'danger')
        else:
            flash("Custom study task added!", 'success')

        return redirect(url_for('planner_view'))

    @app.route('/planner/tasks/<int:task_id>/delete', methods=['POST'])
    @login_required
    def planner_task_delete(task_id):
        user = get_current_user()
        ok, err = delete_task(user.id, task_id)
        if ok:
            flash("Task removed.", 'info')
        else:
            flash(err or "Failed to remove task.", 'danger')
        return redirect(url_for('planner_view'))

    @app.route('/planner/overdue/reschedule', methods=['POST'])
    @login_required
    def planner_reschedule_overdue_all():
        user = get_current_user()
        plan_id = request.form.get('plan_id', type=int)
        count = reschedule_overdue(user.id, plan_id)
        flash(f"Rescheduled {count} overdue tasks to today and upcoming slots.", 'success')
        return redirect(url_for('planner_view'))

    # =========================================================================
    # PREVIOUS YEAR QUESTIONS (PYQ)
    # =========================================================================

    @app.route('/pyq')
    @login_required
    def pyq_catalog():
        user = get_current_user()
        subject = request.args.get('subject', 'All')
        course = request.args.get('course', 'All')
        board = request.args.get('board', 'All')
        year = request.args.get('year', 'All')

        papers = get_pyq_papers(subject=subject, course=course, board=board, year=year)
        filters = get_pyq_filters()

        # Questions search
        q_search = request.args.get('q', '')
        q_type = request.args.get('qtype', 'All')
        q_diff = request.args.get('difficulty', 'All')
        questions = search_pyq_questions(subject=subject, qtype=q_type, difficulty=q_diff, search=q_search, limit=20)

        return render_template(
            'pyq/pyq_list.html',
            user=user,
            papers=papers,
            questions=questions,
            filters=filters,
            selected_subject=subject,
            selected_course=course,
            selected_board=board,
            selected_year=year,
            selected_qtype=q_type,
            selected_difficulty=q_diff,
            search_query=q_search
        )

    @app.route('/pyq/paper/<int:paper_id>')
    @login_required
    def pyq_paper_view(paper_id):
        user = get_current_user()
        paper, questions = get_paper_details(paper_id)
        if not paper:
            flash("Question paper not found.", 'warning')
            return redirect(url_for('pyq_catalog'))

        return render_template(
            'pyq/pyq_paper.html',
            user=user,
            paper=paper,
            questions=questions
        )

    @app.route('/pyq/practice')
    @login_required
    def pyq_practice_mode():
        user = get_current_user()
        subject = request.args.get('subject', 'All')
        qtype = request.args.get('qtype', 'mcq')
        limit = min(20, max(5, int(request.args.get('count', 10))))

        questions = search_pyq_questions(subject=subject, qtype=qtype, limit=limit)
        if not questions:
            questions = PreviousYearQuestion.query.limit(limit).all()

        return render_template(
            'pyq/pyq_practice.html',
            user=user,
            questions=questions,
            subject=subject,
            qtype=qtype
        )

    @app.route('/pyq/submit-practice', methods=['POST'])
    @login_required
    def pyq_practice_submit():
        user = get_current_user()
        eval_result = evaluate_pyq_practice(request.form)
        return render_template('pyq/pyq_practice_result.html', user=user, result=eval_result)

    @app.route('/pyq/upload', methods=['POST'])
    @login_required
    def pyq_upload_paper():
        user = get_current_user()
        title = request.form.get('title')
        subject = request.form.get('subject', 'General')
        course = request.form.get('course', 'B.Tech')
        exam_board = request.form.get('exam_board', 'University')
        exam_year = request.form.get('exam_year', 2024)

        file = request.files.get('file') or request.files.get('paper_file')
        raw_text = request.form.get('raw_text', '')

        if file and file.filename:
            if file.filename.lower().endswith('.pdf'):
                extracted = extract_text_from_pdf(file.stream)
                raw_text = f"{raw_text}\n\n{extracted}"
            else:
                try:
                    raw_text = f"{raw_text}\n\n{file.read().decode('utf-8', errors='ignore')}"
                except Exception:
                    pass

        if not raw_text.strip():
            flash("Please provide either a PDF document or paste question paper text.", 'danger')
            return redirect(url_for('pyq_catalog'))

        paper, count = parse_and_create_pyq_paper(
            title=title or f"{subject} Exam Paper ({exam_year})",
            subject=subject,
            course=course,
            exam_board=exam_board,
            exam_year=exam_year,
            raw_text=raw_text,
            source_note=f"Uploaded by @{user.username} (Community Verified)"
        )

        flash(f"Question paper '{paper.title}' imported successfully with {count} questions extracted!", 'success')
        return redirect(url_for('pyq_paper_view', paper_id=paper.id))

    # =========================================================================
    # SMART PRACTICE & ASSESSMENT HUB
    # =========================================================================

    @app.route('/practice')
    @login_required
    def practice_hub():
        user = get_current_user()
        analytics = get_user_analytics(user.id)
        weak_topics = analytics.get('weak_topics', [])

        # Sample practice coding problems (educational challenges)
        coding_problems = [
            {
                'id': 1,
                'title': 'Reverse a Singly Linked List',
                'difficulty': 'Medium',
                'category': 'Data Structures',
                'description': 'Given the head of a singly linked list, reverse the list and return the reversed list head.',
                'starter_code': 'class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverseList(head):\n    # Write your solution here\n    pass',
                'test_cases': [{'input': '[1, 2, 3, 4, 5]', 'expected': '[5, 4, 3, 2, 1]'}],
                'hint': 'Use three pointers: prev, curr, and nxt to reverse pointer links in a single pass.'
            },
            {
                'id': 2,
                'title': 'Two Sum - Target Pair Indices',
                'difficulty': 'Easy',
                'category': 'Algorithms',
                'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                'starter_code': 'def twoSum(nums, target):\n    # Write your solution here\n    pass',
                'test_cases': [{'input': 'nums = [2, 7, 11, 15], target = 9', 'expected': '[0, 1]'}],
                'hint': 'Use a hash map to look up the complement (target - num) in O(1) time.'
            },
            {
                'id': 3,
                'title': 'Valid Parentheses Matching',
                'difficulty': 'Easy',
                'category': 'Stacks',
                'description': 'Determine if an input string containing (), {}, and [] has valid opening and closing bracket matching.',
                'starter_code': 'def isValid(s):\n    # Write your solution here\n    pass',
                'test_cases': [{'input': '"()[]{}"', 'expected': 'True'}, {'input': '"(]"', 'expected': 'False'}],
                'hint': 'Push opening brackets to a stack; for closing brackets, check if stack.pop() matches.'
            }
        ]

        return render_template(
            'practice/practice_hub.html',
            user=user,
            analytics=analytics,
            weak_topics=weak_topics,
            coding_problems=coding_problems
        )

    # =========================================================================
    # BOOKMARKS HUB
    # =========================================================================

    @app.route('/bookmarks')
    @login_required
    def bookmarks_view():
        user = get_current_user()
        item_type = request.args.get('type', 'all')
        bookmarks = get_user_bookmarks(user.id, item_type=item_type)
        return render_template(
            'bookmarks/bookmarks_view.html',
            user=user,
            bookmarks=bookmarks,
            selected_type=item_type
        )

    @app.route('/api/bookmarks/<int:bookmark_id>/delete', methods=['POST'])
    @login_required
    def api_delete_bookmark(bookmark_id):
        user = get_current_user()
        ok = remove_bookmark(user.id, bookmark_id)
        return jsonify({'success': ok})

    # =========================================================================
    # STUDENT PROFILE & SETTINGS
    # =========================================================================

    @app.route('/profile')
    @login_required
    def profile_view():
        user = get_current_user()
        analytics = get_user_analytics(user.id)
        recs = generate_personalized_recommendations(user.id)
        notes_count = Note.query.filter_by(user_id=user.id).count()
        tasks_completed = StudyTask.query.filter_by(user_id=user.id, is_completed=True).count()
        streak = calculate_user_streak(user.id)

        return render_template(
            'profile/profile_view.html',
            user=user,
            analytics=analytics,
            recommendations=recs,
            notes_count=notes_count,
            tasks_completed=tasks_completed,
            streak=streak
        )

    @app.route('/profile/update', methods=['POST'])
    @login_required
    def profile_update():
        user = get_current_user()
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        degree_or_stream = request.form.get('degree_or_stream')
        target_exam = request.form.get('target_exam')
        learning_path = request.form.get('learning_path')
        semester = request.form.get('semester')
        skill_level = request.form.get('skill_level')
        study_goals = request.form.get('study_goals')
        preferred_subjects = request.form.get('preferred_subjects')

        updated_user, error = update_user_profile(
            user_id=user.id,
            full_name=full_name,
            email=email,
            degree_or_stream=degree_or_stream,
            target_exam=target_exam,
            learning_path=learning_path,
            semester=semester,
            skill_level=skill_level,
            study_goals=study_goals,
            preferred_subjects=preferred_subjects
        )

        if error:
            flash(error, 'danger')
        else:
            flash("Profile details updated successfully!", 'success')

        return redirect(url_for('profile_view'))

    @app.route('/profile/change-password', methods=['POST'])
    @login_required
    def profile_change_password():
        user = get_current_user()
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        success, error = change_user_password(
            user_id=user.id,
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password
        )

        if error:
            flash(error, 'danger')
        else:
            flash("Your password has been changed successfully!", 'success')

        return redirect(url_for('profile_view'))

    @app.route('/settings')
    @login_required
    def settings_view():
        user = get_current_user()
        provider_name, provider_key = get_active_provider()
        return render_template(
            'settings/settings_view.html',
            user=user,
            ai_provider=provider_name,
            has_live_llm=bool(provider_key)
        )

    @app.route('/settings/update', methods=['POST'])
    @login_required
    def settings_update():
        user = get_current_user()
        theme = request.form.get('theme_preference', user.theme_preference or 'light')
        skill_level = request.form.get('skill_level', user.skill_level)
        study_goals = request.form.get('study_goals', user.study_goals)

        user.theme_preference = theme
        user.skill_level = skill_level
        user.study_goals = study_goals
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'json' in request.headers.get('Accept', ''):
            return jsonify({'success': True, 'theme': theme})

        flash("Settings saved successfully!", 'success')
        return redirect(url_for('settings_view'))

    # =========================================================================
    # QUIZ ENGINE (PRESERVED)
    # =========================================================================

    @app.route('/quiz')
    @login_required
    def quiz_view():
        user = get_current_user()
        learning_path = request.args.get('path', user.learning_path or 'college')
        subject = request.args.get('subject', 'Python Programming')
        exam = request.args.get('exam', None)
        difficulty = request.args.get('difficulty', None)

        try:
            count = int(request.args.get('count', 10))
        except (ValueError, TypeError):
            count = 10
        count = max(3, min(100, count))

        default_time = 15 if learning_path == 'competitive' else 0
        try:
            time_limit = int(request.args.get('time_limit', default_time))
        except (ValueError, TypeError):
            time_limit = default_time
        time_limit = max(0, min(180, time_limit))

        clean_diff = difficulty if difficulty and difficulty.lower() != 'all' else None

        questions, available_count = get_quiz_questions(
            learning_path=learning_path,
            subject_or_category=subject,
            exam_name=exam,
            limit=count,
            difficulty=clean_diff
        )

        if not questions:
            flash(f"No questions found for {subject} with the selected filters. Please choose another subject or reset difficulty.", 'warning')
            if learning_path == 'competitive':
                return redirect(url_for('competitive_path'))
            return redirect(url_for('college_path'))

        if available_count < count:
            flash(f"Note: Only {available_count} questions are available matching your filter (requested {count}). Showing all {available_count} questions.", 'info')

        duration_minutes = time_limit if time_limit > 0 else None

        return render_template(
            'quiz/quiz_view.html',
            user=user,
            questions=questions,
            learning_path=learning_path,
            subject=subject,
            exam=exam,
            duration_minutes=duration_minutes,
            time_limit_minutes=time_limit,
            available_count=available_count,
            difficulty=difficulty or 'all'
        )

    @app.route('/quiz/submit', methods=['POST'])
    @login_required
    def submit_quiz():
        user = get_current_user()
        learning_path = request.form.get('learning_path', 'college')
        subject = request.form.get('subject', 'General')
        exam = request.form.get('exam', None)
        time_taken = request.form.get('time_taken_seconds', 0)
        time_limit = request.form.get('time_limit_minutes', 0)

        answers = {}
        for key, val in request.form.items():
            if key.startswith('answer_'):
                qid = key.replace('answer_', '')
                answers[qid] = val

        if not answers:
            flash("No answers were submitted.", 'warning')
            return redirect(url_for('dashboard'))

        attempt, breakdown = submit_quiz_attempt(
            user_id=user.id,
            learning_path=learning_path,
            subject_or_category=subject,
            exam_name=exam,
            answers_dict=answers,
            time_taken_seconds=time_taken,
            time_limit_minutes=time_limit
        )

        return redirect(url_for('quiz_result', attempt_id=attempt.id))

    @app.route('/quiz/result/<int:attempt_id>')
    @login_required
    def quiz_result(attempt_id):
        user = get_current_user()
        attempt = db.get_or_404(QuizAttempt, attempt_id)

        if attempt.user_id != user.id:
            flash("Unauthorized access to quiz attempt.", 'danger')
            return redirect(url_for('dashboard'))

        answers = StudentAnswer.query.filter_by(attempt_id=attempt.id).all()
        breakdown = []
        for a in answers:
            q = a.question
            breakdown.append({
                'question_id': q.id,
                'question_text': q.question_text,
                'topic': q.topic,
                'difficulty': q.difficulty,
                'options': {
                    'A': q.option_a,
                    'B': q.option_b,
                    'C': q.option_c,
                    'D': q.option_d
                },
                'selected_option': a.selected_option,
                'correct_option': q.correct_option,
                'is_correct': a.is_correct,
                'explanation': q.explanation
            })

        recs = generate_personalized_recommendations(user.id)

        return render_template(
            'quiz/result_view.html',
            attempt=attempt,
            breakdown=breakdown,
            recommendations=recs
        )

    @app.route('/api/quiz/available_count')
    @login_required
    def quiz_available_count():
        learning_path = request.args.get('path', 'college')
        subject = request.args.get('subject', '')
        exam = request.args.get('exam', None)
        difficulty = request.args.get('difficulty', None)

        available = count_eligible_questions(
            learning_path=learning_path,
            subject_or_category=subject,
            exam_name=exam,
            difficulty=difficulty
        )
        return jsonify({'available': available})

    return app


# Module-level WSGI entry point for Gunicorn (e.g. gunicorn --bind 0.0.0.0:$PORT app:app)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    is_prod = (resolve_config_name() in ('production', 'prod'))
    app.run(host='127.0.0.1', port=port, debug=not is_prod)
