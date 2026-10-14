"""
Previous Year Questions (PYQ) service for querying papers, practice mode, scoring, and PDF extraction.
"""

import os
import re
from models import db, PYQPaper, PreviousYearQuestion, Bookmark

def get_pyq_papers(subject=None, course=None, board=None, year=None):
    """Retrieve question papers matching filters."""
    query = PYQPaper.query

    if subject and subject != 'All':
        query = query.filter(PYQPaper.subject.ilike(f"%{subject}%"))
    if course and course != 'All':
        query = query.filter(PYQPaper.course.ilike(f"%{course}%"))
    if board and board != 'All':
        query = query.filter(PYQPaper.exam_board.ilike(f"%{board}%"))
    if year and year != 'All':
        try:
            query = query.filter_by(exam_year=int(year))
        except (ValueError, TypeError):
            pass

    return query.order_by(PYQPaper.exam_year.desc(), PYQPaper.id.desc()).all()

def get_pyq_filters():
    """Retrieve distinct filter values for the PYQ browsing interface."""
    papers = PYQPaper.query.all()
    subjects = sorted(list({p.subject for p in papers if p.subject}))
    courses = sorted(list({p.course for p in papers if p.course}))
    boards = sorted(list({p.exam_board for p in papers if p.exam_board}))
    years = sorted(list({p.exam_year for p in papers if p.exam_year}), reverse=True)
    return {
        'subjects': subjects,
        'courses': courses,
        'boards': boards,
        'years': years
    }

def get_paper_details(paper_id):
    """Get single question paper and its questions."""
    paper = db.session.get(PYQPaper, paper_id)
    if not paper:
        return None, []
    questions = PreviousYearQuestion.query.filter_by(paper_id=paper.id).order_by(PreviousYearQuestion.id.asc()).all()
    return paper, questions

def search_pyq_questions(subject=None, topic=None, qtype=None, difficulty=None, search=None, limit=25):
    """Search and filter individual questions across papers."""
    query = PreviousYearQuestion.query

    if subject and subject != 'All':
        query = query.filter(PreviousYearQuestion.subject.ilike(f"%{subject}%"))
    if topic and topic != 'All':
        query = query.filter(PreviousYearQuestion.topic.ilike(f"%{topic}%"))
    if qtype and qtype != 'All':
        query = query.filter_by(question_type=qtype)
    if difficulty and difficulty != 'All':
        query = query.filter_by(difficulty=difficulty)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (PreviousYearQuestion.question_text.ilike(term)) |
            (PreviousYearQuestion.topic.ilike(term)) |
            (PreviousYearQuestion.explanation.ilike(term))
        )

    return query.limit(limit).all()

def evaluate_pyq_practice(answers_dict):
    """
    Evaluate student submitted answers for PYQ practice session.
    Format: answers_dict = { 'pyq_<id>': 'A'|'B'|'C'|'D'|'text answer' }
    Returns summary and detailed question-by-question breakdown.
    """
    question_ids = []
    submitted_answers = {}

    for key, val in answers_dict.items():
        if key.startswith('pyq_'):
            try:
                qid = int(key.replace('pyq_', ''))
                question_ids.append(qid)
                submitted_answers[qid] = val
            except ValueError:
                pass

    if not question_ids:
        return {'score': 0, 'total': 0, 'percentage': 0, 'breakdown': []}

    questions = PreviousYearQuestion.query.filter(PreviousYearQuestion.id.in_(question_ids)).all()
    score = 0
    total_mcqs = 0
    breakdown = []

    for q in questions:
        user_ans = submitted_answers.get(q.id, '').strip()
        is_mcq = q.question_type == 'mcq'
        is_correct = False

        if is_mcq:
            total_mcqs += 1
            if user_ans.upper() == q.correct_answer.strip().upper():
                score += q.marks
                is_correct = True
        else:
            # Conceptual question self-assessment
            is_correct = bool(user_ans)

        breakdown.append({
            'question_id': q.id,
            'question_text': q.question_text,
            'question_type': q.question_type,
            'topic': q.topic,
            'marks': q.marks,
            'user_answer': user_ans,
            'correct_answer': q.correct_answer,
            'is_correct': is_correct,
            'explanation': q.explanation,
            'suggested_answer_structure': q.suggested_answer_structure,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c,
                'D': q.option_d
            } if is_mcq else None
        })

    pct = round((score / max(1, total_mcqs * 2)) * 100, 1) if total_mcqs > 0 else 100.0

    return {
        'score': score,
        'total_mcqs': total_mcqs,
        'total_questions': len(questions),
        'percentage': pct,
        'breakdown': breakdown
    }

