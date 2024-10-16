import pytest
import pytest_asyncio

from testcontainers.mongodb import MongoDbContainer
from src.utils.mongodb_news_saver import MongoDbNewsSaver


# https://github.com/tortoise/tortoise-orm/issues/638#issuecomment-2386523478
@pytest_asyncio.fixture(autouse=True, scope="session", loop_scope="session")
def mongodb_container():
    """Fixture to set up a MongoDB container for the tests."""
    container = MongoDbContainer("mongo:latest")
    container.start()
    yield container
    container.stop()


@pytest_asyncio.fixture(autouse=True, scope="session", loop_scope="session")
async def news_saver(mongodb_container):
    """Fixture to set up MongoDbNewsSaver with async context manager."""
    mongo_uri = mongodb_container.get_connection_url()
    saver = MongoDbNewsSaver(
        mongo_uri=mongo_uri, mongo_db="test", mongo_collection="test"
    )
    try:
        yield saver
    finally:
        await saver.close()


@pytest.mark.asyncio
async def test_mongodb_save_news(news_saver):
    """Test case using the MongoDB container."""
    await news_saver.get_docs()

    test_data: list[dict] = [
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
    ]

    await news_saver.save_news(test_data)
    news_count = await news_saver.collection.count_documents({})
    assert news_count == 2

    result = await news_saver.collection.find_one(
        {"title": "Inside the £70K 'mafia-style' shoplifting champagne gang"}
    )
    assert result["author"] == "BBC News"
    assert (
        result["urlToImage"]
        == "https://ichef.bbci.co.uk/news/1024/branded_news/98c5/live/4acde8c0-8aef-11ef-81f8-1f28bcc5be15.jpg"
    )
