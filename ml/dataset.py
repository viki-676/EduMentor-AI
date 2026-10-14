"""
Synthetic Benchmark Dataset Generator for EduMentor AI.

DISCLOSURE & TRANSPARENCY:
This dataset is synthetically generated for demonstration, prototyping, and academic evaluation
in the absence of long-term real student logs. It does NOT represent real student observations.
Features and relationships are modeled after standard cognitive educational metrics:
- avg_score_past: Historical score percentage (0-100)
- quizzes_attempted: Volume of practice sessions (1-50)
- time_per_question: Speed/pace in seconds (10-120s)
- difficulty_level: Numerical index (1=Easy, 2=Medium, 3=Hard)
- consistency_score: Active study cadence index (1-10)

Target variable:
- needs_intervention (1 = Student at risk of scoring < 60%, 0 = Proficient / On Track)
"""

import numpy as np
import pandas as pd

def generate_synthetic_student_data(n_samples: int = 500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate a labeled synthetic dataset with realistic correlations.
    """
    np.random.seed(random_seed)

    avg_score_past = np.random.normal(loc=65.0, scale=18.0, size=n_samples)
    avg_score_past = np.clip(avg_score_past, 20.0, 98.0)

    quizzes_attempted = np.random.poisson(lam=12, size=n_samples)
    quizzes_attempted = np.clip(quizzes_attempted, 1, 60)

    time_per_question = np.random.normal(loc=45.0, scale=15.0, size=n_samples)
    time_per_question = np.clip(time_per_question, 10.0, 120.0)

    difficulty_level = np.random.choice([1, 2, 3], size=n_samples, p=[0.3, 0.5, 0.2])
    consistency_score = np.random.randint(1, 11, size=n_samples)

    # Probabilistic logic for target outcome
    # Lower score, high difficulty, low consistency increase probability of needing intervention
    latent_risk = (
        - 0.05 * avg_score_past
        - 0.04 * quizzes_attempted
        + 0.6 * difficulty_level
        + 0.01 * time_per_question
        - 0.15 * consistency_score
        + 1.5
    )

    prob_risk = 1.0 / (1.0 + np.exp(-latent_risk))
    needs_intervention = (np.random.uniform(0, 1, size=n_samples) < prob_risk).astype(int)

    df = pd.DataFrame({
        'avg_score_past': np.round(avg_score_past, 2),
        'quizzes_attempted': quizzes_attempted,
        'time_per_question': np.round(time_per_question, 1),
        'difficulty_level': difficulty_level,
        'consistency_score': consistency_score,
        'needs_intervention': needs_intervention
    })

    return df
