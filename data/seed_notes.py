"""
Sample initial starter notes for students in EduMentor AI.
"""

from models import db, Note, User

STARTER_NOTES = [
    {
        'title': 'Python Memory Model & The Global Interpreter Lock (GIL)',
        'subject': 'Python Programming',
        'topic': 'Memory Management',
        'tags': 'python, memory, gil, multithreading',
        'source': 'manual',
        'content': """### Python Memory Management Highlights:
- **Reference Counting:** Every Python object maintains an `ob_refcnt`. When it drops to 0, memory is immediately reclaimed.
- **Cyclic Garbage Collector:** Detects circular references (e.g., list containing itself) that reference counting alone cannot free.
- **GIL (Global Interpreter Lock):** A mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes simultaneously in CPython.
- **Consequence:** For CPU-bound tasks, use `multiprocessing` instead of `threading`. For I/O-bound tasks, `threading` or `asyncio` works great!"""
    },
    {
        'title': 'B+ Trees vs. Hash Indexes in RDBMS',
        'subject': 'DBMS',
        'topic': 'Indexing & Optimization',
        'tags': 'dbms, sql, indexing, btree',
        'source': 'resource',
        'content': """### Choosing the Right Index:
1. **B+ Tree Index (Default):**
   - Keeps data sorted in leaf nodes connected by pointers.
   - Time complexity: $O(\\log N)$ for search, insert, delete.
   - **Supports Range Queries:** `WHERE age BETWEEN 20 AND 30` or `ORDER BY salary`.
2. **Hash Index:**
   - Uses hash table buckets.
   - Time complexity: $O(1)$ point lookups.
   - **Does NOT support range queries** or prefix matching (e.g. `LIKE 'A%'`).
3. **Rule of Thumb:**
   - Always index foreign keys and columns frequently used in `JOIN` conditions."""
    },
    {
        'title': 'Big-O Algorithmic Time & Space Complexity Reference',
        'subject': 'Data Structures',
        'topic': 'Complexity Analysis',
        'tags': 'dsa, algorithms, big-o, cheat-sheet',
        'source': 'ai_mentor',
        'content': """### Complexity Hierarchy (Fastest to Slowest):
$O(1) < O(\\log N) < O(N) < O(N \\log N) < O(N^2) < O(2^N) < O(N!)$

### Common Data Structure Operations:
- **Hash Table:** Average $O(1)$ search/insert; Worst $O(N)$ with hash collisions.
- **Binary Search Tree (Balanced AVL/Red-Black):** $O(\\log N)$ search/insert.
- **Array:** $O(1)$ lookup by index; $O(N)$ arbitrary insertion/deletion.
- **Linked List:** $O(N)$ search; $O(1)$ insertion at head."""
    },
    {
        'title': 'Operating System Deadlocks & Prevention Rules',
        'subject': 'Operating Systems',
        'topic': 'Process Synchronization',
        'tags': 'os, deadlocks, coffman, concurrency',
        'source': 'manual',
        'content': """### 4 Coffman Conditions for Deadlock:
All four must hold simultaneously for a deadlock to occur:
1. **Mutual Exclusion:** At least one non-shareable resource.
2. **Hold and Wait:** A process holds one resource while waiting for another.
3. **No Preemption:** Resources cannot be forcibly seized.
4. **Circular Wait:** Closed chain of processes each waiting for the next.

### Prevention Strategy:
- Break any **one** of the four conditions (e.g. impose total ordering on resource allocation IDs to eliminate circular wait)."""
    }
]

def seed_sample_notes_for_user(database, user_id):
    """
    Seeds initial starter notes for a newly registered student if they have 0 notes.
    """
    existing_count = Note.query.filter_by(user_id=user_id).count()
    if existing_count > 0:
        return

    for n in STARTER_NOTES:
        note = Note(
            user_id=user_id,
            title=n['title'],
            subject=n['subject'],
            topic=n['topic'],
            tags=n['tags'],
            source=n['source'],
            content=n['content'],
            is_bookmarked=True
        )
        database.session.add(note)

    database.session.commit()
