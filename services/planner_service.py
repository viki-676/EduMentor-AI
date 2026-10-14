"""
Smart Study Planner service for realistic personalized schedules, task management, and rescheduling.
"""

import json
from datetime import date, datetime, timedelta, timezone
from models import db, StudyPlan, StudyTask, LearningResource

def generate_study_plan(user_id, goal_title=None, target_exam_or_goal=None, knowledge_level='Beginner', daily_hours=2.0, target_date=None, subjects=None, weak_topics=None, learning_style='balanced', **kwargs):
    """
    Generates a personalized daily and weekly study plan without exceeding available daily hours.
    """
    if 'plan_title' in kwargs and not goal_title:
        goal_title = kwargs['plan_title']
    if 'daily_available_hours' in kwargs:
        daily_hours = kwargs['daily_available_hours']
    if 'focus_areas' in kwargs and not subjects:
        subjects = kwargs['focus_areas']

    if not subjects:
        subjects = ['Python Programming', 'Data Structures', 'DBMS']

    today = date.today()
    if not target_date:
        target_date = today + timedelta(days=30)
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    total_days = (target_date - today).days
    if total_days < 3:
        total_days = 7
        target_date = today + timedelta(days=7)
    elif total_days > 120:
        total_days = 120
        target_date = today + timedelta(days=120)

    daily_hours = max(1.0, min(8.0, float(daily_hours or 2.0)))
    daily_budget_minutes = int(daily_hours * 60)

    # Archive previous active plans for this student
    existing_active = StudyPlan.query.filter_by(user_id=user_id, status='active').all()
    for ep in existing_active:
        ep.status = 'archived'

    plan = StudyPlan(
        user_id=user_id,
        goal_title=goal_title or f"Plan for {target_exam_or_goal}",
        target_exam_or_goal=target_exam_or_goal or "General Mastery",
        current_knowledge_level=knowledge_level or "Beginner",
        daily_hours_available=daily_hours,
        start_date=today,
        target_completion_date=target_date,
        preferred_learning_style=learning_style,
        subjects_to_cover_json=json.dumps(subjects if isinstance(subjects, list) else [subjects]),
        weak_topics_priority_json=json.dumps(weak_topics if isinstance(weak_topics, list) else ([weak_topics] if weak_topics else [])),
        status='active'
    )
    db.session.add(plan)
    db.session.flush()

    # Subject topics catalog for scheduling
    subject_topics = {
        'Python Programming': ['Variables & Data Types', 'Control Flow & Loops', 'Functions & Scope', 'Lists & Dictionaries', 'OOP & Classes'],
        'Data Structures': ['Arrays & Complexity', 'Linked Lists', 'Stacks & Queues', 'Binary Trees', 'Sorting Algorithms'],
        'DBMS': ['Relational Model', 'SQL Joins & Queries', 'Normalization (1NF-3NF)', 'ACID Transactions', 'Indexing'],
        'Operating Systems': ['Processes & Threads', 'CPU Scheduling', 'Deadlocks', 'Virtual Memory & Paging', 'File Systems'],
        'Computer Networks': ['OSI 7 Layers', 'TCP 3-Way Handshake', 'IP Addressing & Subnets', 'DNS Resolution', 'HTTP/HTTPS Protocols'],
        'Quantitative Aptitude': ['Percentages & Profit-Loss', 'Ratio & Proportion', 'Time, Speed & Distance', 'Time & Work', 'Number Systems'],
        'Logical Reasoning': ['Syllogisms', 'Blood Relations', 'Coding-Decoding', 'Series & Analogies', 'Direction Sense'],
        'Artificial Intelligence': ['Supervised Learning', 'Neural Networks', 'Evaluation Metrics', 'NLP & Transformers', 'Model Overfitting']
    }

    # Flatten topics to schedule
    scheduled_subjects = subjects if isinstance(subjects, list) else [subjects]
    topics_queue = []
    
    # Priority for weak topics
    if weak_topics:
        for wt in weak_topics:
            topics_queue.append(('Priority Revision', str(wt), 'revision'))

    for sub in scheduled_subjects:
        topics = subject_topics.get(sub, [f"{sub} Core Concepts", f"{sub} Practice", f"{sub} Advanced Review"])
        for top in topics:
            topics_queue.append((sub, top, 'study'))

    if not topics_queue:
        topics_queue = [('General Study', 'Core Concepts & Principles', 'study')]

    topic_idx = 0
    num_topics = len(topics_queue)

    for day_i in range(1, total_days + 1):
        sched_date = today + timedelta(days=day_i - 1)
        day_minutes_used = 0

        # Day 7, 14, 21... are Comprehensive Mock Test days
        if day_i % 7 == 0:
            mock_duration = min(60, daily_budget_minutes - 15)
            t1 = StudyTask(
                plan_id=plan.id,
                user_id=user_id,
                day_number=day_i,
                scheduled_date=sched_date,
                title=f"Weekly Mock Test & Performance Review",
                subject="Comprehensive Assessment",
                topic="Full Syllabus Mock Drill",
                task_type="mock_test",
                duration_minutes=mock_duration
            )
            db.session.add(t1)
            day_minutes_used += mock_duration

            if daily_budget_minutes - day_minutes_used >= 20:
                review_duration = daily_budget_minutes - day_minutes_used
                t2 = StudyTask(
                    plan_id=plan.id,
                    user_id=user_id,
                    day_number=day_i,
                    scheduled_date=sched_date,
                    title="Review Mock Test Explanations & Error Log",
                    subject="Assessment Review",
                    topic="Error Diagnosis",
                    task_type="revision",
                    duration_minutes=review_duration
                )
                db.session.add(t2)
            continue

        # Day 3, 6, 9... are Spaced Revision days
        if day_i % 3 == 0:
            prev_sub, prev_top, _ = topics_queue[(topic_idx - 1) % num_topics]
            rev_time = min(45, daily_budget_minutes // 2)
            t_rev = StudyTask(
                plan_id=plan.id,
                user_id=user_id,
                day_number=day_i,
                scheduled_date=sched_date,
                title=f"Spaced Revision: {prev_top}",
                subject=prev_sub,
                topic=prev_top,
                task_type="revision",
                duration_minutes=rev_time,
                notes="Review summary notes, formulas, and common traps."
            )
            db.session.add(t_rev)
            day_minutes_used += rev_time

        # Allocate Core Concept Study Session
        if day_minutes_used + 40 <= daily_budget_minutes:
            curr_sub, curr_top, _ = topics_queue[topic_idx % num_topics]
            topic_idx += 1
            study_duration = 45 if (daily_budget_minutes - day_minutes_used) >= 60 else 35
            t_study = StudyTask(
                plan_id=plan.id,
                user_id=user_id,
                day_number=day_i,
                scheduled_date=sched_date,
                title=f"Concept Study: {curr_top}",
                subject=curr_sub,
                topic=curr_top,
                task_type="study",
                duration_minutes=study_duration,
                notes="Read resource concepts and step-by-step examples."
            )
            db.session.add(t_study)
            day_minutes_used += study_duration

            # Allocate Practice Session if budget remains
            remaining = daily_budget_minutes - day_minutes_used
            if remaining >= 20:
                t_practice = StudyTask(
                    plan_id=plan.id,
                    user_id=user_id,
                    day_number=day_i,
                    scheduled_date=sched_date,
                    title=f"Practice MCQs & Drills: {curr_top}",
                    subject=curr_sub,
                    topic=curr_top,
                    task_type="practice",
                    duration_minutes=remaining,
                    notes="Take 5-10 practice questions and analyze explanations."
                )
                db.session.add(t_practice)

    db.session.commit()
    return plan

def get_active_plan(user_id):
    """Retrieve current active study plan for user."""
    return StudyPlan.query.filter_by(user_id=user_id, status='active').first()

def get_today_tasks(user_id):
    """Fetch all tasks scheduled for today."""
    today = date.today()
    return StudyTask.query.filter_by(user_id=user_id, scheduled_date=today).order_by(StudyTask.is_completed.asc(), StudyTask.id.asc()).all()

def toggle_task(task_id, user_id):
    """Toggle task is_completed and record completion timestamp."""
    task = StudyTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return False, "Task not found."

    task.is_completed = not task.is_completed
    task.completed_at = datetime.now(timezone.utc) if task.is_completed else None
    db.session.commit()
    return task.is_completed, None

def reschedule_overdue(user_id, plan_id):
    """Automatically pushes incomplete overdue tasks to today or next available slots."""
    today = date.today()
    overdue_tasks = StudyTask.query.filter(
        StudyTask.user_id == user_id,
        StudyTask.plan_id == plan_id,
        StudyTask.is_completed == False,
        StudyTask.scheduled_date < today
    ).all()

    for idx, t in enumerate(overdue_tasks):
        t.scheduled_date = today + timedelta(days=idx // 2)

    db.session.commit()
    return len(overdue_tasks)

def create_task(user_id, plan_id, title, subject, topic, task_type='study', scheduled_date=None, duration_minutes=30):
    if not title:
        return None, "Task title is required."

    if not scheduled_date:
        sched_date = date.today()
    elif isinstance(scheduled_date, str):
        sched_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
    else:
        sched_date = scheduled_date

    task = StudyTask(
        plan_id=plan_id,
        user_id=user_id,
        title=title.strip(),
        subject=(subject or 'General').strip(),
        topic=(topic or 'General').strip(),
        task_type=task_type or 'study',
        scheduled_date=sched_date,
        duration_minutes=int(duration_minutes or 30),
        is_completed=False
    )
    db.session.add(task)
    db.session.commit()
    return task, None

def delete_task(user_id, task_id):
    task = StudyTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return False, "Task not found."
    db.session.delete(task)
    db.session.commit()
    return True, None
