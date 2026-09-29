from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., max_length=240)
    objective: str
    normative_constraint: Optional[str] = None
    instructions: List[Any] = Field(default_factory=list)
    acceptance_criteria: List[Any] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    execution: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    priority: str = Field(default="medium")
    source_type: str = Field(default="manual")
    source_id: Optional[str] = None
    external_id: Optional[str] = None
    due_at: Optional[datetime] = None

class TaskClaimRequest(BaseModel):
    agent_public_id: str
    lease_seconds: Optional[int] = 300

class TaskHeartbeatRequest(BaseModel):
    lease_seconds: Optional[int] = 300
    progress_percent: Optional[int] = None
    summary: Optional[str] = None

class TaskCompleteRequest(BaseModel):
    agent_public_id: str
    summary: Optional[str] = None
    result: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)

class TaskFailRequest(BaseModel):
    agent_public_id: str
    error_message: str
    summary: Optional[str] = None

class TaskResponse(BaseModel):
    public_id: str
    external_id: Optional[str] = None
    title: str
    objective: str
    normative_constraint: Optional[str] = None
    instructions: List[Any]
    acceptance_criteria: List[Any]
    context: Dict[str, Any]
    execution: Dict[str, Any]
    priority: str
    status: str
    claimed_by: Optional[str] = None
    lease_expires_at: Optional[datetime] = None
    attempt_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
