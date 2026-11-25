import os

# =========================
# FMStar Server Configuration
# =========================

APP_NAME = "FMStar AI Studio"
APP_VERSION = "1.0.0"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Server
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))

# API
API_PREFIX = "/api/v1"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "")

# CORS
ALLOWED_ORIGINS = [
    "https://fefeana.github.io",
]

# AI Providers
OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "")
OMNIROUTE_API_KEY = os.getenv("OMNIROUTE_API_KEY", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")

# Jobs
JOB_TIMEOUT_SECONDS = 1800
MAX_CONCURRENT_JOBS = 3

# Uploads
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_MB = 50

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Models
DEFAULT_CHAT_MODEL = os.getenv(
    "DEFAULT_CHAT_MODEL",
    "gemini-2.5-flash"
)

# Health
HEALTH_ENDPOINT = f"{API_PREFIX}/health"

# Rate Limit
RATE_LIMIT_PER_MINUTE = 60
