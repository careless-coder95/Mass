import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "vault.db")

# Security
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# MongoDB (Optional)
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "telegram_vault")

# Validate required config
if not BOT_TOKEN or not API_ID or not API_HASH:
    raise ValueError("BOT_TOKEN, API_ID, and API_HASH must be set in .env file")

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY must be set in .env file")

# Session folder for temporary client sessions
SESSION_FOLDER = "sessions"
os.makedirs(SESSION_FOLDER, exist_ok=True)
