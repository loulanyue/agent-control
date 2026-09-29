from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from datetime import datetime

from db.session import get_db
from app.models.agent import Agent, ApiClient
from app.schemas.agent import AgentRegister, AgentHeartbeat, AgentResponse
from app.schemas.pagination import PageResult, paginate_query
from app.core.security import generate_ulid

router = APIRouter(prefix="/agents", tags=["Agents & Clients"])

@router.post("", response_model=AgentResponse)
def register_agent(payload: AgentRegister, db: Session = Depends(get_db)):
    public_id = generate_ulid("AGENT")
    agent = Agent(
        public_id=public_id,
        name=payload.name,
        agent_type=payload.agent_type,
        capabilities=payload.capabilities,
        metadata_=payload.metadata,
        status="online",
        last_seen_at=datetime.utcnow()
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@router.get("", response_model=PageResult[Any])
def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Agent)
    if isinstance(status, str) and status.strip():
        query = query.filter(Agent.status == status.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Agent.name.ilike(kw),
                Agent.public_id.ilike(kw),
                Agent.agent_type.ilike(kw)
            )
        )
    query = query.order_by(desc(Agent.id))

    def serialize(a: Agent):
        return {
            "id": a.id,
            "public_id": a.public_id,
            "name": a.name,
            "agent_type": a.agent_type,
            "capabilities": a.capabilities,
            "metadata": a.metadata_,
            "status": a.status,
            "last_seen_at": a.last_seen_at.isoformat() if a.last_seen_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        }

    return paginate_query(query, page, page_size, serialize)

@router.get("/api-clients", response_model=PageResult[Any])
def list_api_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ApiClient)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                ApiClient.name.ilike(kw),
                ApiClient.public_id.ilike(kw)
            )
        )
    query = query.order_by(desc(ApiClient.id))

    def serialize(c: ApiClient):
        return {
            "id": c.id,
            "public_id": c.public_id,
            "name": c.name,
            "token_hash": c.token_hash[:8] + "..." if c.token_hash else "",
            "scopes": c.scopes,
            "last_used_at": c.last_used_at.isoformat() if c.last_used_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }

    return paginate_query(query, page, page_size, serialize)

@router.get("/{public_id}", response_model=AgentResponse)
def get_agent(public_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.public_id == public_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/{public_id}/heartbeat", response_model=AgentResponse)
def agent_heartbeat(public_id: str, payload: AgentHeartbeat, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.public_id == public_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.last_seen_at = datetime.utcnow()
    if payload.status:
        agent.status = payload.status
    if payload.capabilities is not None:
        agent.capabilities = payload.capabilities
    if payload.metadata is not None:
        agent.metadata_ = payload.metadata

    db.commit()
    db.refresh(agent)
    return agent

