"""
Screenshot Capture Module for Media Clipping Agent
Captures full-page or viewport screenshots of articles
"""
import asyncio
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

try:
    from playwright.async_api import async_playwright, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ScreenshotCapture:
    """Handles screenshot capture for articles"""

    def __init__(self, screenshot_dir: str = None, headless: bool = True):
        if screenshot_dir is None:
            screenshot_dir = "/a0/usr/projects/project_1/media_clipping_agent/screenshots"
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None

    async def __aenter__(self):
        if PLAYWRIGHT_AVAILABLE:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def _generate_filename(self, url: str, prefix: str = "") -> str:
        """Generate unique filename for screenshot"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prefix = prefix.replace(" ", "_")[:50] if prefix else "article"
        return f"{safe_prefix}_{timestamp}_{url_hash}.png"

    async def capture_full_page(self, url: str, title: str = "", 
                               wait_for_load: bool = True,
                               timeout: int = 30000) -> Optional[str]:
        """Capture full page screenshot"""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        page = await self.context.new_page()
        screenshot_path = None

        try:
            # Navigate to page
            await page.goto(url, wait_until="networkidle", timeout=timeout)

            if wait_for_load:
                # Wait for common content indicators
                try:
                    await page.wait_for_selector("article, main, [class*='content'], body", timeout=5000)
                except:
                    pass
                await asyncio.sleep(2)  # Extra time for dynamic content

            # Generate filename and path
            filename = self._generate_filename(url, title)
            screenshot_path = self.screenshot_dir / filename

            # Take full page screenshot
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True,
                type="png"
            )

            return str(screenshot_path)

        except Exception as e:
            print(f"Error capturing screenshot for {url}: {e}")
            return None
        finally:
            await page.close()

    async def capture_viewport(self, url: str, title: str = "") -> Optional[str]:
        """Capture viewport-only screenshot (faster)"""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        page = await self.context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(1)

            filename = self._generate_filename(url, title)
            screenshot_path = self.screenshot_dir / filename

            await page.screenshot(
                path=str(screenshot_path),
                full_page=False,
                type="png"
            )

            return str(screenshot_path)

        except Exception as e:
            print(f"Error capturing viewport for {url}: {e}")
            return None
        finally:
            await page.close()

    async def capture_batch(self, urls_data: List[dict], 
                           progress_callback = None) -> List[dict]:
        """Capture screenshots for multiple URLs"""
        results = []
        total = len(urls_data)

        for idx, data in enumerate(urls_data):
            url = data.get("url", "")
            title = data.get("title", "")

            if progress_callback:
                progress_callback(idx + 1, total, title)

            screenshot_path = await self.capture_full_page(url, title)

            results.append({
                "url": url,
                "title": title,
                "screenshot_path": screenshot_path
            })

        return results


# Standalone function for quick screenshots
async def quick_screenshot(url: str, output_path: str = None) -> str:
    """Quick screenshot capture"""
    async with ScreenshotCapture(headless=True) as capture:
        return await capture.capture_full_page(url, output_path)
