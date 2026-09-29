from typing import Optional, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import hashlib

from db.session import get_db
from app.models.rule import Rule, RuleSource
from app.schemas.pagination import PageResult, paginate_query
from app.core.security import generate_ulid

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("", response_model=PageResult[Any])
def list_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Rule).filter(Rule.deleted_at.is_(None))
    if isinstance(status, str) and status.strip():
        query = query.filter(Rule.status == status.strip())
    if isinstance(category, str) and category.strip():
        query = query.filter(Rule.category == category.strip())
    if isinstance(priority, str) and priority.strip():
        query = query.filter(Rule.priority == priority.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Rule.title.ilike(kw),
                Rule.summary.ilike(kw),
                Rule.group_name.ilike(kw),
                Rule.content.ilike(kw)
            )
        )
    query = query.order_by(desc(Rule.id))

    def serialize(r: Rule):
        return {
            "id": r.id,
            "public_id": r.public_id,
            "title": r.title,
            "category": r.category,
            "group_name": r.group_name,
            "priority": r.priority,
            "summary": r.summary,
            "content": r.content,
            "tags": r.tags,
            "globs": r.globs,
            "always_apply": r.always_apply,
            "status": r.status,
            "duplicate_count": r.duplicate_count,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page, page_size, serialize)

@router.get("/sources", response_model=PageResult[Any])
def list_rule_sources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(RuleSource)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                RuleSource.source_type.ilike(kw),
                RuleSource.source_ref.ilike(kw),
                RuleSource.source_heading.ilike(kw)
            )
        )
    query = query.order_by(desc(RuleSource.id))

    def serialize(s: RuleSource):
        return {
            "id": s.id,
            "public_id": s.public_id,
            "rule_id": s.rule_id,
            "source_type": s.source_type,
            "source_ref": s.source_ref,
            "source_uri": s.source_ref,
            "source_heading": s.source_heading,
            "source_key": s.source_key,
            "metadata": s.metadata_,
            "sync_status": "synced",
            "last_synced_at": s.imported_at.isoformat() if s.imported_at else None,
            "imported_at": s.imported_at.isoformat() if s.imported_at else None,
            "created_at": s.imported_at.isoformat() if s.imported_at else None
        }

    return paginate_query(query, page, page_size, serialize)

@router.post("")
def create_rule(payload: dict, db: Session = Depends(get_db)):
    content = payload.get("content", "")
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    rule = db.query(Rule).filter(Rule.content_hash == content_hash).first()
    if rule:
        rule.duplicate_count += 1
        db.commit()
        return {"status": "duplicate", "public_id": rule.public_id}

    public_id = generate_ulid("RULE")
    new_rule = Rule(
        public_id=public_id,
        title=payload.get("title", ""),
        summary=payload.get("summary"),
        content=content,
        category=payload.get("category", "general"),
        group_name=payload.get("group_name", "未分组"),
        priority=payload.get("priority", "medium"),
        content_hash=content_hash,
        globs=payload.get("globs", []),
        tags=payload.get("tags", []),
        always_apply=payload.get("always_apply", False),
        status="active"
    )
    db.add(new_rule)
    db.commit()
    return {"status": "created", "public_id": public_id}

