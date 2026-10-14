import json
import html
import re
from datetime import datetime, timezone
from . import db

def render_markdown(text):
    if not text:
        return ""
    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or 'code'
        code = match.group(2).strip()
        escaped_code = html.escape(code)
        display_lang = lang.upper()
        block_html = (
            f'<div class="code-container my-3 rounded-3 overflow-hidden border border-secondary shadow-sm">'
            f'<div class="d-flex justify-content-between align-items-center bg-dark text-light px-3 py-1.5 font-monospace small" style="background-color: #0f172a !important;">'
            f'<span class="badge bg-secondary-subtle text-light small">{display_lang}</span>'
            f'<button type="button" class="btn btn-sm btn-outline-light py-0 px-2" style="font-size: 0.75rem;" onclick="navigator.clipboard.writeText(this.closest(\'.code-container\').querySelector(\'code\').innerText)">'
            f'<i class="bi bi-clipboard"></i> Copy</button>'
            f'</div>'
            f'<pre class="bg-dark text-light p-3 m-0 overflow-x-auto"><code class="language-{lang}">{escaped_code}</code></pre>'
            f'</div>'
        )
        idx = len(code_blocks)
        code_blocks.append(block_html)
        return f"@@CODE_BLOCK_{idx}@@"

    text = re.sub(r'```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```', save_code_block, text)
    lines = text.split('\n')
    output_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if in_ol:
                output_lines.append('</ol>')
                in_ol = False
            if not in_ul:
                output_lines.append('<ul class="mb-3 ps-3">')
                in_ul = True
            item_text = stripped[2:].strip()
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'`([^`]+)`', r'<code class="bg-light text-dark px-1.5 py-0.5 rounded border small">\1</code>', item_text)
            output_lines.append(f'<li class="mb-1">{item_text}</li>')
            continue
        elif re.match(r'^\d+\.\s+', stripped):
            if in_ul:
                output_lines.append('</ul>')
                in_ul = False
            if not in_ol:
                output_lines.append('<ol class="mb-3 ps-3">')
                in_ol = True
            item_text = re.sub(r'^\d+\.\s+', '', stripped).strip()
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'`([^`]+)`', r'<code class="bg-light text-dark px-1.5 py-0.5 rounded border small">\1</code>', item_text)
            output_lines.append(f'<li class="mb-1">{item_text}</li>')
            continue
        else:
            if in_ul:
                output_lines.append('</ul>')
                in_ul = False
            if in_ol:
                output_lines.append('</ol>')
                in_ol = False

        if not stripped:
            continue

        if stripped.startswith('#### '):
            h_text = stripped[5:]
            h_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', h_text)
            output_lines.append(f'<h5 class="fw-bold text-dark mt-4 mb-2">{h_text}</h5>')
        elif stripped.startswith('### '):
            h_text = stripped[4:]
            h_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', h_text)
            output_lines.append(f'<h4 class="fw-bold text-dark mt-4 mb-2">{h_text}</h4>')
        elif stripped.startswith('## '):
            h_text = stripped[3:]
            output_lines.append(f'<h3 class="fw-bold text-dark mt-4 mb-2">{h_text}</h3>')
        elif stripped.startswith('@@CODE_BLOCK_'):
            output_lines.append(stripped)
        else:
            p_text = stripped
            p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_text)
            p_text = re.sub(r'`([^`]+)`', r'<code class="bg-light text-dark px-1.5 py-0.5 rounded border small">\1</code>', p_text)
            output_lines.append(f'<p class="mb-3 text-secondary">{p_text}</p>')

    if in_ul:
        output_lines.append('</ul>')
    if in_ol:
        output_lines.append('</ol>')

    result = '\n'.join(output_lines)
    for idx, block in enumerate(code_blocks):
        result = result.replace(f'@@CODE_BLOCK_{idx}@@', block)

    return result

