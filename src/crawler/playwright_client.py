# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutErrorSync
from typing import Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class PlaywrightClient:
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
    
    async def crawl_async(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Crawl a URL using Playwright asynchronously and return the HTML content.
        
        Args:
            url: The URL to crawl
            wait_for_selector: Optional CSS selector to wait for before extracting content
            
        Returns:
            HTML content as string
            
        Raises:
            Exception: If crawling fails
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                
                # Set a reasonable viewport
                await page.set_viewport_size({"width": 1280, "height": 720})
                
                # Navigate to the page
                await page.goto(url, timeout=self.timeout)
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=self.timeout)
                else:
                    # Wait for network to be idle
                    await page.wait_for_load_state("networkidle", timeout=self.timeout)
                
                # Get the HTML content
                html = await page.content()
                await browser.close()
                
                return html
                
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout while crawling {url}: {e}")
            raise Exception(f"Timeout while crawling {url}")
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            raise Exception(f"Failed to crawl {url}: {str(e)}")
    
    def crawl(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Crawl a URL using Playwright synchronously and return the HTML content.
        This is a wrapper around the async method for backward compatibility.
        
        Args:
            url: The URL to crawl
            wait_for_selector: Optional CSS selector to wait for before extracting content
            
        Returns:
            HTML content as string
            
        Raises:
            Exception: If crawling fails
        """
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're already in an async context, we need to use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.crawl_async(url, wait_for_selector))
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run directly
            return asyncio.run(self.crawl_async(url, wait_for_selector))
        except Exception as e:
            # Fallback to sync implementation
            return self._crawl_sync(url, wait_for_selector)
    
    def _crawl_sync(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Fallback synchronous crawl method using sync Playwright API.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                
                # Set a reasonable viewport
                page.set_viewport_size({"width": 1280, "height": 720})
                
                # Navigate to the page
                page.goto(url, timeout=self.timeout)
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    page.wait_for_selector(wait_for_selector, timeout=self.timeout)
                else:
                    # Wait for network to be idle
                    page.wait_for_load_state("networkidle", timeout=self.timeout)
                
                # Get the HTML content
                html = page.content()
                browser.close()
                
                return html
                
        except PlaywrightTimeoutErrorSync as e:
            logger.error(f"Timeout while crawling {url}: {e}")
            raise Exception(f"Timeout while crawling {url}")
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            raise Exception(f"Failed to crawl {url}: {str(e)}")
    
    async def crawl_multiple_async(self, urls: list[str], wait_for_selector: Optional[str] = None) -> list[str]:
        """
        Crawl multiple URLs concurrently using async Playwright.
        
        Args:
            urls: List of URLs to crawl
            wait_for_selector: Optional CSS selector to wait for before extracting content
            
        Returns:
            List of HTML content strings in the same order as input URLs
        """
        tasks = [self.crawl_async(url, wait_for_selector) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)