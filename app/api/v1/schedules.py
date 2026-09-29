from typing import Optional, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from db.session import get_db
from app.models.schedule import TaskSchedule, ScheduleRun
from app.schemas.pagination import PageResult, paginate_query

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.get("", response_model=PageResult[Any])
def list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    enabled: Optional[bool] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TaskSchedule)
    if isinstance(enabled, bool):
        query = query.filter(TaskSchedule.enabled == enabled)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                TaskSchedule.name.ilike(kw),
                TaskSchedule.public_id.ilike(kw),
                TaskSchedule.cron_expression.ilike(kw)
            )
        )
    query = query.order_by(desc(TaskSchedule.id))

    def serialize(s: TaskSchedule):
        return {
            "id": s.id,
            "public_id": s.public_id,
            "name": s.name,
            "enabled": s.enabled,
            "schedule_type": s.schedule_type,
            "cron_expression": s.cron_expression,
            "interval_seconds": s.interval_seconds,
            "timezone": s.timezone,
            "misfire_policy": s.misfire_policy,
            "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None,
            "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }

    return paginate_query(query, page, page_size, serialize)

@router.get("/runs", response_model=PageResult[Any])
def list_schedule_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    schedule_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ScheduleRun)
    if isinstance(schedule_id, int):
        query = query.filter(ScheduleRun.schedule_id == schedule_id)
    if isinstance(status, str) and status.strip():
        query = query.filter(ScheduleRun.status == status.strip())
    query = query.order_by(desc(ScheduleRun.id))

    def serialize(r: ScheduleRun):
        return {
            "id": r.id,
            "public_id": r.public_id,
            "schedule_id": r.schedule_id,
            "task_id": r.task_id,
            "scheduled_for": r.scheduled_for.isoformat() if r.scheduled_for else None,
            "scheduled_time": r.scheduled_for.isoformat() if r.scheduled_for else None,
            "triggered_at": r.triggered_at.isoformat() if r.triggered_at else None,
            "status": r.status,
            "message": r.message,
            "error_message": r.message,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page, page_size, serialize)

