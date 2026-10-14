import pytest
from datetime import date, timedelta
from models import db, StudyPlan, StudyTask
from services.planner_service import (
    generate_study_plan, get_today_tasks,
    toggle_task, reschedule_overdue
)

def test_planner_generation_and_constraints(app):
    with app.app_context():
        user_id = 1
        daily_hours = 2.5
        target_date = date.today() + timedelta(days=14)

        plan = generate_study_plan(
            user_id=user_id,
            plan_title="GATE CS Sprint",
            target_exam_or_goal="GATE CS 2025",
            daily_available_hours=daily_hours,
            target_date=target_date,
            focus_areas=["Data Structures", "DBMS", "Operating Systems"],
            learning_style="balanced"
        )

        assert plan is not None
        assert plan.daily_available_hours == daily_hours
        tasks = plan.tasks.all()
        assert len(tasks) > 0

        # Verify daily hour constraint is respected: tasks on any day <= daily_hours * 60 minutes
        daily_task_minutes = {}
        for t in tasks:
            daily_task_minutes[t.scheduled_date] = daily_task_minutes.get(t.scheduled_date, 0) + t.duration_minutes

        for sched_date, total_mins in daily_task_minutes.items():
            assert total_mins <= (daily_hours * 60) + 15, f"Over-budget schedule on {sched_date}: {total_mins} mins vs {daily_hours * 60} mins allowed"

def test_task_toggle_and_reschedule(app):
    with app.app_context():
        user_id = 1
        plan = StudyPlan(user_id=user_id, title="Test Plan", daily_available_hours=3.0)
        db.session.add(plan)
        db.session.commit()

        # Task yesterday (overdue)
        yesterday = date.today() - timedelta(days=2)
        task = StudyTask(
            plan_id=plan.id,
            user_id=user_id,
            title="Overdue DSA Practice",
            subject="Data Structures",
            scheduled_date=yesterday,
            duration_minutes=45,
            is_completed=False
        )
        db.session.add(task)
        db.session.commit()

        # Reschedule overdue
        rescheduled_count = reschedule_overdue(user_id, plan.id)
        assert rescheduled_count >= 1

        db.session.refresh(task)
        assert task.scheduled_date == date.today()

        # Toggle complete
        is_done, err = toggle_task(task.id, user_id)
        assert is_done is True
        assert err is None
        db.session.refresh(task)
        assert task.is_completed is True

def test_planner_routes_authenticated(auth_client):
    # Wizard view
    res = auth_client.get('/planner/new')
    assert res.status_code == 200
    assert b"Smart Study Plan Generator" in res.data

    # Generate plan via form
    gen_res = auth_client.post('/planner/generate', data={
        'plan_title': 'Placement Prep',
        'target_exam_or_goal': 'Campus Placements',
        'daily_hours': '3.0',
        'target_date': (date.today() + timedelta(days=20)).isoformat(),
        'focus_areas_custom': 'Python Programming, SQL',
        'learning_style': 'balanced'
    }, follow_redirects=True)
    assert gen_res.status_code == 200
    assert b"Today's Agenda" in gen_res.data or b"Study Planner" in gen_res.data
