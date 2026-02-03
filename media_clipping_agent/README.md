# 📰 Media Clipping Agent

An automated media monitoring and clipping system for PR campaigns, events, and product launches. Searches web, news sites, and social media platforms to track mentions, capture screenshots, and generate professional Excel reports with estimated audience reach.

---

## ✨ Features

- **🔍 Multi-Source Search**: Google web search + direct news site monitoring
- **📰 News Database**: Pre-configured major news outlets (BBC, CNN, Reuters, NYT, etc.)
- **📱 Social Media**: LinkedIn, Facebook, Instagram monitoring
- **📊 Custom Sources**: Add your own news sites via file or CLI
- **📸 Screenshots**: Full-page captures of each article found
- **📈 Reach Estimation**: Estimated audience numbers based on source authority
- **📑 Excel Reports**: Professional reports with embedded screenshots
- **⏰ Scheduling**: Automated recurring searches via cron jobs
- **🔄 Incremental Updates**: Continuously updates reports as new mentions appear

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (Chromium)
playwright install chromium
```

### 2. Interactive Setup

```bash
python setup.py
```

This wizard will guide you through:
- Setting search keywords
- Configuring news sources
- Scheduling frequency
- Running your first search

### 3. Run Manual Search

```bash
# Basic search
python run_search.py -k "your product launch"

# Advanced search
python run_search.py \
  --keywords "AI technology healthcare" \
  --duration-days 14 \
  --num-results 50 \
  --sources "https://custom-news-site.com"
```

---

## 📋 Command Reference

### `run_search.py` - Execute Media Searches

| Option | Description | Default |
|--------|-------------|---------|
| `-k, --keywords` | **Required.** Search keywords/phrases | - |
| `-d, --duration-days` | Days back to search | 7 |
| `-n, --num-results` | Max results to fetch | 20 |
| `-s, --sources` | Additional source URLs | - |
| `--no-screenshots` | Skip screenshot capture | False |
| `--no-headless` | Show browser (debug) | False |
| `-o, --output` | Save JSON summary | - |

### `setup.py` - Interactive Configuration

```bash
python setup.py
```

Walks you through:
1. Search keyword configuration
2. News source selection
3. Scheduling setup (hourly/daily/weekly)
4. Initial search execution

---

## 📁 Directory Structure

```
media_clipping_agent/
├── modules/              # Core Python modules
│   ├── config_manager.py      # Settings & news database
│   ├── search_engine.py       # Web/search functionality
│   ├── screenshot_capture.py  # Browser screenshots
│   ├── report_generator.py    # Excel report creation
│   ├── orchestrator.py        # Main workflow
│   └── scheduler_manager.py   # Cron job management
├── data/                 # Configuration & data
│   ├── config.json            # App settings
│   ├── news_sites.json        # News sources database
│   └── schedules.json         # Scheduled jobs
├── reports/              # Generated Excel reports
├── screenshots/          # Article screenshots
├── requirements.txt      # Python dependencies
├── run_search.py         # CLI tool
└── setup.py              # Interactive setup
```

---

## 🔧 Advanced Usage

### Adding Custom News Sources

**Via File (one URL per line):**
```bash
# Create file with URLs
echo "https://tech-news-site.com" > my_sources.txt
echo "https://industry-blog.com" >> my_sources.txt

# Use in search
python run_search.py -k "product launch" -s $(cat my_sources.txt)
```

**Via Setup Script:**
```bash
python setup.py
# Select "Add custom news source URLs"
```

### Scheduled Monitoring (Cron)

The setup script can automatically create cron jobs:

```bash
# Example: Daily monitoring of "Product X"
python setup.py
# > Keywords: "Product X"
# > Schedule: 24 (daily)
# > Install to crontab: yes
```

**Manual Cron Entry:**
```cron
# Daily at 9 AM
0 9 * * * cd /path/to/agent && python run_search.py -k "Product X" --duration-days 1

# Every 6 hours
0 */6 * * * cd /path/to/agent && python run_search.py -k "Event Name" --duration-days 1
```

### Programmatic Usage

```python
import asyncio
from media_clipping_agent.modules.orchestrator import MediaClippingAgent

async def monitor():
    agent = MediaClippingAgent(headless=True)

    def progress(msg, pct):
        print(f"[{pct}%] {msg}")

    agent.set_progress_callback(progress)

    result = await agent.run_search(
        keywords="Your Campaign",
        duration_days=7,
        num_results=30
    )

    print(f"Found {result['articles_found']} articles")
    print(f"Report: {result['report_path']}")

asyncio.run(monitor())
```

---

## 📊 Report Format

Generated Excel files include:

| Column | Description |
|--------|-------------|
| Date Found | When article was discovered |
| Published Date | Article publication date (if detected) |
| Title | Article headline |
| URL | Clickable link to article |
| Source | Website/social platform |
| Estimated Reach | Estimated audience size |
| Screenshot | Embedded page capture |
| Notes | Article snippet/snippet |

**Summary Section:**
- Total mentions found
- Combined estimated reach
- Search parameters used

---

## ⚙️ Configuration

Configuration files are stored in `data/`:

- `config.json` - App settings (timeouts, limits)
- `news_sites.json` - News source database
- `searches.json` - Active/completed searches

Edit these files to customize default behavior.

---

## 🔒 Privacy & Ethics

- **Respect robots.txt**: Tool follows site crawling policies
- **Rate limiting**: Built-in delays between requests
- **Fair use**: Designed for PR monitoring, not bulk scraping
- **Data retention**: Screenshots/reports stored locally only

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser won't start | Run `playwright install chromium` |
| No results found | Try broader keywords, increase --num-results |
| Screenshots empty | Try `--no-headless` to see browser |
| Excel won't open | Ensure openpyxl installed |
| Cron job not running | Check `crontab -l`, verify paths |

---

## 📦 Export/Transfer

To move this application to another system:

```bash
# 1. Copy entire directory
cp -r media_clipping_agent/ /destination/

# 2. Install dependencies on target system
pip install -r media_clipping_agent/requirements.txt
playwright install chromium

# 3. Run setup
python media_clipping_agent/setup.py
```

---

## 📝 License

MIT License - Free for personal and commercial use.

---

**Built for PR professionals, marketers, and communications teams.** 🚀
