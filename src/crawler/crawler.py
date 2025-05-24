# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import sys
import asyncio
from typing import Optional, Dict

from .article import Article
from .jina_client import JinaClient
from .readability_extractor import ReadabilityExtractor


class Crawler:
    def __init__(self, backend: str = "jina", cache: Optional[Dict[str, Article]] = None):
        self.backend = backend
        self.cache = cache if cache is not None else {}

    def crawl(self, url: str) -> Article:
        # Check cache first
        if url in self.cache:
            return self.cache[url]
        try:
            if self.backend == "playwright":
                from .playwright_crawler import PlaywrightCrawler
                crawler_client = PlaywrightCrawler()
                html = crawler_client.crawl(url)
            else:
                jina_client = JinaClient()
                html = jina_client.crawl(url, return_format="html")
            extractor = ReadabilityExtractor()
            article = extractor.extract_article(html)
            article.url = url
            self.cache[url] = article
            return article
        except Exception as e:
            # Log or handle error as needed
            raise RuntimeError(f"Crawling failed for {url} with backend {self.backend}: {e}")

    async def acrawl(self, url: str) -> Article:
        # Async version for Playwright or future async backends
        if url in self.cache:
            return self.cache[url]
        try:
            if self.backend == "playwright":
                from .playwright_crawler import PlaywrightCrawler
                crawler_client = PlaywrightCrawler()
                html = await crawler_client.acrawl(url)
            else:
                # JinaClient is sync, so run in thread
                jina_client = JinaClient()
                loop = asyncio.get_event_loop()
                html = await loop.run_in_executor(None, jina_client.crawl, url, "html")
            extractor = ReadabilityExtractor()
            article = extractor.extract_article(html)
            article.url = url
            self.cache[url] = article
            return article
        except Exception as e:
            raise RuntimeError(f"Async crawling failed for {url} with backend {self.backend}: {e}")

    def crawl_batch(self, urls):
        # Placeholder for future batch crawling
        return [self.crawl(url) for url in urls]

    async def acrawl_batch(self, urls):
        # Placeholder for future async batch crawling
        return await asyncio.gather(*(self.acrawl(url) for url in urls))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = "https://fintel.io/zh-hant/s/br/nvdc34"
    # Example: pass backend as second argument
    backend = sys.argv[2] if len(sys.argv) > 2 else "jina"
    crawler = Crawler(backend=backend)
    article = crawler.crawl(url)
    print(article.to_markdown())
