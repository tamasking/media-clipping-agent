"""
Main Orchestrator for Media Clipping Agent
Coordinates search, screenshot, and report generation
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable

from .config_manager import ConfigManager
from .search_engine import MediaSearchEngine, SearchResult
from .screenshot_capture import ScreenshotCapture
from .report_generator import ReportGenerator


class MediaClippingAgent:
    """Main agent orchestrating media clipping workflow"""

    def __init__(self, headless: bool = True):
        self.config = ConfigManager()
        self.headless = headless
        self.search_engine = None
        self.screenshot_capture = None
        self.report_generator = ReportGenerator()
        self.progress_callback = None

    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback

    async def run_search(self, keywords: str, 
                        sources: List[str] = None,
                        num_results: int = 20,
                        include_screenshots: bool = True,
                        duration_days: int = 7) -> Dict:
        """Run complete media clipping search workflow"""

        search_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()

        results = {
            "search_id": search_id,
            "keywords": keywords,
            "started_at": start_time.isoformat(),
            "status": "in_progress",
            "articles_found": 0,
            "screenshots_taken": 0,
            "report_path": "",
            "errors": []
        }

        try:
            # Initialize browser
            async with MediaSearchEngine(headless=self.headless) as search_engine:
                # Step 1: Web search
                self._notify_progress("Searching web...", 10)
                web_results = await search_engine.search_google(
                    keywords, 
                    num_results=num_results,
                    date_range=f"d{duration_days}"
                )

                # Step 2: News sites search
                self._notify_progress("Searching news sites...", 30)
                news_results = await search_engine.search_news_sites(keywords, custom_sites=sources)

                # Combine and deduplicate results
                all_results = self._deduplicate_results(web_results + news_results)
                results["articles_found"] = len(all_results)

                self._notify_progress(f"Found {len(all_results)} unique articles", 40)

                # Step 3: Capture screenshots
                if include_screenshots and all_results:
                    self._notify_progress("Capturing screenshots...", 50)

                    async with ScreenshotCapture(headless=self.headless) as capture:
                        for idx, article in enumerate(all_results):
                            progress = 50 + int((idx / len(all_results)) * 40)
                            self._notify_progress(
                                f"Screenshot {idx+1}/{len(all_results)}: {article.title[:50]}...",
                                progress
                            )

                            screenshot_path = await capture.capture_full_page(
                                article.url,
                                article.title
                            )
                            article.screenshot_path = screenshot_path or ""

                            if screenshot_path:
                                results["screenshots_taken"] += 1

                # Step 4: Generate report
                self._notify_progress("Generating report...", 90)

                report_data = [r.to_dict() for r in all_results]
                report_path = self.report_generator.generate_report(
                    report_data,
                    keywords=keywords,
                    report_name=f"media_clipping_{search_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                )

                results["report_path"] = report_path
                results["status"] = "completed"
                results["completed_at"] = datetime.now().isoformat()

                # Save results summary
                self._save_search_results(search_id, results, report_data)

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(str(e))
            raise

        self._notify_progress("Complete!", 100)
        return results

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []

        for result in results:
            # Normalize URL
            url = result.url.lower().strip().rstrip("/")
            url = url.replace("https://", "").replace("http://", "")

            if url and url not in seen_urls and len(url) > 10:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _notify_progress(self, message: str, percent: int):
        """Send progress update"""
        if self.progress_callback:
            self.progress_callback(message, percent)
        print(f"[{percent}%] {message}")

    def _save_search_results(self, search_id: str, summary: Dict, data: List[Dict]):
        """Save search results to JSON for reference"""
        results_dir = Path("/a0/usr/projects/project_1/media_clipping_agent/data/results")
        results_dir.mkdir(parents=True, exist_ok=True)

        output_file = results_dir / f"search_{search_id}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "summary": summary,
                "data": data
            }, f, indent=2)


# Scheduler integration for automated runs
class ScheduledSearch:
    """Configuration for scheduled media clipping searches"""

    def __init__(self, keywords: str, duration_days: int = 7, 
                 interval_hours: int = 24, sources: List[str] = None):
        self.keywords = keywords
        self.duration_days = duration_days
        self.interval_hours = interval_hours
        self.sources = sources or []
        self.search_id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict:
        return {
            "search_id": self.search_id,
            "keywords": self.keywords,
            "duration_days": self.duration_days,
            "interval_hours": self.interval_hours,
            "sources": self.sources
        }


# Convenience function for quick runs
def run_media_clipping(
    keywords: str,
    duration_days: int = 7,
    interval_hours: int = 24,
    num_results: int = 20,
    sources: List[str] = None,
    headless: bool = True,
    progress_callback: Callable = None
) -> Dict:
    """
    Run media clipping search and generate report

    Args:
        keywords: Search keywords
        duration_days: How many days back to search
        interval_hours: Interval for recurring searches (for scheduler)
        num_results: Maximum results to fetch
        sources: Additional custom news sources
        headless: Run browser in headless mode
        progress_callback: Function(message, percent) for progress updates

    Returns:
        Dictionary with search results and report path
    """
    agent = MediaClippingAgent(headless=headless)
    if progress_callback:
        agent.set_progress_callback(progress_callback)

    return asyncio.run(agent.run_search(
        keywords=keywords,
        sources=sources,
        num_results=num_results
    ))
