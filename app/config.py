import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "airline.db"

# ── Database ───────────────────────────────────────────
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ── JWT / Auth ─────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "airline-reservation-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ── Rate Limiting ──────────────────────────────────────
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
