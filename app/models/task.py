from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Enum, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import relationship
from db.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    external_id = Column(String(190), nullable=True)
    title = Column(String(240), nullable=False)
    objective = Column(Text, nullable=False)
    normative_constraint = Column(Text, nullable=True)
    instructions = Column(JSON, nullable=False, default=list)
    acceptance_criteria = Column(JSON, nullable=False, default=list)
    context = Column(JSON, nullable=False, default=dict)
    execution = Column(JSON, nullable=False, default=dict)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    priority = Column(
        Enum("low", "medium", "high", "critical"),
        nullable=False,
        default="medium"
    )
    status = Column(
        Enum("pending", "claimed", "running", "blocked", "review", "completed", "failed", "cancelled"),
        nullable=False,
        default="pending"
    )
    source_type = Column(
        Enum("manual", "api", "agent", "schedule", "webhook"),
        nullable=False,
        default="manual"
    )
    source_id = Column(String(190), nullable=True)
    schedule_id = Column(BigInteger, nullable=True)
    current_attempt_id = Column(BigInteger, nullable=True)
    claimed_by = Column(String(40), nullable=True)
    lease_expires_at = Column(DateTime, nullable=True)
    attempt_count = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    due_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attempts = relationship("TaskAttempt", back_populates="task", cascade="all, delete-orphan")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")
    artifacts = relationship("TaskArtifact", back_populates="task", cascade="all, delete-orphan")
    notes = relationship("TaskNote", back_populates="task", cascade="all, delete-orphan")

class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(BigInteger, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    agent_public_id = Column(String(40), nullable=False)
    attempt_no = Column(Integer, nullable=False)
    status = Column(
        Enum("claimed", "running", "blocked", "completed", "failed", "expired"),
        nullable=False,
        default="claimed"
    )
    claimed_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    heartbeat_at = Column(DateTime, nullable=True)
    lease_expires_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    progress_percent = Column(SmallInteger, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="attempts")
    agent = relationship("Agent", back_populates="attempts")
    artifacts = relationship("TaskArtifact", back_populates="attempt")

class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    attempt_id = Column(BigInteger, ForeignKey("task_attempts.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(80), nullable=False)
    actor_type = Column(
        Enum("user", "agent", "scheduler", "system"),
        nullable=False
    )
    actor_id = Column(String(80), nullable=True)
    from_status = Column(String(40), nullable=True)
    to_status = Column(String(40), nullable=True)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="events")

class TaskArtifact(Base):
    __tablename__ = "task_artifacts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    attempt_id = Column(BigInteger, ForeignKey("task_attempts.id", ondelete="SET NULL"), nullable=True)
    artifact_type = Column(String(40), nullable=False)
    name = Column(String(200), nullable=False)
    location = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="artifacts")
    attempt = relationship("TaskAttempt", back_populates="artifacts")

class TaskNote(Base):
    __tablename__ = "task_notes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    attempt_id = Column(BigInteger, ForeignKey("task_attempts.id", ondelete="SET NULL"), nullable=True)
    author_type = Column(Enum("user", "agent", "system"), nullable=False)
    author_id = Column(String(80), nullable=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def content(self):
        return self.body

    task = relationship("Task", back_populates="notes")

class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    depends_on_task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(40), nullable=False, default="blocks")
    created_at = Column(DateTime, default=datetime.utcnow)

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    endpoint = Column(String(120), nullable=False)
    response_code = Column(Integer, nullable=False)
    response_body = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
