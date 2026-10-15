import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env if present
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_sqlite_uri(custom_url=None):
    """
    Safely resolve SQLite database URI for cross-platform compatibility
    (Windows local development and Render/Linux deployment).
    """
    if custom_url and not custom_url.startswith('sqlite:///'):
        return custom_url

    if custom_url and custom_url.startswith('sqlite:///'):
        raw = custom_url[len('sqlite:///'):]
        if raw.startswith('/') or (len(raw) > 2 and raw[1] == ':'):
            abs_path = raw
        else:
            abs_path = os.path.join(BASE_DIR, raw)
    else:
        abs_path = os.path.join(BASE_DIR, 'instance', 'edumentor.db')

    # Ensure parent directory exists before SQLite tries to connect
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    except OSError:
        pass

    # Normalize backslashes to forward slashes for cross-platform SQLite URI
    norm_path = os.path.abspath(abs_path).replace('\\', '/')
    return f"sqlite:///{norm_path}"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'edumentor-super-secure-dev-key-2026')
    SQLALCHEMY_DATABASE_URI = get_sqlite_uri(os.environ.get('DATABASE_URL'))
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
    TESTING = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
