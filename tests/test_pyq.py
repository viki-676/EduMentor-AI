import pytest
import io
from models import db, PYQPaper, PreviousYearQuestion
from services.pyq_service import (
    get_pyq_papers, get_paper_details, search_pyq_questions,
    evaluate_pyq_practice, extract_text_from_pdf, parse_and_create_pyq_paper
)

def test_pyq_papers_seeded(app):
    with app.app_context():
        papers = PYQPaper.query.all()
        assert len(papers) >= 3
        subjects = set(p.subject for p in papers)
        assert "Computer Science" in subjects or "Operating Systems" in subjects or "Quantitative Aptitude" in subjects
        questions = PreviousYearQuestion.query.all()
        assert len(questions) >= 9

def test_pyq_filtering_and_paper_detail(app):
    with app.app_context():
        papers = get_pyq_papers(course="GATE / B.Tech CSE")
        assert len(papers) >= 1

        paper = PYQPaper.query.first()
        p_obj, qs = get_paper_details(paper.id)
        assert p_obj is not None
        assert len(qs) > 0
        assert qs[0].paper_id == paper.id

def test_pyq_practice_evaluation(app):
    with app.app_context():
        mcqs = PreviousYearQuestion.query.filter_by(question_type='mcq').all()
        assert len(mcqs) > 0

        target_q = mcqs[0]
        # Test correct answer
        answers = {f"pyq_{target_q.id}": target_q.correct_answer}
        result = evaluate_pyq_practice(answers)
        assert result['score'] == target_q.marks
        assert result['percentage'] == 100.0
        assert result['breakdown'][0]['is_correct'] is True

        # Test incorrect answer
        wrong_ans = 'A' if target_q.correct_answer != 'A' else 'B'
        wrong_answers = {f"pyq_{target_q.id}": wrong_ans}
        wrong_result = evaluate_pyq_practice(wrong_answers)
        assert wrong_result['score'] == 0
        assert wrong_result['percentage'] == 0.0
        assert wrong_result['breakdown'][0]['is_correct'] is False

def test_pyq_routes_authenticated(auth_client, app):
    # Catalog view
    res = auth_client.get('/pyq')
    assert res.status_code == 200
    assert b"Authentic PYQ Repository" in res.data or b"Previous Year Question Papers" in res.data

    with app.app_context():
        paper = PYQPaper.query.first()
        p_id = paper.id

    # Paper view
    paper_res = auth_client.get(f'/pyq/paper/{p_id}')
    assert paper_res.status_code == 200
    assert paper.exam_name.encode('utf-8') in paper_res.data

    # Practice mode
    practice_res = auth_client.get('/pyq/practice')
    assert practice_res.status_code == 200
    assert b"Authentic Exam Practice Drill" in practice_res.data

def test_pyq_upload_parser(app):
    with app.app_context():
        raw_text = """
        Q1. What is the time complexity of QuickSort in the worst case?
        A) O(n)
        B) O(n log n)
        C) O(n^2)
        D) O(1)
        Answer: C
        Explanation: Worst case occurs when the pivot is always the smallest or largest element.

        Q2. Define Thrashing in Operating Systems.
        Answer: High paging activity where CPU spends more time swapping pages than executing processes.
        """
        paper, count = parse_and_create_pyq_paper(
            title="University OS Midterm 2024",
            subject="Operating Systems",
            course="B.Tech",
            exam_board="State Tech University",
            exam_year=2024,
            raw_text=raw_text,
            source_note="Uploaded test paper"
        )
        assert paper is not None
        assert count >= 1
        assert paper.is_verified is False  # Correctly labeled community paper
