from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Config(BaseSettings):
    TAAPI_KEY: str
    NEWS_API_KEY: str
    MORALIS_API_KEY: str
    OPENAI_API_KEY: str
    MONGO_URI: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Config()

if not all([config.TAAPI_KEY, config.NEWS_API_KEY, config.MORALIS_API_KEY, config.OPENAI_API_KEY, config.MONGO_URI]):
    raise ValueError("❌ Error: Could not load API keys! Check .env file")

print("✅ Successfully loaded .env Keys")
