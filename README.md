# EduMentor AI 🎓
### An AI-Powered Personalized Learning & Competitive Exam Preparation System
---
## 📌 Project Overview
**EduMentor AI** is a responsive educational web application built for college students and competitive exam aspirants. It addresses learning gaps by providing calibrated practice quizzes, identifying weak topics (&lt;60% accuracy), delivering actionable personalized study plans, and offering an autonomous **AI Mentor Agent**—entirely running locally on Windows with **zero paid third-party API dependencies**.
---
## 🛠️ Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Backend**: Python 3.14+, Flask 3.1
- **Database**: SQLite with Flask-SQLAlchemy (ORM)
- **Machine Learning**: Scikit-Learn, Pandas, NumPy
- **Visualizations**: Chart.js 4.4
- **Testing**: pytest 9.1
- **OS**: Windows (PowerShell compatible)
---
## 🎯 Two Targeted Learning Paths
### 💻 Path A — College Learning
Designed for **B.Tech, BCA, B.Sc. (Computer Science)** and degree students for semester exams and campus placement prep:
1. **Python Programming**: Variables, data types, scoping rules, mutability, functions, OOP, and MRO.
2. **Data Structures**: Arrays, Stacks, Queues, Linked Lists (Floyd's algorithm), BST, traversal, and Big-O complexities.
3. **Database Management Systems (DBMS)**: Relational model, Keys, SQL queries, Joins, Normalization (1NF to BCNF), and ACID transactions.

### 🏆 Path B — Competitive Exam Preparation
Designed for aspirants appearing for **SSC (CGL/CHSL), Railway (RRB), Banking (IBPS/SBI), UPSC Civil Services Aptitude, and State PSCs**:
1. **Quantitative Aptitude**: Percentages, Profit & Loss, Ratio & Proportion, Time & Work, Speed, HCF & LCM.
2. **Logical Reasoning**: Number & Letter Series, Coding-Decoding, Blood Relations, Syllogisms, Direction Sense.
3. **English Language**: Error Spotting, Conditional Grammar, Vocabulary (Synonyms/Antonyms), Idioms & Phrases.
4. **General Awareness**: Indian Polity & Constitution (Article 32, DPSPs), Modern Indian History, Geography, Economy (RBI), and Science.
---
## 📂 Project Structure

```text
EduMentorAI/
├── app.py                      # Application factory and route controllers
├── config.py                   # Development, testing, and production configuration
├── requirements.txt            # Pinned dependencies
├── .env.example                # Sample environment variables
├── .gitignore                  # Git ignore rules
├── models/
│   ├── __init__.py             # SQLAlchemy instance and model exports
│   ├── user.py                 # User model, password hashing, preferences
│   ├── learning.py             # Subjects, topics, categories, exam catalogs
│   └── quiz.py                 # Question, QuizAttempt, StudentAnswer, Recommendation
├── services/
│   ├── __init__.py
│   ├── auth_service.py         # Registration, authentication, session security
│   ├── quiz_service.py         # Question sampling, attempt grading, analytics
│   ├── recommendation.py       # Rule-based weak topic detection & study plans
│   └── ai_mentor.py            # Local AI Mentor knowledge base and response generator
├── ml/
│   ├── __init__.py
│   ├── dataset.py              # Synthetic benchmark student dataset generator
│   └── performance_predictor.py# Scikit-Learn ML pipeline, baseline evaluation, risk predictor
├── data/
│   └── seed_questions.py       # 56 calibrated MCQs with explanations
├── static/
│   ├── css/
│   │   └── styles.css          # Navy, Blue, Teal theme, custom components
│   └── js/
│       ├── main.js             # Alert auto-dismissal, tooltips
│       ├── quiz.js             # Countdown timer, progress tracker, submit validation
│       ├── dashboard.js        # Chart.js line and bar charts
│       └── mentor.js           # Interactive AI mentor chat client
├── templates/
│   ├── base.html               # Shared layout, navbar, flash messages, footer
│   ├── index.html              # Modern landing page
│   ├── auth/
│   │   ├── login.html          # Secure login
│   │   └── register.html       # Student registration with path selection
│   ├── paths/
│   │   ├── select_path.html    # Learning track switcher
│   │   ├── college_dashboard.html # College subjects dashboard
│   │   └── competitive_dashboard.html # Competitive categories & exam filter
│   ├── quiz/
│   │   ├── quiz_view.html      # Interactive quiz interface with timer
│   │   └── result_view.html    # Question breakdown & detailed explanations
│   ├── dashboard/
│   │   └── student_dashboard.html # Chart.js analytics, weak topics, ML card
│   └── mentor/
│       └── mentor_view.html    # Autonomous AI Mentor conversational interface
├── tests/
│   ├── conftest.py             # Pytest fixtures and in-memory test database
│   ├── test_auth.py            # Registration, hashing, session security tests
│   ├── test_quiz.py            # Quiz sampling, grading, isolation tests
│   ├── test_recommendations.py # Analytics and study plan tests
│   ├── test_ml.py              # ML pipeline, metrics, prediction tests
│   └── test_ai_mentor.py       # Concept lookup and chat API tests
└── docs/
    └── REPORT.md               # Full project report, diagrams, viva Q&A, Lean Canvas
```
---
## 🚀 Quick Start Guide (Windows PowerShell)
### Step 1: Open PowerShell in Project Directory
Ensure you are in the project folder:
```powershell
cd c:\Users\Hp\Downloads\EduMentorAI
```
### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```
### Step 3: Run Test Suite
Verify that all 15 unit and integration tests pass:
```powershell
python -m pytest -v
```
### Step 4: Start the Flask Application
```powershell
python app.py
```
Output will show:
```text
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```
### Step 5: Open in Your Browser
Navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
---
## 🧪 Testing the Complete Workflow
1. **Register an Account**: Click **"Get Started Free"**, enter your details (e.g. `Rahul Sharma`, username: `rahul`, password: `password123`), choose **College Track** or **Competitive Exam**.
2. **Take a Quiz**:
   - Go to **College Learning** → Click **"Start Practice Quiz"** under Python Programming or DBMS.
   - Or go to **Competitive Exams** → Select **SSC / Banking / Railway** → Start a 5-minute timed drill in Quantitative Aptitude.
3. **Submit and Review**:
   - Answer the MCQs and click **"Submit & View Results"**.
   - Review your percentage score, time taken, and the **detailed conceptual explanations** for every question.
4. **Inspect Student Dashboard**:
   - Navigate to **"Dashboard"** to see your **Score Progression Trend (Chart.js)** and **Topic Mastery**.
   - Review your **Scikit-Learn ML Risk Assessment** and priority-ranked **Personalized Action Plan**.
5. **Chat with AI Mentor**:
   - Click **"AI Mentor"** from the navigation bar.
   - Click any prompt chip (e.g., *"Explain Python mutability"* or *"How am I doing?"*) or ask custom questions.
---
## 🤖 Machine Learning Model Details
- **Module**: `ml/performance_predictor.py`
- **Target Variable**: `needs_intervention` (Binary classification: `1` = At Risk / Needs Intervention, `0` = On Track / Proficient).
- **Features**: Historical average score, quiz practice volume, average time per question, question difficulty level, and study consistency score.
- **Data Disclosure**: Demonstrative synthetic benchmark dataset (600 samples) cleanly partitioned into a 75% train / 25% test split (`random_state=42`) with zero data leakage.
- **Evaluation Metrics (Unseen Test Set)**:
  - **Baseline Accuracy (`DummyClassifier`)**: ~74.7%
  - **Model Accuracy (`LogisticRegression` + `StandardScaler`)**: ~76.7%
  - **Precision**: 56.0% | **Recall**: 36.8% | **F1-Score**: 0.444
- **Fallback**: Rule-based pedagogical recommendations serve as the reliable primary guidance engine.
---
## 🔒 Security & Best Practices
- **Password Hashing**: Uses Werkzeug's `generate_password_hash` with secure PBKDF2/SHA256 salt. Plaintext passwords are never stored.
- **Access Control**: Users can only access their own quiz results; attempts belonging to other user IDs are blocked.
- **Input Validation**: Enforces minimum lengths, unique email/username constraints, and type coercion.
---
## 📜 Academic Attribution
- Designed and verified for academic submission and technical viva voce presentations.