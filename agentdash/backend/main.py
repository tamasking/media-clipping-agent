"""
AgentDash Backend - Real-time AI Agent Monitoring Dashboard
With OpenSaw Integration
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import random
import asyncio
import hashlib
import hmac

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, get_session, AsyncSessionLocal
from models import Task, Activity, Deliverable, Metric
from opensaw_integration import (
    OpenSawFinding, OpenSawTask, OpenSawWebhookPayload,
    OpenSawSeverity
)

# Configuration storage for OpenSaw
OPENSALAW_CONFIG: Dict[str, Any] = {
    "enabled": False,
    "endpoint_ip": None,
    "webhook_token": None,
    "auto_create_tasks": True,
    "severity_mapping": {
        "critical": "high",
        "high": "medium", 
        "medium": "medium",
        "low": "low",
        "info": "low"
    }
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

# Mock data for demo
mock_tasks = [
    {
        "id": "task-001",
        "title": "Social Media Campaign",
        "description": "Launch Q1 product awareness campaign",
        "status": "in-progress",
        "priority": "high",
        "type": "marketing",
        "assignee": "Sarah Chen",
        "created_at": "2026-02-01T10:00:00",
        "deadline": "2026-02-15T23:59:59"
    },
    {
        "id": "task-002", 
        "title": "News Article Coverage",
        "description": "Track PR mentions in tech publications",
        "status": "pending",
        "priority": "medium",
        "type": "pr",
        "assignee": "Mike Ross",
        "created_at": "2026-02-02T14:30:00",
        "deadline": "2026-02-10T18:00:00"
    },
    {
        "id": "task-003",
        "title": "Influencer Outreach",
        "description": "Contact top 10 industry influencers",
        "status": "completed",
        "priority": "high",
        "type": "marketing",
        "assignee": "Emma Wilson",
        "created_at": "2026-02-01T09:00:00",
        "completed_at": "2026-02-03T16:45:00"
    },
    {
        "id": "task-004",
        "title": "Competitor Analysis",
        "description": "Analyze competitor media mentions",
        "status": "in-progress",
        "priority": "low",
        "type": "research",
        "assignee": "Alex Kumar",
        "created_at": "2026-02-02T11:00:00",
        "deadline": "2026-02-20T17:00:00"
    },
    {
        "id": "task-005",
        "title": "Crisis Response Plan",
        "description": "Draft response templates for potential issues",
        "status": "blocked",
        "priority": "high",
        "type": "pr",
        "assignee": "Sarah Chen",
        "created_at": "2026-02-03T08:00:00",
        "deadline": "2026-02-05T12:00:00"
    }
]

mock_metrics = {
    "total_requests": 15420,
    "success_rate": 98.5,
    "avg_latency": 45,
    "active_agents": 12
}

mock_activities = [
    {"id": 1, "type": "task", "message": "New task created: Social Media Campaign", "timestamp": "2026-02-04T11:30:00", "agent": "System"},
    {"id": 2, "type": "alert", "message": "High priority task approaching deadline", "timestamp": "2026-02-04T11:15:00", "agent": "System"},
    {"id": 3, "type": "update", "message": "Task "News Coverage" moved to in-progress", "timestamp": "2026-02-04T10:45:00", "agent": "Sarah Chen"},
    {"id": 4, "type": "complete", "message": "Influencer outreach completed successfully", "timestamp": "2026-02-04T09:20:00", "agent": "Emma Wilson"},
    {"id": 5, "type": "api", "message": "API key regenerated for production", "timestamp": "2026-02-04T08:00:00", "agent": "Admin"},
]

mock_deliverables = [
    {"id": 1, "name": "Q1 Campaign Report.pdf", "type": "pdf", "size": "2.4 MB", "created": "2026-02-03"},
    {"id": 2, "name": "Media Coverage Analysis.xlsx", "type": "xlsx", "size": "856 KB", "created": "2026-02-02"},
    {"id": 3, "name": "Influencer Contact List.csv", "type": "csv", "size": "124 KB", "created": "2026-02-01"},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    await init_db()

    # Start background metrics simulation
    asyncio.create_task(simulate_metrics())

    yield

    # Cleanup
    pass

async def simulate_metrics():
    """Simulate real-time metrics updates"""
    while True:
        await asyncio.sleep(5)
        mock_metrics["total_requests"] += random.randint(10, 50)
        mock_metrics["avg_latency"] = max(20, min(100, mock_metrics["avg_latency"] + random.randint(-5, 5)))
        mock_metrics["success_rate"] = round(max(95, min(99.9, mock_metrics["success_rate"] + random.uniform(-0.2, 0.2))), 1)

        await manager.broadcast({
            "type": "metrics_update",
            "data": mock_metrics
        })

app = FastAPI(title="AgentDash API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks"""
    return {"tasks": mock_tasks}

@app.get("/api/metrics")
async def get_metrics():
    """Get current metrics"""
    return mock_metrics

@app.get("/api/activities")
async def get_activities():
    """Get recent activities"""
    return {"activities": mock_activities}

@app.get("/api/deliverables")
async def get_deliverables():
    """Get completed deliverables"""
    return {"deliverables": mock_deliverables}

# OpenSaw Integration Endpoints

