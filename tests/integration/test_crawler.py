# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import pytest
import asyncio
from src.crawler import Crawler
from src.crawler.crawler import CrawlerType
from src.crawler.playwright_client import PlaywrightClient


def test_crawler_initialization():
    """Test that crawler can be properly initialized."""
    crawler = Crawler()
    assert isinstance(crawler, Crawler)


def test_crawler_crawl_valid_url():
    """Test crawling with a valid URL."""
    crawler = Crawler()
    test_url = "https://finance.sina.com.cn/stock/relnews/us/2024-08-15/doc-incitsya6536375.shtml"
    result = crawler.crawl(test_url)
    assert result is not None
    assert hasattr(result, "to_markdown")


def test_crawler_markdown_output():
    """Test that crawler output can be converted to markdown."""
    crawler = Crawler()
    test_url = "https://finance.sina.com.cn/stock/relnews/us/2024-08-15/doc-incitsya6536375.shtml"
    result = crawler.crawl(test_url)
    markdown = result.to_markdown()
    assert isinstance(markdown, str)
    assert len(markdown) > 0


def test_playwright_client_initialization():
    """Test that PlaywrightClient can be properly initialized."""
    client = PlaywrightClient()
    assert isinstance(client, PlaywrightClient)
    
    # Test custom parameters
    custom_client = PlaywrightClient(headless=False, timeout=60000)
    assert custom_client.headless is False
    assert custom_client.timeout == 60000


def test_playwright_client_crawl_sync():
    """Test synchronous crawling with PlaywrightClient."""
    client = PlaywrightClient()
    test_url = "https://example.com"
    html = client.crawl(test_url)
    
    # Basic validation of HTML content
    assert isinstance(html, str)
    assert len(html) > 0
    assert "<html" in html.lower()
    assert "</html>" in html.lower()


@pytest.mark.asyncio
async def test_playwright_client_crawl_async():
    """Test asynchronous crawling with PlaywrightClient."""
    client = PlaywrightClient()
    test_url = "https://example.com"
    html = await client.crawl_async(test_url)
    
    # Basic validation of HTML content
    assert isinstance(html, str)
    assert len(html) > 0
    assert "<html" in html.lower()
    assert "</html>" in html.lower()


@pytest.mark.asyncio
async def test_playwright_client_crawl_multiple():
    """Test crawling multiple URLs concurrently with PlaywrightClient."""
    client = PlaywrightClient()
    test_urls = ["https://example.com", "https://google.com"]
    results = await client.crawl_multiple_async(test_urls)
    
    # Validate results
    assert isinstance(results, list)
    assert len(results) == len(test_urls)
    for html in results:
        assert isinstance(html, str)
        assert len(html) > 0


def test_crawler_with_playwright():
    """Test that Crawler works with PlaywrightClient."""
    crawler = Crawler(crawler_type=CrawlerType.PLAYWRIGHT)
    test_url = "https://example.com"
    result = crawler.crawl(test_url)
    
    # Validate result
    assert result is not None
    assert hasattr(result, "to_markdown")
    assert hasattr(result, "url")
    assert result.url == test_url


@pytest.mark.asyncio
async def test_crawler_async_with_playwright():
    """Test that Crawler works asynchronously with PlaywrightClient."""
    crawler = Crawler(crawler_type=CrawlerType.PLAYWRIGHT)
    test_url = "https://example.com"
    result = await crawler.crawl_async(test_url)
    
    # Validate result
    assert result is not None
    assert hasattr(result, "to_markdown")
    assert hasattr(result, "url")
    assert result.url == test_url
