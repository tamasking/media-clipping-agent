"""
Configuration and Database Manager for Media Clipping Agent
Handles news sites database, user settings, and search criteria
"""
import json
import os
from datetime import datetime
from pathlib import Path

class ConfigManager:
    def __init__(self, base_path="/a0/usr/projects/project_1/media_clipping_agent"):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.config_file = self.data_path / "config.json"
        self.news_sites_file = self.data_path / "news_sites.json"
        self.searches_file = self.data_path / "searches.json"

        # Ensure directories exist
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Initialize default files
        self._init_config()
        self._init_news_sites()
        self._init_searches()

    def _init_config(self):
        """Initialize main configuration"""
        default_config = {
            "default_search_duration_days": 7,
            "default_interval_hours": 24,
            "max_results_per_source": 50,
            "screenshot_timeout": 30,
            "headless": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        if not self.config_file.exists():
            self._save_json(self.config_file, default_config)

    def _init_news_sites(self):
        """Initialize default news sites database"""
        default_sites = {
            "news_sites": [
                {"name": "BBC News", "url": "https://www.bbc.com/news", "type": "news", "enabled": True},
                {"name": "CNN", "url": "https://www.cnn.com", "type": "news", "enabled": True},
                {"name": "Reuters", "url": "https://www.reuters.com", "type": "news", "enabled": True},
                {"name": "Associated Press", "url": "https://apnews.com", "type": "news", "enabled": True},
                {"name": "The Guardian", "url": "https://www.theguardian.com", "type": "news", "enabled": True},
                {"name": "Washington Post", "url": "https://www.washingtonpost.com", "type": "news", "enabled": True},
                {"name": "New York Times", "url": "https://www.nytimes.com", "type": "news", "enabled": True},
                {"name": "TechCrunch", "url": "https://techcrunch.com", "type": "tech", "enabled": True},
                {"name": "The Verge", "url": "https://www.theverge.com", "type": "tech", "enabled": True},
                {"name": "Forbes", "url": "https://www.forbes.com", "type": "business", "enabled": True}
            ],
            "social_platforms": [
                {"name": "LinkedIn", "url": "https://www.linkedin.com", "type": "social", "enabled": True, "search_url": "https://www.linkedin.com/search/results/content/?keywords="},
                {"name": "Facebook", "url": "https://www.facebook.com", "type": "social", "enabled": True, "search_url": "https://www.facebook.com/search/posts/?q="},
                {"name": "Instagram", "url": "https://www.instagram.com", "type": "social", "enabled": True, "search_url": "https://www.instagram.com/explore/tags/"}
            ],
            "custom_sites": []
        }
        if not self.news_sites_file.exists():
            self._save_json(self.news_sites_file, default_sites)

    def _init_searches(self):
        """Initialize searches tracking"""
        if not self.searches_file.exists():
            self._save_json(self.searches_file, {"active_searches": [], "completed_searches": []})

    def _save_json(self, filepath, data):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_json(self, filepath):
        """Load data from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def get_config(self):
        """Get current configuration"""
        return self._load_json(self.config_file)

    def update_config(self, updates):
        """Update configuration"""
        config = self.get_config()
        config.update(updates)
        config["updated_at"] = datetime.now().isoformat()
        self._save_json(self.config_file, config)
        return config

    def get_news_sites(self, enabled_only=True):
        """Get news sites database"""
        data = self._load_json(self.news_sites_file)
        if enabled_only:
            return {
                "news_sites": [s for s in data.get("news_sites", []) if s.get("enabled", True)],
                "social_platforms": [s for s in data.get("social_platforms", []) if s.get("enabled", True)],
                "custom_sites": [s for s in data.get("custom_sites", []) if s.get("enabled", True)]
            }
        return data

    def add_news_site(self, name, url, site_type="custom"):
        """Add a custom news site"""
        data = self._load_json(self.news_sites_file)
        new_site = {
            "name": name,
            "url": url,
            "type": site_type,
            "enabled": True,
            "added_at": datetime.now().isoformat()
        }
        data["custom_sites"].append(new_site)
        self._save_json(self.news_sites_file, data)
        return new_site

    def remove_news_site(self, name):
        """Remove a news site by name"""
        data = self._load_json(self.news_sites_file)
        data["custom_sites"] = [s for s in data["custom_sites"] if s["name"] != name]
        data["news_sites"] = [s for s in data["news_sites"] if s["name"] != name]
        self._save_json(self.news_sites_file, data)

    def add_sites_from_file(self, filepath):
        """Add sites from a file (one URL per line or JSON)"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        added = []
        with open(path, 'r') as f:
            content = f.read().strip()
            # Try JSON first
            try:
                sites = json.loads(content)
                if isinstance(sites, list):
                    for site in sites:
                        if isinstance(site, dict):
                            self.add_news_site(site.get("name"), site.get("url"), site.get("type", "custom"))
                            added.append(site.get("name"))
                        elif isinstance(site, str):
                            name = site.split("//")[-1].split("/")[0]
                            self.add_news_site(name, site, "custom")
                            added.append(name)
            except json.JSONDecodeError:
                # Treat as plain text (one URL per line)
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        name = line.split("//")[-1].split("/")[0]
                        self.add_news_site(name, line, "custom")
                        added.append(name)
        return added

    def save_search_criteria(self, search_id, keywords, duration_days, interval_hours, sources):
        """Save a new search configuration"""
        data = self._load_json(self.searches_file)
        search_config = {
            "id": search_id,
            "keywords": keywords,
            "duration_days": duration_days,
            "interval_hours": interval_hours,
            "sources": sources,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        data["active_searches"].append(search_config)
        self._save_json(self.searches_file, data)
        return search_config

    def get_active_searches(self):
        """Get all active searches"""
        data = self._load_json(self.searches_file)
        return data.get("active_searches", [])

    def complete_search(self, search_id):
        """Mark a search as completed"""
        data = self._load_json(self.searches_file)
        active = data.get("active_searches", [])
        completed = data.get("completed_searches", [])

        for search in active:
            if search["id"] == search_id:
                search["status"] = "completed"
                search["completed_at"] = datetime.now().isoformat()
                completed.append(search)
                data["active_searches"] = [s for s in active if s["id"] != search_id]
                break

        self._save_json(self.searches_file, data)


if __name__ == "__main__":
    # Test the config manager
    cm = ConfigManager()
    print("Config:", json.dumps(cm.get_config(), indent=2))
    print("\nNews Sites:", json.dumps(cm.get_news_sites(), indent=2))
