import asyncio
from dataclasses import dataclass
from datetime import datetime

from dateutil import parser
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from src.utils.config_collections import MongoDbConfigProvider


@dataclass
class MongoDbNewsSaver:
    mongo_uri: str = MongoDbConfigProvider().mongo_uri
    mongo_db: str = MongoDbConfigProvider().mongo_db
    mongo_collection: str = MongoDbConfigProvider().mongo_collection
    mongo_port: int = MongoDbConfigProvider().mongo_port
    mongo_username: str = MongoDbConfigProvider().mongo_username
    mongo_password: str = MongoDbConfigProvider().mongo_password

    def __post_init__(self):
        self.client = AsyncIOMotorClient(host=self.mongo_uri, port=self.mongo_port)
        self.collection = self.client[self.mongo_db][self.mongo_collection]

    async def ping(self) -> bool:
        try:
            await self.client.admin.command("ping")
            logger.info("Pinged deployment. Successfully connected to MongoDB!")
            return True
        except Exception as e:
            logger.error(e)
            return False

    async def close(self):
        self.client.close()

    async def get_docs(self) -> list[dict]:
        docs = []
        async for doc in self.collection.find({}):
            docs.append(doc)
        return docs

    @staticmethod
    async def convert_date(news: list[dict]) -> list[dict]:
        for article in news:
            article["publishedAt"] = parser.parse(article["publishedAt"])
        return news

    @staticmethod
    async def add_inserted_time(news: list[dict]) -> list[dict]:
        current_datetime = datetime.now()
        for article in news:
            article["insertedAt"] = current_datetime
        return news

    @staticmethod
    async def remove_blank_author(news: list[dict]) -> list[dict]:
        news = [
            article
            for article in news
            if article["author"] != "" and article["author"] is not None
        ]
        return news

    @staticmethod
    async def remove_blank_content(news: list[dict]) -> list[dict]:
        news = [
            _ for _ in news if _["content"] != "[Removed]" and _["content"] is not None
        ]
        return news

    @staticmethod
    async def remove_blank_description(news: list[dict]) -> list[dict]:
        news = [
            _
            for _ in news
            if _["description"] != "[Removed]"
            and _["description"] != ""
            and _["description"] is not None
        ]
        return news

    async def save_news(self, news: list[dict]):
        news = await MongoDbNewsSaver.remove_blank_content(news)
        news = await MongoDbNewsSaver.remove_blank_description(news)
        news = await MongoDbNewsSaver.remove_blank_author(news)
        news = await MongoDbNewsSaver.convert_date(news)
        news = await MongoDbNewsSaver.add_inserted_time(news)
        try:
            await self.collection.insert_many(news)
        except Exception as e:
            logger.error(e)


async def main():
    try:
        is_pinged: bool = await MongoDbNewsSaver().ping()
        if is_pinged:
            logger.info("Saving news to MongoDB")
            await MongoDbNewsSaver().save_news(example_news)
    except Exception as e:
        logger.error(e)
    finally:
        await MongoDbNewsSaver().close()
        logger.info("MongoDB connection closed")


if __name__ == "__main__":
    example_news: list[dict] = [
        {
            "source": {"id": "bbc-news", "name": "BBC News"},
            "author": "BBC News",
            "title": "Why this month's inflation figure matters for you",
            "description": "The rate of rising prices, known as inflation, are a key factor in our own finances, particularly at this time of year.",
            "url": "https://www.bbc.co.uk/news/articles/czrmzm3113po",
            "urlToImage": "https://ichef.bbci.co.uk/news/1024/branded_news/1a57/live/3ac11670-8b97-11ef-ad63-6f68440cad48.jpg",
            "publishedAt": "2024-10-16T10:22:29.4886885Z",
            "content": "As inflation is now below the Bank of England's 2% target, it paves the way for further interest rate cuts.\r\nThat would make borrowing money less expensive, but could mean lower returns for savers.\r\n… [+988 chars]",
        },
        {
            "source": {"id": "bbc-news", "name": "BBC News"},
            "author": "BBC News",
            "title": "Inside the £70K 'mafia-style' shoplifting champagne gang",
            "description": "A crime gang has stolen more than £70,000 of goods from UK supermarkets in 18 months, the BBC hears.",
            "url": "https://www.bbc.co.uk/news/articles/czxdr29lyggo",
            "urlToImage": "https://ichef.bbci.co.uk/news/1024/branded_news/98c5/live/4acde8c0-8aef-11ef-81f8-1f28bcc5be15.jpg",
            "publishedAt": "2024-10-16T02:07:17.1038065Z",
            "content": "Retailers have repeatedly warned that shoplifting gangs are helping to fuel the rise in retail crime - and it is hitting shoppers in their pockets.\r\nShoplifting added £133 to the cost of an average U… [+1085 chars]",
        },
        {
            "source": {"id": "bbc-news", "name": "BBC News"},
            "author": "BBC News",
            "title": "Newspaper headlines:  'England pick German' and 'Taylorgate'",
            "description": "Wednesday's papers swoop on news that Thomas Tuchel will take over from Gareth Southgate as England coach.",
            "url": "https://www.bbc.co.uk/news/articles/cjd54grgv94o",
            "urlToImage": "https://ichef.bbci.co.uk/news/1024/branded_news/2e39/live/cad154f0-8b47-11ef-b6b0-c9af5f7f16e4.jpg",
            "publishedAt": "2024-10-16T00:52:18.1915401Z",
            "content": 'Image caption, Chancellor of the Exchequer Rachel Reeves has "identified a £40 billion funding gap" , reports the Financial Times. The paper says that the Treasury is seeking to close the gap, which … [+249 chars]',
        },
        {
            "source": {"id": "bbc-news", "name": "BBC News"},
            "author": "BBC News",
            "title": "Rachel Reeves eyes £40bn in tax rises and spending cuts in Budget",
            "description": 'Filling the £22bn financial "black hole" would only be enough “to keep public services" still, she told a meeting.',
            "url": "https://www.bbc.co.uk/news/articles/cj9jdgprv7ko",
            "urlToImage": "https://ichef.bbci.co.uk/news/1024/branded_news/84f1/live/d6a1d9b0-8b3a-11ef-81f8-1f28bcc5be15.jpg",
            "publishedAt": "2024-10-15T22:22:21.2225972Z",
            "content": 'The chancellor is finalising details of her first Budget, to be announced on Wednesday 30 October.\r\nShe recently said there would be "no return to austerity" under this government and promised a boos… [+1566 chars]',
        },
    ]

    asyncio.run(main())
