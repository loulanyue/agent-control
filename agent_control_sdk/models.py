"""
Data models and typed structures for Agent Control SDK.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class Agent:
    id: Optional[int] = None
    public_id: Optional[str] = None
    name: str = ""
    agent_type: str = "general"
    status: str = "online"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen_at: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        return cls(
            id=data.get("id"),
            public_id=data.get("public_id"),
            name=data.get("name", ""),
            agent_type=data.get("agent_type", "general"),
            status=data.get("status", "online"),
            capabilities=data.get("capabilities") or [],
            metadata=data.get("metadata") or data.get("metadata_") or {},
            last_seen_at=data.get("last_seen_at"),
            created_at=data.get("created_at"),
        )

@dataclass
class Task:
    id: Optional[int] = None
    public_id: Optional[str] = None
    external_id: Optional[str] = None
    title: str = ""
    objective: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"
    source_type: str = "api"
    claimed_by: Optional[int] = None
    attempt_count: int = 0
    due_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=data.get("id"),
            public_id=data.get("public_id"),
            external_id=data.get("external_id"),
            title=data.get("title", ""),
            objective=data.get("objective"),
            priority=data.get("priority", "normal"),
            status=data.get("status", "pending"),
            source_type=data.get("source_type", "api"),
            claimed_by=data.get("claimed_by"),
            attempt_count=data.get("attempt_count", 0),
            due_at=data.get("due_at"),
            completed_at=data.get("completed_at"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

@dataclass
class GraphDefinition:
    id: Optional[int] = None
    public_id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    status: str = "active"
    created_by: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphDefinition":
        return cls(
            id=data.get("id"),
            public_id=data.get("public_id"),
            name=data.get("name", ""),
            description=data.get("description"),
            tags=data.get("tags") or [],
            status=data.get("status", "active"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
        )

@dataclass
class GraphRun:
    id: Optional[int] = None
    public_id: Optional[str] = None
    graph_id: Optional[int] = None
    status: str = "pending"
    trigger_type: str = "manual"
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphRun":
        return cls(
            id=data.get("id"),
            public_id=data.get("public_id"),
            graph_id=data.get("graph_id"),
            status=data.get("status", "pending"),
            trigger_type=data.get("trigger_type", "manual"),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
        )

@dataclass
class SystemMetrics:
    total_agents: int = 0
    online_agents: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    total_graphs: int = 0
    raw_stats: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemMetrics":
        agents_data = data.get("agents", {})
        tasks_data = data.get("tasks", {})
        graphs_data = data.get("graphs", {})
        return cls(
            total_agents=agents_data.get("total_agents", 0),
            online_agents=agents_data.get("online_agents", 0),
            total_tasks=tasks_data.get("total_tasks", 0),
            completed_tasks=tasks_data.get("completed_tasks", 0),
            total_graphs=graphs_data.get("definitions", 0),
            raw_stats=data,
        )