def extract_text_from_pdf(file_stream):
    """Extract text from uploaded PDF using pypdf with page traceability."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_stream)
        pages_content = []
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ''
            if txt.strip():
                pages_content.append(f"--- Page {idx + 1} ---\n{txt.strip()}")
        return "\n\n".join(pages_content)
    except Exception as e:
        return f"PDF Extraction notice: {e}"

def parse_and_create_pyq_paper(title, subject, course, exam_board, exam_year, raw_text, source_note="Uploaded Question Paper"):
    """
    Parses questions from raw text / PDF dump and creates paper + questions in database.
    """
    paper = PYQPaper(
        title=title,
        subject=subject,
        course=course,
        exam_board=exam_board,
        exam_year=int(exam_year or 2024),
        is_verified=False, # Marked as Community / User Uploaded for transparency
        source_reference=source_note
    )
    db.session.add(paper)
    db.session.flush()

    # Simple heuristic to extract multiple-choice and conceptual numbered questions
    # e.g., "1. Question text ... A) ... B) ..."
    blocks = re.split(r'\n(?=\d+[\.\)]\s+)', raw_text)
    created_count = 0

    for block in blocks:
        block = block.strip()
        if len(block) < 20:
            continue

        lines = block.split('\n')
        header_match = re.match(r'^\d+[\.\)]\s*(.*)', lines[0])
        question_text = header_match.group(1).strip() if header_match else lines[0].strip()

        # Check for options
        opt_a, opt_b, opt_c, opt_d = None, None, None, None
        q_type = 'short_answer'

        match_a = re.search(r'[A\(\[]\s*[:\.\)]\s*(.*?)(?=[B\(\[]\s*[:\.\)]|$)', block, re.DOTALL)
        match_b = re.search(r'[B\(\[]\s*[:\.\)]\s*(.*?)(?=[C\(\[]\s*[:\.\)]|$)', block, re.DOTALL)
        match_c = re.search(r'[C\(\[]\s*[:\.\)]\s*(.*?)(?=[D\(\[]\s*[:\.\)]|$)', block, re.DOTALL)
        match_d = re.search(r'[D\(\[]\s*[:\.\)]\s*(.*?)(?=\n\n|$)', block, re.DOTALL)

        if match_a and match_b:
            opt_a = match_a.group(1).strip()[:200]
            opt_b = match_b.group(1).strip()[:200]
            opt_c = match_c.group(1).strip()[:200] if match_c else "None of the above"
            opt_d = match_d.group(1).strip()[:200] if match_d else "All of the above"
            q_type = 'mcq'

        pyq = PreviousYearQuestion(
            paper_id=paper.id,
            subject=subject,
            course=course,
            exam_board=exam_board,
            exam_year=paper.exam_year,
            topic=f"{subject} Concepts",
            question_type=q_type,
            difficulty='Medium',
            marks=2 if q_type == 'mcq' else 5,
            question_text=question_text[:500] if question_text else block[:300],
            option_a=opt_a,
            option_b=opt_b,
            option_c=opt_c,
            option_d=opt_d,
            correct_answer='A' if q_type == 'mcq' else 'Review solution from lecture notes',
            explanation="Extracted from uploaded examination paper document.",
            is_verified=False
        )
        db.session.add(pyq)
        created_count += 1
        if created_count >= 15: # safety cap per document
            break

    db.session.commit()
    return paper, created_count
