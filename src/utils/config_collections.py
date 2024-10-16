import os

from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(filename=".env", raise_error_if_not_found=True), verbose=True)


@dataclass
class APIConfigProvider:
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    news_api_base_url: str = os.getenv("NEWS_API_URL", "https://newsapi.org/v2")


@dataclass
class MongoDbConfigProvider:
    mongo_uri: str = os.getenv("MONGO_URI", "localhost")
    mongo_db: str = os.getenv("MONGO_DB", "news")
    mongo_collection: str = os.getenv("MONGO_COLLECTION", "top_headlines")
    mongo_port: int = int(os.getenv("MONGO_PORT", "27017"))
    mongo_username: str = os.getenv("MONGO_USERNAME", "")
    mongo_password: str = os.getenv("MONGO_PASSWORD", "")
