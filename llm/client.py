from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)
