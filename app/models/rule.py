from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Enum, ForeignKey, Integer, Boolean
from db.session import Base

class Rule(Base):
    __tablename__ = "rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    title = Column(String(240), nullable=False)
    summary = Column(String(1000), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(
        Enum("frontend", "backend", "fullstack", "general"),
        nullable=False,
        default="general"
    )
    group_name = Column(String(80), nullable=False, default="未分组")
    priority = Column(
        Enum("low", "medium", "high", "critical"),
        nullable=False,
        default="medium"
    )
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    globs = Column(JSON, nullable=False, default=list)
    tags = Column(JSON, nullable=False, default=list)
    always_apply = Column(Boolean, nullable=False, default=False)
    status = Column(Enum("active", "disabled"), nullable=False, default="active")
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(120), nullable=True)
    duplicate_count = Column(Integer, nullable=False, default=0)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RuleSource(Base):
    __tablename__ = "rule_sources"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    rule_id = Column(BigInteger, nullable=False)
    source_type = Column(String(80), nullable=False)
    source_ref = Column(String(1000), nullable=False)
    source_heading = Column(String(500), nullable=True)
    source_key = Column(String(64), nullable=False)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    imported_at = Column(DateTime, default=datetime.utcnow)

class TaskRule(Base):
    __tablename__ = "task_rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(BigInteger, ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
