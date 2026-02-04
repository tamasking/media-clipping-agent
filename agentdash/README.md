# AgentDash 🚀

Real-time AI Agent Monitoring Dashboard - A replica of the AgentDash interface with dark theme, live metrics, and Kanban task management.

![AgentDash](screenshot.png)

## ✨ Features

- 🔴 **Live Status Indicator** - Real-time WebSocket connection
- 🔑 **API Key Management** - Generate, copy, and regenerate API keys
- 📊 **Performance Metrics** - Total requests, success rate, latency, active agents
- 🎯 **Kanban Task Board** - Drag-and-drop task management (Permanent, Backlog, In Progress)
- 🏷️ **Rich Task Cards** - Priority badges, type icons, recurring indicators
- 📦 **Deliverables Tracking** - View completed work
- 📜 **Activity Log** - Real-time event stream with timestamps
- 🎨 **Dark Theme** - Purple/black aesthetic with neon accents

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python FastAPI + WebSocket |
| Database | SQLite (async) |
| Drag & Drop | @dnd-kit |
| Charts | Recharts |

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
cd agentdash
docker-compose up -d
```

Access at: http://localhost:3000

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/key` | GET | Get API key |
| `/api/metrics` | GET/POST | Get/Update metrics |
| `/api/tasks` | GET/POST | List/Create tasks |
| `/api/tasks/{id}` | PUT/DELETE | Update/Delete task |
| `/api/activities` | GET/POST | List/Create activities |
| `/api/deliverables` | GET | List deliverables |
| `/api/ingest` | POST | Ingest data from agents |
| `/ws` | WebSocket | Real-time updates |

## 🔌 Agent Integration

Send metrics from your agents:

```python
import requests

response = requests.post('http://localhost:8000/api/ingest', 
    json={
        'type': 'success',
        'message': 'Task completed',
        'agent_name': 'MyAgent'
    },
    headers={'x-api-key': 'your-api-key'}
)
```

## 🐳 Docker Deployment

Build and run:
```bash
docker-compose up --build -d
```

Stop:
```bash
docker-compose down
```

## 📝 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | 8000 | Backend API port |
| `FRONTEND_PORT` | 3000 | Frontend dev server port |

## 📁 Project Structure

```
agentdash/
├── backend/
│   ├── main.py              # FastAPI app with WebSocket
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # Database connection
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx          # Main app
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml
```

## 🤝 Contributing

Feel free to submit issues and pull requests!

## 📄 License

MIT License - Built with ❤️ by Agent Zero
