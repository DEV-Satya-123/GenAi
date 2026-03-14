import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_PATH = os.getenv("REPO_PATH", ".")
BRANCH_TO_MONITOR = os.getenv("BRANCH_TO_MONITOR", "main")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
