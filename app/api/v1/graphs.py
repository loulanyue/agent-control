from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from datetime import datetime

from db.session import get_db
from app.models.graph import GraphDefinition, GraphVersion, GraphRun, GraphNodeRun
from app.schemas.pagination import PageResult, paginate_query
from app.core.security import generate_ulid

router = APIRouter(prefix="/graphs", tags=["Graphs & DAG"])

@router.get("", response_model=PageResult[Any])
def list_graphs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(GraphDefinition).filter(GraphDefinition.deleted_at.is_(None))
    if isinstance(status, str) and status.strip():
        query = query.filter(GraphDefinition.status == status.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                GraphDefinition.name.ilike(kw),
                GraphDefinition.description.ilike(kw),
                GraphDefinition.public_id.ilike(kw)
            )
        )
    query = query.order_by(desc(GraphDefinition.id))

    def serialize(g: GraphDefinition):
        return {
            "id": g.id,
            "public_id": g.public_id,
            "name": g.name,
            "description": g.description,
            "tags": g.tags,
            "status": g.status,
            "created_by": g.created_by,
            "created_at": g.created_at.isoformat() if g.created_at else None,
            "updated_at": g.updated_at.isoformat() if g.updated_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/runs", response_model=PageResult[Any])
def list_graph_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    graph_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(GraphRun)
    if isinstance(graph_id, int):
        query = query.filter(GraphRun.graph_id == graph_id)
    if isinstance(status, str) and status.strip():
        query = query.filter(GraphRun.status == status.strip())
    query = query.order_by(desc(GraphRun.id))

    def serialize(r: GraphRun):
        return {
            "id": r.id,
            "public_id": r.public_id,
            "graph_id": r.graph_id,
            "version_id": r.version_id,
            "status": r.status,
            "trigger_type": r.trigger_type,
            "trigger_id": r.trigger_id,
            "summary": r.summary,
            "error_message": r.error_message,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/{public_id}")
def get_graph(public_id: str, db: Session = Depends(get_db)):
    graph = db.query(GraphDefinition).filter(GraphDefinition.public_id == public_id).first()
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    versions = db.query(GraphVersion).filter(GraphVersion.graph_id == graph.id).all()
    return {
        "public_id": graph.public_id,
        "name": graph.name,
        "description": graph.description,
        "status": graph.status,
        "versions": [{
            "public_id": v.public_id,
            "version": v.version,
            "status": v.status,
            "execution_config": v.execution_config
        } for v in versions]
    }

@router.post("/{public_id}/runs")
def trigger_graph_run(public_id: str, payload: dict, db: Session = Depends(get_db)):
    graph = db.query(GraphDefinition).filter(GraphDefinition.public_id == public_id).first()
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    ver = db.query(GraphVersion).filter(GraphVersion.graph_id == graph.id).order_by(desc(GraphVersion.version)).first()
    if not ver:
        raise HTTPException(status_code=400, detail="Graph has no valid version")

    run_public_id = generate_ulid("GRUN")
    run = GraphRun(
        public_id=run_public_id,
        graph_id=graph.id,
        version_id=ver.id,
        status="running",
        trigger_type=payload.get("trigger_type", "api"),
        trigger_by=payload.get("trigger_by", "system"),
        input_payload=payload.get("input", {}),
        context_data={},
        started_at=datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {
        "run_public_id": run.public_id,
        "status": run.status,
        "started_at": run.started_at.isoformat()
    }

