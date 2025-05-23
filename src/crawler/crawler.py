# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import sys

from .article import Article
from .jina_client import JinaClient
from .readability_extractor import ReadabilityExtractor


class Crawler:
    def __init__(self, backend: str = "jina"):
        self.backend = backend

    def crawl(self, url: str) -> Article:
        # To help LLMs better understand content, we extract clean
        # articles from HTML, convert them to markdown, and split
        # them into text and image blocks for one single and unified
        # LLM message.
        #
        # Jina is not the best crawler on readability, however it's
        # much easier and free to use.
        #
        # Instead of using Jina's own markdown converter, we'll use
        # our own solution to get better readability results.
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
        return article


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
