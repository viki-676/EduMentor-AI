import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env if present
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'edumentor-super-secure-dev-key-2026')
    db_env = os.environ.get('DATABASE_URL')
    if db_env and db_env.startswith('sqlite:///') and not (len(db_env) > 11 and db_env[11] == ':'):
        rel_path = db_env.replace('sqlite:///', '', 1)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, rel_path)}"
    else:
        SQLALCHEMY_DATABASE_URI = db_env or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'edumentor.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama')
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
    OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '120'))
    RISK_DECISION_THRESHOLD = float(os.environ.get('RISK_DECISION_THRESHOLD', '0.50'))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    AI_PROVIDER = 'offline'

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
