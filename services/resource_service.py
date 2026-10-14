"""
Learning Resources service for querying, searching, filtering, and tracking reading progress.
"""

from datetime import datetime, timezone
from models import db, LearningResource, ResourceProgress, Bookmark

COMPETITIVE_DOMAINS = [
    'Mathematics and Aptitude',
    'Quantitative Aptitude',
    'Logical Reasoning',
    'English Language',
    'General Awareness'
]

COLLEGE_DOMAINS = [
    'Programming Languages',
    'Artificial Intelligence and Machine Learning',
    'Computer Science Fundamentals',
    'Web Development',
    'Database Management',
    'Operating Systems',
    'Computer Networks',
    'Interview Preparation',
    'Other Academic Subjects'
]

def get_learning_sections():
    """Return resource counts for high-level learning tracks."""
    comp_count = len(get_resources(section='competitive'))
    college_count = len(get_resources(section='college'))
    total_count = LearningResource.query.count()
    return {
        'all': total_count,
        'college': college_count,
        'competitive': comp_count
    }

def get_resource_categories():
    """Return distinct categories and resource counts."""
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
    result = []
    for cat in categories:
        cnt = LearningResource.query.filter(
            (LearningResource.category.ilike(cat)) | (LearningResource.subject.ilike(cat))
        ).count()
        result.append({
            'name': cat,
            'count': cnt
        })
    return result

def normalize_category(category):
    """
    Normalize category parameter whether passed as dict, stringified dict, or plain string.
    Returns clean category string or 'All'.
    """
    if not category:
        return 'All'
    if isinstance(category, dict):
        return category.get('name', 'All')
    category_str = str(category).strip()
    if not category_str or category_str.lower() == 'all':
        return 'All'
    if category_str.startswith('{') and 'name' in category_str:
        import ast, json, re
        try:
            val = ast.literal_eval(category_str)
            if isinstance(val, dict) and 'name' in val:
                return str(val['name']).strip()
        except Exception:
            pass
        try:
            val = json.loads(category_str)
            if isinstance(val, dict) and 'name' in val:
                return str(val['name']).strip()
        except Exception:
            pass
        match = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", category_str)
        if match:
            return match.group(1).strip()
    return category_str

def get_resources(category=None, difficulty=None, search=None, user_id=None, section=None):
    """
    Search and filter resources with user completion and bookmark metadata.
    Supports filtering by category, difficulty, search keyword, and learning section (college / competitive).
    """
    query = LearningResource.query

    category = normalize_category(category)
    cat_lower = category.lower() if category else 'all'
    sec_lower = (section or '').strip().lower()

    # Determine if section-level filtering is requested
    is_competitive = (
        sec_lower in ['competitive', 'competitive exam preparation', 'competitive prep', 'path b'] or
        cat_lower in ['competitive', 'competitive exam preparation', 'competitive prep', 'competitive track']
    )
    is_college = (
        sec_lower in ['college', 'college semester learning', 'college learning', 'path a'] or
        cat_lower in ['college', 'college semester learning', 'college learning', 'college track']
    )

    if is_competitive:
        query = query.filter(
            (LearningResource.category.ilike('%Mathematics and Aptitude%')) |
            (LearningResource.category.ilike('%Competitive%')) |
            (LearningResource.subject.ilike('%Quantitative Aptitude%')) |
            (LearningResource.subject.ilike('%Logical Reasoning%')) |
            (LearningResource.subject.ilike('%English Language%')) |
            (LearningResource.subject.ilike('%General Awareness%'))
        )
    elif is_college:
        query = query.filter(
            ~(
                (LearningResource.category.ilike('%Mathematics and Aptitude%')) |
                (LearningResource.category.ilike('%Competitive%')) |
                (LearningResource.subject.ilike('%Quantitative Aptitude%')) |
                (LearningResource.subject.ilike('%Logical Reasoning%')) |
                (LearningResource.subject.ilike('%English Language%')) |
                (LearningResource.subject.ilike('%General Awareness%'))
            )
        )
    elif category and cat_lower != 'all':
        # Specific category or subject filter
        # Match against either category column or subject column for maximum flexibility
        query = query.filter(
            (LearningResource.category.ilike(category)) |
            (LearningResource.subject.ilike(category))
        )

    if difficulty and difficulty.lower() != 'all':
        query = query.filter(LearningResource.difficulty.ilike(difficulty.strip()))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (LearningResource.title.ilike(term)) |
            (LearningResource.summary.ilike(term)) |
            (LearningResource.subject.ilike(term)) |
            (LearningResource.topic.ilike(term)) |
            (LearningResource.category.ilike(term))
        )

    resources = query.order_by(LearningResource.order_index.asc(), LearningResource.id.asc()).all()

    # User progress map
    progress_map = {}
    if user_id:
        user_progs = ResourceProgress.query.filter_by(user_id=user_id).all()
        for p in user_progs:
            progress_map[p.resource_id] = {
                'completed': p.is_completed,
                'bookmarked': p.is_bookmarked
            }

    data = []
    for r in resources:
        item = r.to_dict()
        user_info = progress_map.get(r.id, {'completed': False, 'bookmarked': False})
        item['is_completed'] = user_info['completed']
        item['is_bookmarked'] = user_info['bookmarked']
        data.append(item)

    return data

