import pytest
from models import db, LearningResource, ResourceProgress, Bookmark
from services.resource_service import (
    get_resources, toggle_resource_progress, toggle_resource_bookmark, normalize_category
)

def test_resources_catalog_seeded(app):
    with app.app_context():
        resources = LearningResource.query.all()
        assert len(resources) >= 10
        categories = set(r.category for r in resources)
        assert "Programming Languages" in categories
        assert "Artificial Intelligence and Machine Learning" in categories
        assert "Operating Systems" in categories

def test_resources_catalog_filtering(app):
    with app.app_context():
        py_res = get_resources(category="Programming Languages")
        assert len(py_res) >= 1
        assert py_res[0]['category'] == "Programming Languages"

        beg_res = get_resources(difficulty="Beginner")
        assert all(r['difficulty'] == "Beginner" for r in beg_res)

        search_res = get_resources(search="Memory")
        assert any("Memory" in r['title'] or "Memory" in r['summary'] for r in search_res)

def test_resource_progress_and_bookmark(app, auth_client):
    with app.app_context():
        res = LearningResource.query.first()
        res_id = res.id
        user_id = 1

        # Test toggle complete
        completed = toggle_resource_progress(user_id, res_id)
        assert completed is True

        prog = ResourceProgress.query.filter_by(user_id=user_id, resource_id=res_id).first()
        assert prog is not None
        assert prog.is_completed is True

        # Test toggle bookmark
        bookmarked = toggle_resource_bookmark(user_id, res_id)
        assert bookmarked is True

        bm = Bookmark.query.filter_by(user_id=user_id, item_type="resource", item_id=res_id).first()
        assert bm is not None

def test_resource_routes_authenticated(auth_client, app):
    # Catalog view
    res = auth_client.get('/resources')
    assert res.status_code == 200
    assert b"Concept Notes" in res.data or b"Learning Resources" in res.data

    with app.app_context():
        r = LearningResource.query.first()
        slug = r.slug
        r_id = r.id

    # Detail view
    res_detail = auth_client.get(f'/resources/{slug}')
    assert res_detail.status_code == 200
    assert r.title.encode('utf-8') in res_detail.data
    assert b"Key Definitions &amp; Terminology" in res_detail.data
    assert b"Core Concepts &amp; Principles" in res_detail.data
    assert b"Key Takeaways for Quick Revision" in res_detail.data
    assert b"Common Pitfalls &amp; Traps" in res_detail.data
    assert b"Self-Check Practice Questions" in res_detail.data

    # Toggle API
    res_api = auth_client.post(f'/api/resources/{r_id}/toggle', json={'action': 'toggle_complete'})
    assert res_api.status_code == 200
    data = res_api.get_json()
    assert data['success'] is True

def test_normalize_category():
    assert normalize_category(None) == 'All'
    assert normalize_category('') == 'All'
    assert normalize_category('All') == 'All'
    assert normalize_category('all') == 'All'
    assert normalize_category('Interview Preparation') == 'Interview Preparation'
    assert normalize_category({'name': 'Interview Preparation', 'count': 1}) == 'Interview Preparation'
    assert normalize_category("{'name': 'Interview Preparation', 'count': 1}") == 'Interview Preparation'
    assert normalize_category('{"name": "Operating Systems", "count": 1}') == 'Operating Systems'

def test_resources_catalog_category_filtering(auth_client, app):
    categories = [
        'Programming Languages',
        'Artificial Intelligence and Machine Learning',
        'Computer Science Fundamentals',
        'Mathematics and Aptitude',
        'Web Development',
        'Database Management',
        'Operating Systems',
        'Computer Networks',
        'Interview Preparation',
        'Other Academic Subjects'
    ]
    for cat in categories:
        res = auth_client.get(f'/resources?category={cat}')
        assert res.status_code == 200
        html = res.data.decode('utf-8')
        # Ensure values in option and href are clean string names, not dicts
        assert "value=\"{'name'" not in html
        assert "href=\"/resources?category=%7B" not in html
        assert f'value="{cat}"' in html

def test_resources_catalog_malformed_category_string(auth_client):
    # Regression test for observed bug where URL contains stringified dictionary
    malformed_url = "/resources?category={'name': 'Interview Preparation', 'count': 1}"
    res = auth_client.get(malformed_url)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Technical Interview Mastery" in html
    assert 'value="Interview Preparation" selected' in html
    assert 'href="/resources?category=Interview+Preparation"' in html


def test_resources_catalog_both_learning_sections(auth_client, app):
    """
    Focused regression test verifying both learning sections:
    1. College Semester Learning displays its resources.
    2. Competitive Exam Preparation displays its resources.
    """
    with app.app_context():
        from services.resource_service import get_learning_sections

        # Check section counts helper
        counts = get_learning_sections()
        assert counts['all'] >= 10
        assert counts['college'] >= 9
        assert counts['competitive'] >= 1

        # 1. College Semester Learning service query
        college_res = get_resources(category='College Semester Learning')
        assert len(college_res) >= 9
        assert all(r['learning_section'] == 'College Semester Learning' for r in college_res)
        assert any("Pointers" in r['title'] for r in college_res)

        # 2. Competitive Exam Preparation service query
        comp_res = get_resources(category='Competitive Exam Preparation')
        assert len(comp_res) >= 1
        assert all(r['learning_section'] == 'Competitive Exam Preparation' for r in comp_res)
        assert any("Quantitative Aptitude" in r['title'] or "Aptitude" in r['subject'] for r in comp_res)

        # 3. Querying by section parameter directly
        sec_college = get_resources(section='college')
        assert len(sec_college) >= 9
        sec_comp = get_resources(section='competitive')
        assert len(sec_comp) >= 1

        # 4. Querying by competitive category name directly
        quant_res = get_resources(category='Quantitative Aptitude')
        assert len(quant_res) >= 1
        assert quant_res[0]['subject'] == 'Quantitative Aptitude'

    # 5. HTTP route test for College Semester Learning
    res_college = auth_client.get('/resources?category=College+Semester+Learning')
    assert res_college.status_code == 200
    html_college = res_college.data.decode('utf-8')
    assert "No Matching Resources Found" not in html_college
    assert "Mastering C Pointers" in html_college or "C++ Object-Oriented Design" in html_college

    # 6. HTTP route test for Competitive Exam Preparation
    res_comp = auth_client.get('/resources?category=Competitive+Exam+Preparation')
    assert res_comp.status_code == 200
    html_comp = res_comp.data.decode('utf-8')
    assert "No Matching Resources Found" not in html_comp
    assert "High-Yield Quantitative Aptitude Formulas" in html_comp
    assert "Competitive Exam Preparation" in html_comp

    # 7. HTTP route test for section=competitive and section=college
    res_sec_comp = auth_client.get('/resources?section=competitive')
    assert res_sec_comp.status_code == 200
    assert b"High-Yield Quantitative Aptitude Formulas" in res_sec_comp.data

    res_sec_college = auth_client.get('/resources?section=college')
    assert res_sec_college.status_code == 200
    assert b"Mastering C Pointers" in res_sec_college.data or b"Operating Systems" in res_sec_college.data
