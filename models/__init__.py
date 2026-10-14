from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .quiz import Question, QuizAttempt, StudentAnswer, Recommendation
from .resource import LearningResource, ResourceProgress
from .note import Note
from .planner import StudyPlan, StudyTask
from .pyq import PYQPaper, PreviousYearQuestion
from .bookmark import Bookmark
from .mentor import MentorConversation, MentorMessage

__all__ = [
    'db', 'User', 'Question', 'QuizAttempt', 'StudentAnswer', 'Recommendation',
    'LearningResource', 'ResourceProgress', 'Note', 'StudyPlan', 'StudyTask',
    'PYQPaper', 'PreviousYearQuestion', 'Bookmark', 'MentorConversation', 'MentorMessage'
]
