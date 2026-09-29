from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AgentRegister(BaseModel):
    name: str = Field(..., max_length=120)
    agent_type: str = Field(default="generic", max_length=80)
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentHeartbeat(BaseModel):
    status: Optional[str] = Field(default="online")
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    public_id: str
    name: str
    agent_type: str
    capabilities: List[str]
    status: str
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApiClientCreate(BaseModel):
    name: str = Field(..., max_length=120)
    scopes: List[str] = Field(default_factory=lambda: ["task:read", "task:claim", "task:write"])

class ApiClientResponse(BaseModel):
    public_id: str
    name: str
    scopes: List[str]
    raw_token: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