class OpenSawConfig(BaseModel):
    enabled: bool
    endpoint_ip: Optional[str] = None
    webhook_token: Optional[str] = None
    auto_create_tasks: bool = True

@app.get("/api/opensaw/config")
async def get_opensaw_config():
    """Get OpenSaw integration configuration"""
    return OPENSALAW_CONFIG

@app.post("/api/opensaw/config")
async def update_opensaw_config(config: OpenSawConfig):
    """Update OpenSaw integration configuration"""
    OPENSALAW_CONFIG["enabled"] = config.enabled
    OPENSALAW_CONFIG["endpoint_ip"] = config.endpoint_ip
    OPENSALAW_CONFIG["webhook_token"] = config.webhook_token
    OPENSALAW_CONFIG["auto_create_tasks"] = config.auto_create_tasks

    # Broadcast config update
    await manager.broadcast({
        "type": "opensaw_config_update",
        "data": OPENSALAW_CONFIG
    })

    return {"status": "success", "config": OPENSALAW_CONFIG}

@app.get("/api/opensaw/status")
async def get_opensaw_status():
    """Check OpenSaw connection status"""
    return {
        "connected": OPENSALAW_CONFIG["enabled"] and OPENSALAW_CONFIG["endpoint_ip"] is not None,
        "last_ping": None,  # Would track actual last communication
        "config": OPENSALAW_CONFIG
    }

@app.post("/api/opensaw/webhook")
async def opensaw_webhook(
    payload: OpenSawWebhookPayload,
    request: Request,
    x_opensaw_signature: Optional[str] = Header(None)
):
    """
    Receive webhook from OpenSaw instance

    OpenSaw sends:
    - task.created: New scan/task started
    - task.updated: Scan progress update
    - task.completed: Scan finished
    - finding.discovered: New vulnerability/finding found
    """

    # Verify webhook token if configured
    if OPENSALAW_CONFIG["webhook_token"]:
        if payload.webhook_token != OPENSALAW_CONFIG["webhook_token"]:
            raise HTTPException(status_code=401, detail="Invalid webhook token")

    event_type = payload.event_type
    data = payload.data

    # Process different event types
    if event_type == "task.created" and OPENSALAW_CONFIG["auto_create_tasks"]:
        task_data = OpenSawTask(**data)
        new_task = {
            "id": f"opensaw-{task_data.id}",
            "title": f"🔍 {task_data.name}",
            "description": f"OpenSaw scan: {task_data.scan_type or 'Security Scan'}\nTarget: {task_data.target_ip or 'N/A'}",
            "status": "pending" if task_data.status == "pending" else "in-progress",
            "priority": "high",
            "type": "security",
            "assignee": "OpenSaw Agent",
            "created_at": task_data.created_at.isoformat(),
            "source": "opensaw"
        }
        mock_tasks.append(new_task)

        # Add activity
        activity = {
            "id": len(mock_activities) + 1,
            "type": "opensaw",
            "message": f"OpenSaw task created: {task_data.name}",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "OpenSaw"
        }
        mock_activities.insert(0, activity)

        await manager.broadcast({
            "type": "task_created",
            "data": new_task
        })

        return {"status": "success", "action": "task_created"}

    elif event_type == "finding.discovered":
        finding = OpenSawFinding(**data)

        # Map severity to priority
        priority = OPENSALAW_CONFIG["severity_mapping"].get(finding.severity.value, "low")

        new_task = {
            "id": f"finding-{finding.id}",
            "title": f"🚨 {finding.title}",
            "description": f"{finding.description or 'Security finding'}\n\nTarget: {finding.target}:{finding.port}\nService: {finding.service or 'Unknown'}",
            "status": "pending",
            "priority": priority,
            "type": "vulnerability",
            "assignee": "Security Team",
            "created_at": finding.timestamp.isoformat(),
            "source": "opensaw",
            "severity": finding.severity.value
        }
        mock_tasks.append(new_task)

        # Add critical activity for high severity
        if finding.severity in [OpenSawSeverity.CRITICAL, OpenSawSeverity.HIGH]:
            activity = {
                "id": len(mock_activities) + 1,
                "type": "alert",
                "message": f"🚨 CRITICAL: {finding.title} on {finding.target}",
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "OpenSaw"
            }
            mock_activities.insert(0, activity)

        await manager.broadcast({
            "type": "finding_discovered",
            "data": new_task
        })

        return {"status": "success", "action": "finding_logged"}

    elif event_type == "task.completed":
        task_data = OpenSawTask(**data)

        # Update existing task
        for task in mock_tasks:
            if task["id"] == f"opensaw-{task_data.id}":
                task["status"] = "completed"
                task["completed_at"] = task_data.completed_at.isoformat() if task_data.completed_at else datetime.utcnow().isoformat()

                await manager.broadcast({
                    "type": "task_completed",
                    "data": task
                })
                break

        return {"status": "success", "action": "task_completed"}

    return {"status": "success", "action": "received"}

@app.get("/api/opensaw/tasks")
async def get_opensaw_tasks():
    """Get all tasks created by OpenSaw"""
    opensaw_tasks = [t for t in mock_tasks if t.get("source") == "opensaw"]
    return {"tasks": opensaw_tasks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
