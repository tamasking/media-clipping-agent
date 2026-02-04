"""
OpenSaw Integration Module
Receives data from OpenSaw instance and converts to dashboard tasks
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum

class OpenSawSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class OpenSawFinding(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    severity: OpenSawSeverity
    target: Optional[str] = None  # IP/domain scanned
    port: Optional[int] = None
    service: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class OpenSawTask(BaseModel):
    id: str
    name: str
    status: str  # pending, running, completed, failed
    target_ip: Optional[str] = None
    scan_type: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    findings_count: Optional[int] = 0

class OpenSawWebhookPayload(BaseModel):
    source_ip: str  # OpenSaw instance IP
    webhook_token: Optional[str] = None
    event_type: str  # task.created, task.updated, finding.discovered
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
