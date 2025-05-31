# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import sys
from enum import Enum
from typing import Optional
import asyncio

from .article import Article
from .jina_client import JinaClient
from .playwright_client import PlaywrightClient
from .readability_extractor import ReadabilityExtractor


class CrawlerType(Enum):
    JINA = "jina"
    PLAYWRIGHT = "playwright"


class Crawler:
    def __init__(self, crawler_type: CrawlerType = CrawlerType.JINA):
        self.crawler_type = crawler_type
    
    async def crawl_async(self, url: str) -> Article:
        """
        Asynchronously crawl a URL and return an Article.
        """
        if self.crawler_type == CrawlerType.PLAYWRIGHT:
            playwright_client = PlaywrightClient()
            html = await playwright_client.crawl_async(url)
        else:
            # For Jina, we'll need to make it async or run it in an executor
            jina_client = JinaClient()
            loop = asyncio.get_event_loop()
            html = await loop.run_in_executor(
                None, 
                lambda: jina_client.crawl(url, return_format="html")
            )
        
        extractor = ReadabilityExtractor()
        # If extractor also needs to be async, run it in executor
        loop = asyncio.get_event_loop()
        article = await loop.run_in_executor(
            None,
            lambda: extractor.extract_article(html)
        )
        article.url = url
        return article
    
    def crawl(self, url: str) -> Article:
        # To help LLMs better understand content, we extract clean
        # articles from HTML, convert them to markdown, and split
        # them into text and image blocks for one single and unified
        # LLM message.
        #
        # Jina is not the best crawler on readability, however it's
        # much easier and free to use. Playwright provides better
        # JavaScript rendering and can handle dynamic content.
        #
        # Instead of using built-in markdown converters, we'll use
        # our own solution to get better readability results.
        
        if self.crawler_type == CrawlerType.PLAYWRIGHT:
            playwright_client = PlaywrightClient()
            html = playwright_client.crawl(url)
        else:
            jina_client = JinaClient()
            html = jina_client.crawl(url, return_format="html")
        
        extractor = ReadabilityExtractor()
        article = extractor.extract_article(html)
        article.url = url
        return article
    
    async def crawl_multiple_async(self, urls: list[str]) -> list[Article]:
        """
        Crawl multiple URLs concurrently.
        """
        tasks = [self.crawl_async(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)


if __name__ == "__main__":
    crawler_type = CrawlerType.PLAYWRIGHT
    url = "https://fintel.io/zh-hant/s/br/nvdc34"
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] in ["--playwright", "-p"]:
            crawler_type = CrawlerType.PLAYWRIGHT
            if len(sys.argv) >= 3:
                url = sys.argv[2]
        else:
            url = sys.argv[1]
            if len(sys.argv) >= 3 and sys.argv[2] in ["--playwright", "-p"]:
                crawler_type = CrawlerType.PLAYWRIGHT
    
    crawler = Crawler(crawler_type)
    article = crawler.crawl(url)
    print(article.to_markdown())
