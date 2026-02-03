"""
Scheduler Integration for Media Clipping Agent
Manages cron jobs and scheduled searches
"""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from .config_manager import ConfigManager
from .orchestrator import ScheduledSearch


class SchedulerManager:
    """Manages scheduled media clipping jobs"""

    def __init__(self):
        self.config = ConfigManager()
        self.schedules_file = Path("/a0/usr/projects/project_1/media_clipping_agent/data/schedules.json")
        self.schedules_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.schedules_file.exists():
            self._save_schedules({})

    def _load_schedules(self) -> Dict:
        """Load scheduled jobs"""
        with open(self.schedules_file, 'r') as f:
            return json.load(f)

    def _save_schedules(self, schedules: Dict):
        """Save scheduled jobs"""
        with open(self.schedules_file, 'w') as f:
            json.dump(schedules, f, indent=2)

    def create_cron_schedule(self, 
                           job_id: str,
                           keywords: str,
                           duration_days: int,
                           interval_hours: int,
                           sources: List[str] = None) -> str:
        """
        Create a cron schedule for media clipping

        Returns the cron expression and saves the job config
        """
        # Calculate cron expression
        # interval_hours: 1-23 = hourly pattern, 24 = daily, 168 = weekly
        if interval_hours < 24:
            # Run every N hours
            cron = f"0 */{interval_hours} * * *"
        elif interval_hours == 24:
            # Daily at 9 AM
            cron = "0 9 * * *"
        elif interval_hours <= 168:
            # Weekly
            cron = "0 9 * * 1"  # Monday 9 AM
        else:
            # Monthly
            cron = "0 9 1 * *"  # 1st of month at 9 AM

        # Save job configuration
        schedules = self._load_schedules()
        schedules[job_id] = {
            "keywords": keywords,
            "duration_days": duration_days,
            "interval_hours": interval_hours,
            "sources": sources or [],
            "cron": cron,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        self._save_schedules(schedules)

        return cron

    def get_all_schedules(self) -> Dict:
        """Get all scheduled jobs"""
        return self._load_schedules()

    def get_schedule(self, job_id: str) -> Optional[Dict]:
        """Get specific scheduled job"""
        schedules = self._load_schedules()
        return schedules.get(job_id)

    def disable_schedule(self, job_id: str):
        """Disable a scheduled job"""
        schedules = self._load_schedules()
        if job_id in schedules:
            schedules[job_id]["active"] = False
            self._save_schedules(schedules)

    def delete_schedule(self, job_id: str):
        """Delete a scheduled job"""
        schedules = self._load_schedules()
        if job_id in schedules:
            del schedules[job_id]
            self._save_schedules(schedules)

    def generate_cron_command(self, job_id: str) -> str:
        """Generate the full cron command for a job"""
        schedules = self._load_schedules()
        job = schedules.get(job_id)

        if not job:
            raise ValueError(f"Job {job_id} not found")

        script_path = "/a0/usr/projects/project_1/media_clipping_agent/run_search.py"

        cmd = f"{job['cron']} cd /a0/usr/projects/project_1 && python {script_path} \\
"
        cmd += f"  --keywords \"{job['keywords']}\" \\
"
        cmd += f"  --duration-days {job['duration_days']} \\
"
        cmd += f"  --job-id {job_id}"

        return cmd

    def install_cron_job(self, job_id: str) -> bool:
        """Install a job into system crontab"""
        try:
            cmd = self.generate_cron_command(job_id)

            # Get existing crontab
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            existing = result.stdout if result.returncode == 0 else ""

            # Remove existing entry for this job if present
            lines = [l for l in existing.split("\n") if job_id not in l]
            new_crontab = "\n".join(lines) + f"\n# Media Clipping Agent - Job {job_id}\n{cmd}\n"

            # Install new crontab
            subprocess.run(
                ["crontab", "-"],
                input=new_crontab,
                text=True,
                check=True
            )

            return True
        except Exception as e:
            print(f"Error installing cron job: {e}")
            return False

    def remove_cron_job(self, job_id: str) -> bool:
        """Remove a job from system crontab"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            existing = result.stdout if result.returncode == 0 else ""

            # Filter out this job
            lines = []
            skip_next = False
            for line in existing.split("\n"):
                if skip_next:
                    skip_next = False
                    continue
                if f"Job {job_id}" in line:
                    skip_next = True
                    continue
                lines.append(line)

            new_crontab = "\n".join(lines)
            subprocess.run(
                ["crontab", "-"],
                input=new_crontab,
                text=True,
                check=True
            )

            return True
        except Exception as e:
            print(f"Error removing cron job: {e}")
            return False


# Helper for scheduler:wait_for_task compatibility
def get_scheduler_task_status(job_id: str) -> Dict:
    """Get status of a scheduled task"""
    manager = SchedulerManager()
    schedule = manager.get_schedule(job_id)

    if not schedule:
        return {"status": "not_found"}

    return {
        "status": "active" if schedule.get("active") else "disabled",
        "job_id": job_id,
        "keywords": schedule.get("keywords"),
        "cron": schedule.get("cron"),
        "created_at": schedule.get("created_at")
    }


if __name__ == "__main__":
    # Test scheduler
    manager = SchedulerManager()
    cron = manager.create_cron_schedule(
        "test-job",
        "artificial intelligence",
        duration_days=7,
        interval_hours=24
    )
    print(f"Created schedule: {cron}")
    print(f"Command: {manager.generate_cron_command('test-job')}")
