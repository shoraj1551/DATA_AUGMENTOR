import os

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    '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'
    )

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-oss-20b"
DEFAULT_ROWS = 50
MAX_ROWS = 1000

# Cache settings
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE = 100  # Maximum number of cached responses
