"""
Personalized Recommendation Engine for EduMentor AI.
Uses transparent pedagogical rule-based logic as a reliable foundation,
with ML integration for performance risk classification.
"""

from models import db, Recommendation, User
from models.learning import COLLEGE_SUBJECTS, COMPETITIVE_CATEGORIES
from .quiz_service import get_user_analytics

# Topic study suggestions and key concepts for actionable guidance
TOPIC_STUDY_TIPS = {
    'Variables & Data Types': 'Review mutable vs. immutable objects (e.g. tuples vs. lists) and memory references.',
    'Control Flow & Loops': 'Practice `for...else` loops, `break`, `continue`, and list comprehensions.',
    'Functions & Scope': 'Carefully review Python LEGB scoping rules and avoid mutable default arguments.',
    'Data Structures (List/Dict/Set)': 'Master dict hash table lookups O(1), set intersections, and deque usage.',
    'Object-Oriented Programming': 'Revise class inheritance, `__init__` vs `__new__`, and C3 MRO linearization.',
    'Arrays & Strings': 'Practice two-pointer techniques, sliding windows, and in-place manipulations.',
    'Stacks & Queues': 'Solve parentheses validation and postfix expression evaluation problems.',
    'Linked Lists': 'Master Floyd’s fast-and-slow pointer cycle detection and linked list reversal.',
    'Binary Trees & BST': 'Review recursion patterns for In-order, Pre-order, and Post-order BST traversals.',
    'Sorting & Searching Algorithms': 'Focus on Merge Sort O(n log n) divide-and-conquer and binary search boundary conditions.',
    'Relational Model & Keys': 'Distinguish candidate keys, primary keys, and foreign keys referential integrity.',
    'SQL Queries & Joins': 'Practice difference between WHERE and HAVING, and visualize LEFT/INNER joins.',
    'Normalization & Normal Forms': 'Understand 1NF atomic values, 2NF partial dependencies, and 3NF/BCNF determinants.',
    'Transactions & ACID Properties': 'Revisit dirty reads, non-repeatable reads, and serializable isolation levels.',
    'Percentages & Averages': 'Memorize fractional equivalents (e.g. 1/6 = 16.67%, 1/8 = 12.5%) for 2x faster mental math.',
    'Profit, Loss & Discount': 'Use cost price ratio method: SP = CP * (100 + P)/100 and effective discount chaining.',
    'Ratio & Proportion': 'Practice combining ratios A:B and B:C by finding common multiples.',
    'Time, Speed & Work': 'Use unitary LCM method for work efficiency and 5/18 conversion for km/h to m/s.',
    'Number System & HCF/LCM': 'Apply property: Product of two numbers = HCF * LCM.',
    'Series & Analogy': 'Test differences, double differences, prime steps, and multiplication + constant patterns.',
    'Coding & Decoding': 'Write alphabet index numbers (A=1...Z=26) and look for forward/backward shift symmetry.',
    'Blood Relations': 'Draw family tree diagrams with gender notation (+ for male, - for female).',
    'Syllogism & Deductive Logic': 'Use standard Venn diagram circles or tick-cross method for universal and particular premises.',
    'Direction & Seating Arrangement': 'Plot cardinal directions N-S-E-W and solve step-by-step from anchor positions.',
    'Error Spotting & Grammar': 'Check subject-verb agreement (e.g. "each of" takes singular verb) and conditional tenses.',
    'Vocabulary (Synonyms & Antonyms)': 'Learn root words, prefixes, suffixes, and contextual connotation.',
    'Indian Polity & Constitution': 'Review Articles 12-35 (Fundamental Rights) and constitutional amendment provisions.',
    'Modern Indian History': 'Create a chronological timeline of key freedom movement milestones (1857-1947).'
}

