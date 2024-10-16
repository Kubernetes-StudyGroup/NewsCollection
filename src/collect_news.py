import asyncio

from dataclasses import dataclass
from loguru import logger
from utils.news_fetcher import NewsFetcher
from utils.mongodb_news_saver import MongoDbNewsSaver


@dataclass
class NewsCollector:
    news_fetcher: NewsFetcher
    mongo_db_news_saver: MongoDbNewsSaver

    async def collect_news(self, country: str = "us"):
        async with self.news_fetcher.session_manager() as session:
            try:
                headlines = await self.news_fetcher.fetch_top_lines(session, country)
            except Exception as e:
                logger.error(e)
            else:
                logger.info(f"Fetched {headlines['totalResults']} news")
                await self.mongo_db_news_saver.save_news(headlines["articles"])


async def main():
    news_collector = NewsCollector(NewsFetcher(), MongoDbNewsSaver())
    await news_collector.collect_news()


if __name__ == "__main__":
    asyncio.run(main())
