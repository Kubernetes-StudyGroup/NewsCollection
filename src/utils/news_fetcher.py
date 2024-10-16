import asyncio
from mmap import PAGESIZE

import aiohttp

from aiohttp import ClientSession
from contextlib import asynccontextmanager
from dataclasses import dataclass

from src.utils.config_collections import APIConfigProvider


PAGESIZE: int = 100


@dataclass
class NewsFetcher:
    api_key: str = APIConfigProvider().news_api_key
    api_base_url: str = APIConfigProvider().news_api_base_url
    session: ClientSession = None

    @asynccontextmanager
    async def session_manager(self):
        async with aiohttp.ClientSession() as session:
            try:
                yield session
            finally:
                await session.close()

    async def fetch_top_lines(self, session: ClientSession, country: str = "us"):
        url: str = (
            f"{self.api_base_url}/top-headlines?country={country}&apiKey={self.api_key}&pageSize={PAGESIZE}"
        )
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