def generate_personalized_recommendations(user_id):
    """
    Generate actionable study recommendations based on user's quiz performance history.
    Returns:
        dict: {
            'weak_topics': list,
            'study_plan': list of daily/session action items,
            'suggested_next_quiz': dict,
            'readiness_level': str ('Beginner', 'Developing', 'Proficient', 'Exam-Ready')
        }
    """
    analytics = get_user_analytics(user_id)
    user = db.session.get(User, user_id)
    
    weak_topics = analytics.get('weak_topics', [])
    total_quizzes = analytics.get('total_quizzes', 0)
    overall_accuracy = analytics.get('overall_accuracy', 0.0)

    # Determine Readiness Tier
    if total_quizzes == 0:
        readiness_level = "Getting Started"
        readiness_badge = "info"
        readiness_percent = 10
    elif overall_accuracy < 50:
        readiness_level = "Needs Foundation Review"
        readiness_badge = "warning"
        readiness_percent = 35
    elif overall_accuracy < 75:
        readiness_level = "Developing Proficiency"
        readiness_badge = "primary"
        readiness_percent = 65
    else:
        readiness_level = "Exam-Ready & Consistent"
        readiness_badge = "success"
        readiness_percent = 90

    # Build Structured Study Plan
    study_plan = []
    
    if total_quizzes == 0:
        # User has no history yet: create initial diagnostic plan
        if user and user.learning_path == 'competitive':
            study_plan.append({
                'day': 'Step 1: Baseline Assessment',
                'title': 'Attempt Quantitative Aptitude Diagnostic',
                'category': 'Quantitative Aptitude',
                'description': 'Take your first 5-question quiz to establish your baseline score in fundamental arithmetic.',
                'action_type': 'quiz',
                'estimated_minutes': 10
            })
            study_plan.append({
                'day': 'Step 2: Reasoning Logic',
                'title': 'Attempt Logical Reasoning Basics',
                'category': 'Logical Reasoning',
                'description': 'Test your pattern recognition, series, and analogy solving skills.',
                'action_type': 'quiz',
                'estimated_minutes': 10
            })
        else:
            study_plan.append({
                'day': 'Step 1: Core Fundamentals',
                'title': 'Python Programming Diagnostic',
                'category': 'Python Programming',
                'description': 'Take a short 5-question quiz on variables, loops, and data structures to uncover initial weak spots.',
                'action_type': 'quiz',
                'estimated_minutes': 10
            })
            study_plan.append({
                'day': 'Step 2: Data Structures Review',
                'title': 'Arrays & Linked Lists Assessment',
                'category': 'Data Structures',
                'description': 'Assess memory layout, pointers, and time complexities.',
                'action_type': 'quiz',
                'estimated_minutes': 10
            })
    else:
        # User has quiz data: target identified weaknesses
        for idx, weak in enumerate(weak_topics[:4]):
            topic_name = weak['topic']
            tip = TOPIC_STUDY_TIPS.get(topic_name, 'Review core definitions, work through 3 solved examples, and re-test.')
            study_plan.append({
                'day': f"Priority {idx + 1}",
                'title': f"Strengthen: {topic_name}",
                'category': weak.get('subject', 'Core Topic'),
                'description': tip,
                'accuracy': weak['accuracy'],
                'action_type': 'revision',
                'estimated_minutes': 20
            })

        # Add consolidation step
        if not weak_topics:
            study_plan.append({
                'day': 'Consolidation',
                'title': 'Maintain Speed & Endurance',
                'category': 'All Subjects',
                'description': 'You have maintained high accuracy (>75%) across your attempted topics! Take timed practice tests to enhance speed.',
                'action_type': 'quiz',
                'estimated_minutes': 25
            })

    # Suggested Next Quiz Target
    suggested_quiz = {}
    if weak_topics:
        suggested_quiz = {
            'subject_or_category': weak_topics[0].get('subject', 'Core Topic'),
            'topic': weak_topics[0]['topic'],
            'reason': f"Your accuracy in this topic is currently {weak_topics[0]['accuracy']}%. Dedicated practice will rapidly raise your score."
        }
    else:
        if user and user.learning_path == 'competitive':
            suggested_quiz = {
                'subject_or_category': 'Quantitative Aptitude',
                'topic': 'All Topics',
                'reason': 'Take a comprehensive mixed quiz to test speed and multi-topic agility.'
            }
        else:
            suggested_quiz = {
                'subject_or_category': 'Python Programming',
                'topic': 'All Topics',
                'reason': 'Reinforce object-oriented programming and data structures with a targeted review quiz.'
            }

    return {
        'readiness_level': readiness_level,
        'readiness_badge': readiness_badge,
        'readiness_percent': readiness_percent,
        'weak_topics': weak_topics,
        'study_plan': study_plan,
        'suggested_next_quiz': suggested_quiz,
        'total_quizzes': total_quizzes,
        'overall_accuracy': overall_accuracy
    }
