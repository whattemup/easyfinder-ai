import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "mock_key")
FROM_EMAIL = os.getenv("FROM_EMAIL", "demo@easyfinder.ai")
APP_ENV = os.getenv("APP_ENV", "local")

# Mock mode for testing without real SendGrid
MOCK_EMAIL_MODE = True
