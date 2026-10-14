"""
Constants and catalog for EduMentor AI learning paths.
"""

COLLEGE_SUBJECTS = {
    'Python Programming': {
        'icon': 'bi-code-slash',
        'description': 'Master core Python syntax, OOP, functions, data structures, and algorithmic logic.',
        'topics': [
            'Variables & Data Types',
            'Control Flow & Loops',
            'Functions & Scope',
            'Data Structures (List/Dict/Set)',
            'Object-Oriented Programming'
        ]
    },
    'Data Structures': {
        'icon': 'bi-diagram-3',
        'description': 'Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, and algorithmic complexity.',
        'topics': [
            'Arrays & Strings',
            'Stacks & Queues',
            'Linked Lists',
            'Binary Trees & BST',
            'Sorting & Searching Algorithms'
        ]
    },
    'Database Management Systems (DBMS)': {
        'icon': 'bi-database-fill-gear',
        'description': 'Relational data models, SQL queries, normalization, ACID properties, and transactions.',
        'topics': [
            'Relational Model & Keys',
            'SQL Queries & Joins',
            'Normalization & Normal Forms',
            'Transactions & ACID Properties',
            'Indexing & Views'
        ]
    }
}

COMPETITIVE_EXAMS = {
    'SSC': {
        'title': 'Staff Selection Commission (CGL / CHSL)',
        'badge': 'Government Services',
        'duration_minutes': 15
    },
    'Railway': {
        'title': 'RRB NTPC & Group D',
        'badge': 'Indian Railways',
        'duration_minutes': 15
    },
    'Banking': {
        'title': 'IBPS / SBI PO & Clerk',
        'badge': 'Banking & Financial',
        'duration_minutes': 20
    },
    'UPSC': {
        'title': 'Civil Services Aptitude & GS',
        'badge': 'All India Services',
        'duration_minutes': 20
    },
    'State-level': {
        'title': 'State Public Service Commission',
        'badge': 'State Cadre',
        'duration_minutes': 15
    }
}

COMPETITIVE_CATEGORIES = {
    'Quantitative Aptitude': {
        'icon': 'bi-calculator',
        'description': 'Percentages, Profit & Loss, Ratio & Proportion, Time & Work, Number Systems.',
        'topics': [
            'Percentages & Averages',
            'Profit, Loss & Discount',
            'Ratio & Proportion',
            'Time, Speed & Work',
            'Number System & HCF/LCM'
        ]
    },
    'Logical Reasoning': {
        'icon': 'bi-lightbulb',
        'description': 'Syllogisms, Blood Relations, Coding-Decoding, Series, Direction Sense.',
        'topics': [
            'Series & Analogy',
            'Coding & Decoding',
            'Blood Relations',
            'Syllogism & Deductive Logic',
            'Direction & Seating Arrangement'
        ]
    },
    'English Language': {
        'icon': 'bi-book',
        'description': 'Reading Comprehension, Spotting Errors, Sentence Improvement, Vocabulary.',
        'topics': [
            'Error Spotting & Grammar',
            'Vocabulary (Synonyms & Antonyms)',
            'Sentence Completion & Fillers',
            'Idioms & Phrases',
            'Reading Comprehension'
        ]
    },
    'General Awareness': {
        'icon': 'bi-globe-americas',
        'description': 'Indian Polity, History, Geography, Economy, Science, and Current Affairs.',
        'topics': [
            'Indian Polity & Constitution',
            'Modern Indian History',
            'Geography & Environment',
            'Indian Economy & Budget',
            'General Science & Tech'
        ]
    }
}
