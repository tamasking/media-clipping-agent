import asyncio
import json
import secrets
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel

from database import init_db, async_session, engine
from models import Task, TaskStatus, Priority, TaskType, Metric, Activity, Deliverable

# API Key storage (in production, use secure storage)
API_KEY = "ak_" + secrets.token_hex(32)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.BACKLOG
    priority: Priority = Priority.MEDIUM
    task_type: TaskType = TaskType.CUSTOM
    is_recurring: int = 0

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    task_type: Optional[TaskType] = None
    is_recurring: Optional[int] = None

class MetricUpdate(BaseModel):
    total_requests: Optional[int] = None
    success_rate: Optional[float] = None
    avg_latency: Optional[float] = None
    active_agents: Optional[int] = None

class ActivityCreate(BaseModel):
    type: str
    message: str
    agent_name: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="AgentDash API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now, can be extended for bidirectional commands
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Key endpoints
@app.get("/api/key")
async def get_api_key():
    return {"api_key": API_KEY}

@app.post("/api/key/regenerate")
async def regenerate_api_key():
    global API_KEY
    API_KEY = "ak_" + secrets.token_hex(32)
    return {"api_key": API_KEY}

# Metrics endpoints
@app.get("/api/metrics")
async def get_metrics():
    async with async_session() as session:
        result = await session.execute(select(Metric).order_by(desc(Metric.id)).limit(1))
        metric = result.scalar_one_or_none()
        if not metric:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "avg_latency": 0.0,
                "active_agents": 0
            }
        return {
            "total_requests": metric.total_requests,
            "success_rate": metric.success_rate,
            "avg_latency": metric.avg_latency,
            "active_agents": metric.active_agents
        }

@app.post("/api/metrics")
async def update_metrics(metric_update: MetricUpdate):
    async with async_session() as session:
        result = await session.execute(select(Metric).order_by(desc(Metric.id)).limit(1))
        metric = result.scalar_one_or_none()

        if not metric:
            metric = Metric()
            session.add(metric)

        if metric_update.total_requests is not None:
            metric.total_requests = metric_update.total_requests
        if metric_update.success_rate is not None:
            metric.success_rate = metric_update.success_rate
        if metric_update.avg_latency is not None:
            metric.avg_latency = metric_update.avg_latency
        if metric_update.active_agents is not None:
            metric.active_agents = metric_update.active_agents

        await session.commit()

        # Broadcast update
        await manager.broadcast({
            "type": "metrics_update",
            "data": {
                "total_requests": metric.total_requests,
                "success_rate": metric.success_rate,
                "avg_latency": metric.avg_latency,
                "active_agents": metric.active_agents
            }
        })

        return {"status": "updated"}

# Task endpoints
@app.get("/api/tasks")
async def get_tasks():
    async with async_session() as session:
        result = await session.execute(select(Task).order_by(desc(Task.created_at)))
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status.value,
                "priority": t.priority.value,
                "task_type": t.task_type.value,
                "is_recurring": t.is_recurring,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tasks
        ]

@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    async with async_session() as session:
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            task_type=task.task_type,
            is_recurring=task.is_recurring
        )
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        await manager.broadcast({
            "type": "task_created",
            "data": {
                "id": db_task.id,
                "title": db_task.title,
                "status": db_task.status.value
            }
        })

        return {"id": db_task.id, "status": "created"}

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.priority is not None:
            task.priority = task_update.priority
        if task_update.task_type is not None:
            task.task_type = task_update.task_type
        if task_update.is_recurring is not None:
            task.is_recurring = task_update.is_recurring

        await session.commit()

        await manager.broadcast({
            "type": "task_updated",
            "data": {
                "id": task.id,
                "status": task.status.value
            }
        })

        return {"status": "updated"}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        await session.delete(task)
        await session.commit()

        await manager.broadcast({
            "type": "task_deleted",
            "data": {"id": task_id}
        })

        return {"status": "deleted"}

# Activity endpoints
@app.get("/api/activities")
async def get_activities(limit: int = 20):
    async with async_session() as session:
        result = await session.execute(
            select(Activity).order_by(desc(Activity.created_at)).limit(limit)
        )
        activities = result.scalars().all()
        return [
            {
                "id": a.id,
                "type": a.type,
                "message": a.message,
                "agent_name": a.agent_name,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in activities
        ]

@app.post("/api/activities")
async def create_activity(activity: ActivityCreate):
    async with async_session() as session:
        db_activity = Activity(
            type=activity.type,
            message=activity.message,
            agent_name=activity.agent_name
        )
        session.add(db_activity)
        await session.commit()
        await session.refresh(db_activity)

        await manager.broadcast({
            "type": "activity_created",
            "data": {
                "id": db_activity.id,
                "type": db_activity.type,
                "message": db_activity.message
            }
        })

        return {"id": db_activity.id, "status": "created"}

# Deliverables endpoints
@app.get("/api/deliverables")
async def get_deliverables():
    async with async_session() as session:
        result = await session.execute(select(Deliverable).order_by(desc(Deliverable.created_at)))
        deliverables = result.scalars().all()
        return [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "file_path": d.file_path,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in deliverables
        ]

# Ingest endpoint for agents
@app.post("/api/ingest")
async def ingest_data(data: dict):
    """Receive data from external agents"""
    async with async_session() as session:
        # Log activity
        activity = Activity(
            type=data.get("type", "info"),
            message=data.get("message", "Data ingested"),
            agent_name=data.get("agent_name", "Unknown")
        )
        session.add(activity)
        await session.commit()

        await manager.broadcast({
            "type": "ingest_received",
            "data": data
        })

        return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
