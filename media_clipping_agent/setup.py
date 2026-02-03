#!/usr/bin/env python3
"""
Interactive Setup for Media Clipping Agent
Guides user through configuration and scheduling
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/a0/usr/projects/project_1")

from media_clipping_agent.modules.config_manager import ConfigManager
from media_clipping_agent.modules.scheduler_manager import SchedulerManager


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_section(text):
    print(f"\n▶ {text}")
    print("-" * 40)


def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def get_int_input(prompt, default=None, min_val=None, max_val=None):
    while True:
        try:
            value = int(get_input(prompt, str(default) if default else None))
            if min_val is not None and value < min_val:
                print(f"  Please enter a value >= {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"  Please enter a value <= {max_val}")
                continue
            return value
        except ValueError:
            print("  Please enter a valid number")


def get_yes_no(prompt, default="y"):
    while True:
        response = get_input(prompt, default).lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        print("  Please enter 'y' or 'n'")


def main():
    print_header("📰 MEDIA CLIPPING AGENT SETUP")
    print("\nThis wizard will help you configure media monitoring")
    print("for your PR campaigns, events, or product launches.\n")

    config = ConfigManager()
    scheduler = SchedulerManager()

    # Step 1: Search Configuration
    print_section("Step 1: Search Configuration")

    keywords = get_input("Enter search keywords/phrases")
    if not keywords:
        print("❌ Keywords are required")
        return 1

    print(f"\nSearch keywords: "{keywords}"")

    duration_days = get_int_input(
        "How many days back should we search?",
        default=7,
        min_val=1,
        max_val=30
    )

    # Step 2: Custom Sources
    print_section("Step 2: News Sources")

    print("Default news sources configured:")
    sites = config.get_news_sites()
    print(f"  - News sites: {len(sites['news_sites'])}")
    print(f"  - Social platforms: {len(sites['social_platforms'])}")

    custom_sources = []
    if get_yes_no("\nAdd custom news source URLs?", "n"):
        print("Enter URLs (one per line, blank line to finish):")
        while True:
            url = input("  URL: ").strip()
            if not url:
                break
            if url.startswith("http"):
                custom_sources.append(url)
                print(f"    ✓ Added")
            else:
                print(f"    ⚠️  Invalid URL (must start with http/https)")

    # Step 3: Load from file
    if get_yes_no("\nLoad news sites from file?", "n"):
        file_path = get_input("Enter file path (one URL per line, or JSON)")
        if Path(file_path).exists():
            try:
                added = config.add_sites_from_file(file_path)
                print(f"  ✓ Added {len(added)} sites from file")
            except Exception as e:
                print(f"  ⚠️  Error loading file: {e}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

    # Step 4: Scheduling
    print_section("Step 3: Scheduling")

    print("Configure how often to run this search:")
    print("  1 - Every hour")
    print("  6 - Every 6 hours")
    print("  12 - Every 12 hours")
    print("  24 - Daily")
    print("  168 - Weekly")
    print("  0 - Run once only (no schedule)")

    interval_hours = get_int_input(
        "Enter interval in hours",
        default=24,
        min_val=0,
        max_val=720
    )

    # Step 5: Execute or Schedule
    print_section("Summary")
    print(f"Keywords: "{keywords}"")
    print(f"Search duration: {duration_days} days")
    print(f"Custom sources: {len(custom_sources)}")
    if interval_hours > 0:
        if interval_hours < 24:
            freq = f"every {interval_hours} hours"
        elif interval_hours == 24:
            freq = "daily"
        else:
            freq = f"every {interval_hours // 24} days"
        print(f"Schedule: {freq}")
    else:
        print("Schedule: Run once")

    if not get_yes_no("\nProceed?", "y"):
        print("\n❌ Setup cancelled")
        return 0

    # Create schedule if needed
    job_id = None
    if interval_hours > 0:
        job_id = f"clip-{keywords.replace(' ', '-')[:20]}"
        cron = scheduler.create_cron_schedule(
            job_id=job_id,
            keywords=keywords,
            duration_days=duration_days,
            interval_hours=interval_hours,
            sources=custom_sources
        )

        print(f"\n✅ Schedule created: {job_id}")
        print(f"Cron expression: {cron}")

        if get_yes_no("Install to system crontab now? (requires cron)", "n"):
            if scheduler.install_cron_job(job_id):
                print("  ✓ Cron job installed")
            else:
                print("  ⚠️  Could not install cron job automatically")
                print(f"\nManual command:")
                print(scheduler.generate_cron_command(job_id))

    # Run initial search
    if get_yes_no("\nRun initial search now?", "y"):
        print("\n" + "="*60)
        print("Starting search...")
        print("="*60)

        import asyncio
        from media_clipping_agent.modules.orchestrator import MediaClippingAgent

        def progress(msg, pct):
            print(f"\r[{pct:3d}%] {msg:<50}", end="", flush=True)

        async def run():
            agent = MediaClippingAgent(headless=True)
            agent.set_progress_callback(progress)
            return await agent.run_search(
                keywords=keywords,
                sources=custom_sources,
                duration_days=duration_days
            )

        try:
            result = asyncio.run(run())
            print("\n\n" + "="*60)
            print("✅ SEARCH COMPLETE")
            print("="*60)
            print(f"Articles found: {result['articles_found']}")
            print(f"Screenshots: {result['screenshots_taken']}")
            print(f"Report saved to:")
            print(f"  {result['report_path']}")

            if job_id:
                print(f"\n📅 This search will run automatically per your schedule")
                print(f"   Job ID: {job_id}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1

    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print(f"\nTo run manually later:")
    print(f"  python media_clipping_agent/run_search.py -k "{keywords}"")
    print(f"\nReports are saved to:")
    print(f"  /a0/usr/projects/project_1/media_clipping_agent/reports/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
