#!/usr/bin/env python3
"""
CLI Interface for Media Clipping Agent
Run searches from command line or cron
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, "/a0/usr/projects/project_1")

from media_clipping_agent.modules.orchestrator import MediaClippingAgent
from media_clipping_agent.modules.config_manager import ConfigManager


def main():
    parser = argparse.ArgumentParser(
        description="Media Clipping Agent - Search and report on media mentions"
    )
    parser.add_argument(
        "--keywords", "-k",
        required=True,
        help="Search keywords (quoted if multiple words)"
    )
    parser.add_argument(
        "--duration-days", "-d",
        type=int,
        default=7,
        help="How many days back to search (default: 7)"
    )
    parser.add_argument(
        "--num-results", "-n",
        type=int,
        default=20,
        help="Maximum results to fetch (default: 20)"
    )
    parser.add_argument(
        "--sources", "-s",
        nargs="+",
        help="Additional news source URLs to search"
    )
    parser.add_argument(
        "--no-screenshots",
        action="store_true",
        help="Skip screenshot capture (faster)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Show browser window (for debugging)"
    )
    parser.add_argument(
        "--job-id",
        help="Job ID for scheduled runs"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file for results summary"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run interactive setup"
    )

    args = parser.parse_args()

    # Progress callback
    def progress(message, percent):
        print(f"\r[{percent:3d}%] {message:<60}", end="", flush=True)

    print(f"\n{'='*60}")
    print(f"📰 MEDIA CLIPPING AGENT")
    print(f"{'='*60}")
    print(f"Keywords: {args.keywords}")
    print(f"Duration: {args.duration_days} days")
    print(f"Max Results: {args.num_results}")
    if args.sources:
        print(f"Custom Sources: {len(args.sources)}")
    print(f"{'='*60}\n")

    # Run search
    try:
        agent = MediaClippingAgent(headless=args.headless)
        agent.set_progress_callback(progress)

        result = asyncio.run(agent.run_search(
            keywords=args.keywords,
            sources=args.sources,
            num_results=args.num_results,
            include_screenshots=not args.no_screenshots,
            duration_days=args.duration_days
        ))

        print("\n")
        print(f"\n{'='*60}")
        print("✅ SEARCH COMPLETE")
        print(f"{'='*60}")
        print(f"Search ID: {result['search_id']}")
        print(f"Articles Found: {result['articles_found']}")
        print(f"Screenshots Taken: {result['screenshots_taken']}")
        print(f"Report: {result['report_path']}")

        if result.get('errors'):
            print(f"\n⚠️  Errors: {len(result['errors'])}")
            for err in result['errors']:
                print(f"  - {err}")

        print(f"{'='*60}")

        # Save summary if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Summary saved to: {args.output}")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Search interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
