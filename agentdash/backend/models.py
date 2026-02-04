from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    PERMANENT = "permanent"
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskType(str, enum.Enum):
    HEALTH_CHECK = "health_check"
    BACKUP = "backup"
    MONITORING = "monitoring"
    CUSTOM = "custom"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.BACKLOG)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    task_type = Column(Enum(TaskType), default=TaskType.CUSTOM)
    is_recurring = Column(Integer, default=0)  # 0 = false, >0 = days
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    metadata_json = Column(JSON, default=dict)

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    total_requests = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_latency = Column(Float, default=0.0)
    active_agents = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # info, success, warning, error
    message = Column(String, nullable=False)
    agent_name = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class Deliverable(Base):
    __tablename__ = "deliverables"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, server_default=func.now())
