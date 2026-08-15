import os
import shutil
from pathlib import Path

# ── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect Vercel environment
IS_VERCEL = os.getenv("VERCEL") == "1" or "VERCEL" in os.environ

if IS_VERCEL:
    DB_PATH = Path("/tmp/airline.db")
    INITIAL_DB = BASE_DIR / "airline.db"
    if INITIAL_DB.exists() and not DB_PATH.exists():
        try:
            shutil.copy2(INITIAL_DB, DB_PATH)
        except Exception as e:
            print(f"Error copying database to /tmp: {e}")
else:
    DB_PATH = BASE_DIR / "airline.db"

# ── Database ───────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# ── JWT / Auth ─────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "airline-reservation-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ── Rate Limiting ──────────────────────────────────────
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