def get_resource_by_slug(slug, user_id=None):
    """Fetch single resource with full concept content and adjacent prev/next topics."""
    resource = LearningResource.query.filter_by(slug=slug).first()
    if not resource:
        return None, None, None

    # Get user progress
    user_prog = None
    if user_id:
        user_prog = ResourceProgress.query.filter_by(user_id=user_id, resource_id=resource.id).first()
        if not user_prog:
            user_prog = ResourceProgress(
                user_id=user_id,
                resource_id=resource.id,
                is_completed=False,
                is_bookmarked=False,
                last_read_at=datetime.now(timezone.utc)
            )
            db.session.add(user_prog)
        else:
            user_prog.last_read_at = datetime.now(timezone.utc)
        db.session.commit()

    # Prev and Next in same category or overall
    prev_res = LearningResource.query.filter(
        LearningResource.category == resource.category,
        LearningResource.order_index < resource.order_index
    ).order_by(LearningResource.order_index.desc()).first()

    next_res = LearningResource.query.filter(
        LearningResource.category == resource.category,
        LearningResource.order_index > resource.order_index
    ).order_by(LearningResource.order_index.asc()).first()

    return resource, prev_res, next_res

def toggle_resource_progress(user_id, resource_id, field='completed'):
    """Toggle completed or bookmarked status."""
    prog = ResourceProgress.query.filter_by(user_id=user_id, resource_id=resource_id).first()
    if not prog:
        prog = ResourceProgress(
            user_id=user_id,
            resource_id=resource_id,
            is_completed=False,
            is_bookmarked=False
        )
        db.session.add(prog)

    resource = db.session.get(LearningResource, resource_id)

    if field == 'completed':
        prog.is_completed = not prog.is_completed
        new_val = prog.is_completed
    elif field == 'bookmarked':
        prog.is_bookmarked = not prog.is_bookmarked
        new_val = prog.is_bookmarked
        # Sync with global Bookmarks table
        if prog.is_bookmarked and resource:
            bm = Bookmark.query.filter_by(user_id=user_id, item_type='resource', item_id=resource_id).first()
            if not bm:
                bm = Bookmark(
                    user_id=user_id,
                    item_type='resource',
                    item_id=resource_id,
                    title=resource.title,
                    subject=resource.subject,
                    url=f"/resources/{resource.slug}"
                )
                db.session.add(bm)
        else:
            Bookmark.query.filter_by(user_id=user_id, item_type='resource', item_id=resource_id).delete()

    db.session.commit()
    return new_val

def toggle_resource_bookmark(user_id, resource_id):
    """Convenience alias for toggling bookmark status on a resource."""
    return toggle_resource_progress(user_id, resource_id, field='bookmarked')