class LearningResource(db.Model):
    __tablename__ = 'learning_resources'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False, index=True) # e.g., 'Programming Languages'
    subject = db.Column(db.String(100), nullable=False, index=True)  # e.g., 'Python', 'Operating Systems'
    topic = db.Column(db.String(120), nullable=False, index=True)    # e.g., 'Memory Management & Paging'
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='Intermediate', nullable=False) # 'Beginner', 'Intermediate', 'Advanced'
    estimated_reading_minutes = db.Column(db.Integer, default=10, nullable=False)
    prerequisites = db.Column(db.Text, nullable=True) # comma-separated or text
    definitions_json = db.Column(db.Text, nullable=True) # JSON array of {term, definition}
    concepts_markdown = db.Column(db.Text, nullable=False)
    step_by_step_examples = db.Column(db.Text, nullable=True)
    code_examples_json = db.Column(db.Text, nullable=True) # JSON array of {title, language, code, explanation}
    key_points_json = db.Column(db.Text, nullable=True) # JSON array of strings
    common_mistakes_json = db.Column(db.Text, nullable=True) # JSON array of strings
    practice_questions_json = db.Column(db.Text, nullable=True) # JSON array of {question, answer, explanation}
    related_topics = db.Column(db.Text, nullable=True) # comma-separated
    order_index = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user_progress = db.relationship('ResourceProgress', backref='resource', lazy='dynamic', cascade='all, delete-orphan')

    def get_definitions(self):
        try:
            return json.loads(self.definitions_json) if self.definitions_json else []
        except Exception:
            return []

    def get_code_examples(self):
        try:
            return json.loads(self.code_examples_json) if self.code_examples_json else []
        except Exception:
            return []

    def get_key_points(self):
        try:
            return json.loads(self.key_points_json) if self.key_points_json else []
        except Exception:
            return []

    def get_common_mistakes(self):
        try:
            return json.loads(self.common_mistakes_json) if self.common_mistakes_json else []
        except Exception:
            return []

    def get_practice_questions(self):
        try:
            return json.loads(self.practice_questions_json) if self.practice_questions_json else []
        except Exception:
            return []

    @property
    def estimated_read_minutes(self):
        return self.estimated_reading_minutes

    @property
    def content(self):
        """Rendered HTML for concepts_markdown and step_by_step_examples."""
        md = self.concepts_markdown or ''
        if self.step_by_step_examples:
            md = md + '\n\n' + self.step_by_step_examples
        return render_markdown(md)

    @property
    def definitions(self):
        defs = self.get_definitions()
        if isinstance(defs, list):
            res = {}
            for item in defs:
                if isinstance(item, dict) and 'term' in item:
                    res[item['term']] = item.get('definition', '')
            return res
        elif isinstance(defs, dict):
            return defs
        return {}

    @property
    def key_points(self):
        return self.get_key_points()

    @property
    def common_mistakes(self):
        return self.get_common_mistakes()

    @property
    def practice_questions(self):
        return self.get_practice_questions()

    @property
    def code_examples(self):
        return self.get_code_examples()

    @property
    def learning_section(self):
        """Return high-level learning section: 'Competitive Exam Preparation' or 'College Semester Learning'."""
        comp_indicators = {
            'mathematics and aptitude', 'quantitative aptitude',
            'logical reasoning', 'english language', 'general awareness',
            'competitive exam preparation', 'competitive prep', 'competitive'
        }
        cat = (self.category or '').strip().lower()
        sub = (self.subject or '').strip().lower()
        if cat in comp_indicators or sub in comp_indicators:
            return 'Competitive Exam Preparation'
        return 'College Semester Learning'

    @property
    def learning_path(self):
        """Return 'competitive' or 'college' identifier."""
        return 'competitive' if self.learning_section == 'Competitive Exam Preparation' else 'college'

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'subject': self.subject,
            'topic': self.topic,
            'slug': self.slug,
            'title': self.title,
            'summary': self.summary,
            'difficulty': self.difficulty,
            'estimated_reading_minutes': self.estimated_reading_minutes,
            'estimated_read_minutes': self.estimated_reading_minutes,
            'prerequisites': self.prerequisites,
            'related_topics': self.related_topics,
            'practice_questions': self.get_practice_questions(),
            'learning_section': self.learning_section,
            'learning_path': self.learning_path
        }


class ResourceProgress(db.Model):
    __tablename__ = 'resource_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('learning_resources.id', ondelete='CASCADE'), nullable=False, index=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    is_bookmarked = db.Column(db.Boolean, default=False, nullable=False)
    last_read_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_id', name='uq_user_resource_progress'),
    )
