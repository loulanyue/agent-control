from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from db.session import get_db
from app.models.task import Task, TaskAttempt, TaskArtifact, TaskNote, TaskEvent
from app.schemas.task import (
    TaskCreate, TaskResponse, TaskClaimRequest, TaskHeartbeatRequest,
    TaskCompleteRequest
)
from app.schemas.pagination import PageResult, paginate_query
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=TaskResponse)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return TaskService.create_task(db, payload)

@router.get("", response_model=PageResult[Any])
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.deleted_at.is_(None))
    if isinstance(status, str) and status.strip():
        query = query.filter(Task.status == status.strip())
    if isinstance(priority, str) and priority.strip():
        query = query.filter(Task.priority == priority.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Task.title.ilike(kw),
                Task.public_id.ilike(kw),
                Task.objective.ilike(kw)
            )
        )
    query = query.order_by(desc(Task.id))

    def serialize(t: Task):
        return {
            "id": t.id,
            "public_id": t.public_id,
            "external_id": t.external_id,
            "title": t.title,
            "objective": t.objective,
            "priority": t.priority,
            "status": t.status,
            "source_type": t.source_type,
            "claimed_by": t.claimed_by,
            "attempt_count": t.attempt_count,
            "due_at": t.due_at.isoformat() if t.due_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/attempts", response_model=PageResult[Any])
def list_task_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TaskAttempt)
    if isinstance(task_id, int):
        query = query.filter(TaskAttempt.task_id == task_id)
    if isinstance(status, str) and status.strip():
        query = query.filter(TaskAttempt.status == status.strip())
    query = query.order_by(desc(TaskAttempt.id))

    def serialize(a: TaskAttempt):
        return {
            "id": a.id,
            "public_id": a.public_id,
            "task_id": a.task_id,
            "agent_public_id": a.agent_public_id,
            "attempt_no": a.attempt_no,
            "status": a.status,
            "progress_percent": a.progress_percent,
            "summary": a.summary,
            "lease_expires_at": a.lease_expires_at.isoformat() if a.lease_expires_at else None,
            "heartbeat_at": a.heartbeat_at.isoformat() if a.heartbeat_at else None,
            "finished_at": a.finished_at.isoformat() if a.finished_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/artifacts", response_model=PageResult[Any])
def list_task_artifacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TaskArtifact)
    if isinstance(task_id, int):
        query = query.filter(TaskArtifact.task_id == task_id)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                TaskArtifact.name.ilike(kw),
                TaskArtifact.artifact_type.ilike(kw)
            )
        )
    query = query.order_by(desc(TaskArtifact.id))

    def serialize(art: TaskArtifact):
        return {
            "id": art.id,
            "public_id": art.public_id,
            "task_id": art.task_id,
            "attempt_id": art.attempt_id,
            "name": art.name,
            "artifact_type": art.artifact_type,
            "location": art.location,
            "storage_uri": art.location,
            "metadata": art.metadata_,
            "created_at": art.created_at.isoformat() if art.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/notes", response_model=PageResult[Any])
def list_task_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TaskNote)
    if isinstance(task_id, int):
        query = query.filter(TaskNote.task_id == task_id)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                TaskNote.body.ilike(kw),
                TaskNote.public_id.ilike(kw),
                TaskNote.author_id.ilike(kw)
            )
        )
    query = query.order_by(desc(TaskNote.id))

    def serialize(n: TaskNote):
        return {
            "id": n.id,
            "public_id": n.public_id,
            "task_id": n.task_id,
            "attempt_id": n.attempt_id,
            "author_type": n.author_type,
            "author_id": n.author_id,
            "content": n.body,
            "body": n.body,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/{public_id}", response_model=TaskResponse)
def get_task(public_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.public_id == public_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{public_id}/claim")
def claim_task(public_id: str, payload: TaskClaimRequest, db: Session = Depends(get_db)):
    attempt = TaskService.claim_task(db, public_id, payload)
    return {
        "status": "success",
        "attempt_public_id": attempt.public_id,
        "attempt_no": attempt.attempt_no,
        "lease_expires_at": attempt.lease_expires_at
    }

@router.post("/{public_id}/heartbeat")
def task_heartbeat(public_id: str, payload: TaskHeartbeatRequest, db: Session = Depends(get_db)):
    attempt = TaskService.heartbeat(db, public_id, payload)
    return {
        "status": "success",
        "lease_expires_at": attempt.lease_expires_at,
        "progress_percent": attempt.progress_percent
    }

@router.post("/{public_id}/complete", response_model=TaskResponse)
def complete_task(public_id: str, payload: TaskCompleteRequest, db: Session = Depends(get_db)):
    return TaskService.complete_task(db, public_id, payload)

