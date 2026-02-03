"""
Search Engine Module for Media Clipping Agent
Handles web search, news site search, and social media monitoring
"""
import asyncio
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote, urljoin

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: playwright not available. Install with: pip install playwright")

from .config_manager import ConfigManager


class SearchResult:
    """Represents a single search result"""
    def __init__(self, title: str, url: str, snippet: str = "", source: str = "", 
                 published_date: str = "", reach_estimate: int = 0):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.published_date = published_date
        self.reach_estimate = reach_estimate
        self.screenshot_path = ""
        self.found_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "published_date": self.published_date,
            "reach_estimate": self.reach_estimate,
            "screenshot_path": self.screenshot_path,
            "found_at": self.found_at
        }


class MediaSearchEngine:
    """Main search engine for media clipping"""

    def __init__(self, headless: bool = True):
        self.config = ConfigManager()
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.results: List[SearchResult] = []

    async def __aenter__(self):
        if PLAYWRIGHT_AVAILABLE:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def search_google(self, keywords: str, num_results: int = 20, 
                           date_range: str = "w") -> List[SearchResult]:
        """Search Google for keywords"""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        results = []
        page = await self.context.new_page()

        try:
            # Build search URL with date filter
            encoded_keywords = quote(keywords)
            search_url = f"https://www.google.com/search?q={encoded_keywords}&num={num_results}"
            if date_range:
                search_url += f"&tbs=qdr:{date_range}"

            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector("div#search", timeout=10000)

            # Extract search results
            search_results = await page.query_selector_all("div.g")

            for idx, result in enumerate(search_results[:num_results]):
                try:
                    title_elem = await result.query_selector("h3")
                    title = await title_elem.inner_text() if title_elem else "No title"

                    link_elem = await result.query_selector("a[href]")
                    url = await link_elem.get_attribute("href") if link_elem else ""

                    snippet_elem = await result.query_selector("div.VwiC3b, span.MUxGbd")
                    snippet = await snippet_elem.inner_text() if snippet_elem else ""

                    # Try to extract date
                    date_elem = await result.query_selector("span.f")
                    date_text = await date_elem.inner_text() if date_elem else ""

                    if url and url.startswith("http"):
                        search_result = SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source="Google",
                            published_date=date_text
                        )
                        results.append(search_result)
                except Exception as e:
                    continue

        except Exception as e:
            print(f"Error in Google search: {e}")
        finally:
            await page.close()

        self.results.extend(results)
        return results

    async def search_news_sites(self, keywords: str, custom_sites: List[str] = None) -> List[SearchResult]:
        """Search specific news sites"""
        sites_config = self.config.get_news_sites()
        results = []

        # Combine default and custom sites
        sites_to_search = []
        for category in ["news_sites", "social_platforms", "custom_sites"]:
            sites_to_search.extend(sites_config.get(category, []))

        if custom_sites:
            for site_url in custom_sites:
                sites_to_search.append({"name": site_url, "url": site_url, "enabled": True})

        # Search each enabled site
        for site in sites_to_search:
            if not site.get("enabled", True):
                continue

            try:
                site_results = await self._search_single_site(site, keywords)
                results.extend(site_results)
            except Exception as e:
                print(f"Error searching {site.get('name')}: {e}")

        self.results.extend(results)
        return results

    async def _search_single_site(self, site: dict, keywords: str) -> List[SearchResult]:
        """Search a single news site"""
        results = []
        page = await self.context.new_page()

        try:
            site_url = site.get("url", "")
            site_name = site.get("name", "Unknown")

            # Try site's native search if available
            search_url = site.get("search_url")
            if not search_url and site_url:
                # Construct common search URLs
                if "google.com" in site_url:
                    search_url = f"https://www.google.com/search?q={quote(keywords)}+site:{site_url}"
                else:
                    search_url = f"{site_url.rstrip('/')}/search?q={quote(keywords)}"

            if search_url:
                await page.goto(search_url, wait_until="networkidle", timeout=20000)
                await asyncio.sleep(2)  # Let page load

                # Try to extract articles
                article_selectors = [
                    "article", "[class*='article']", "[class*='story']",
                    "[class*='post']", "[class*='news']", ".result", ".item"
                ]

                for selector in article_selectors:
                    elements = await page.query_selector_all(selector)
                    if len(elements) > 0:
                        for elem in elements[:10]:  # Limit to 10 per site
                            try:
                                title_elem = await elem.query_selector("h1, h2, h3, h4, [class*='title'], a")
                                title = await title_elem.inner_text() if title_elem else "No title"

                                link_elem = await elem.query_selector("a[href]")
                                href = await link_elem.get_attribute("href") if link_elem else ""
                                if href and not href.startswith("http"):
                                    href = urljoin(site_url, href)

                                result = SearchResult(
                                    title=title.strip()[:200],
                                    url=href,
                                    source=site_name,
                                    snippet=f"Found on {site_name}"
                                )
                                results.append(result)
                            except:
                                continue
                        break  # Found working selector
        except Exception as e:
            print(f"Error in site search for {site.get('name')}: {e}")
        finally:
            await page.close()

        return results

    def clear_results(self):
        """Clear all collected results"""
        self.results = []


# Standalone functions for simple searches
def quick_search(keywords: str, num_results: int = 10) -> List[Dict]:
    """Quick synchronous search function"""
    async def _search():
        async with MediaSearchEngine() as engine:
            return await engine.search_google(keywords, num_results)

    results = asyncio.run(_search())
    return [r.to_dict() for r in results]


if __name__ == "__main__":
    # Test the search engine
    async def test():
        async with MediaSearchEngine(headless=False) as engine:
            results = await engine.search_google("AI technology news", num_results=5)
            print(f"Found {len(results)} results")
            for r in results:
                print(f"- {r.title} ({r.source})")

    asyncio.run(test())
