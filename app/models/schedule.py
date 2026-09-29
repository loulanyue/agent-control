from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Enum, ForeignKey, Integer, Boolean
from db.session import Base

class TaskSchedule(Base):
    __tablename__ = "task_schedules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(160), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    schedule_type = Column(Enum("once", "interval", "cron"), nullable=False, default="cron")
    run_at = Column(DateTime, nullable=True)
    interval_seconds = Column(Integer, nullable=True)
    cron_expression = Column(String(120), nullable=True)
    timezone = Column(String(80), nullable=False, default="Asia/Shanghai")
    task_template = Column(JSON, nullable=False)
    misfire_policy = Column(Enum("skip", "fire_once", "catch_up"), nullable=False, default="fire_once")
    overlap_policy = Column(Enum("forbid", "allow", "replace"), nullable=False, default="forbid")
    max_catch_up = Column(Integer, nullable=False, default=1)
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScheduleRun(Base):
    __tablename__ = "schedule_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    schedule_id = Column(BigInteger, ForeignKey("task_schedules.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    scheduled_for = Column(DateTime, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("created", "skipped", "failed"), nullable=False, default="created")
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
