from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Enum, ForeignKey, Integer, SmallInteger, Numeric, Boolean
from sqlalchemy.orm import relationship
from db.session import Base

class GraphDefinition(Base):
    __tablename__ = "graph_definitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    status = Column(Enum("draft", "published", "disabled"), nullable=False, default="draft")
    current_draft_version_id = Column(BigInteger, nullable=True)
    current_published_version_id = Column(BigInteger, nullable=True)
    created_by = Column(String(120), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("GraphVersion", back_populates="graph", foreign_keys="GraphVersion.graph_id", cascade="all, delete-orphan")
    runs = relationship("GraphRun", back_populates="graph", cascade="all, delete-orphan")

class GraphVersion(Base):
    __tablename__ = "graph_versions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    graph_id = Column(BigInteger, ForeignKey("graph_definitions.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    status = Column(Enum("draft", "published", "archived"), nullable=False, default="published")
    input_schema = Column(JSON, nullable=False, default=dict)
    execution_config = Column(JSON, nullable=False, default=dict)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    changelog = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=False, default="system")
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    graph = relationship("GraphDefinition", back_populates="versions", foreign_keys=[graph_id])
    nodes = relationship("GraphNode", back_populates="version", cascade="all, delete-orphan")
    edges = relationship("GraphEdge", back_populates="version", cascade="all, delete-orphan")

class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    version_id = Column(BigInteger, ForeignKey("graph_versions.id", ondelete="CASCADE"), nullable=False)
    node_key = Column(String(80), nullable=False)
    node_type = Column(
        Enum("start", "end", "task", "decision", "parallel", "join", "approval", "custom"),
        nullable=False
    )
    title = Column(String(180), nullable=False)
    position_x = Column(Numeric(10, 3), nullable=False, default=0)
    position_y = Column(Numeric(10, 3), nullable=False, default=0)
    config = Column(JSON, nullable=False, default=dict)
    input_mapping = Column(JSON, nullable=False, default=dict)
    output_mapping = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    version = relationship("GraphVersion", back_populates="nodes")

class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    version_id = Column(BigInteger, ForeignKey("graph_versions.id", ondelete="CASCADE"), nullable=False)
    edge_key = Column(String(80), nullable=False)
    source_node_id = Column(BigInteger, ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id = Column(BigInteger, ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False)
    condition_expr = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    version = relationship("GraphVersion", back_populates="edges")

class GraphRun(Base):
    __tablename__ = "graph_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    graph_id = Column(BigInteger, ForeignKey("graph_definitions.id", ondelete="CASCADE"), nullable=False)
    version_id = Column(BigInteger, ForeignKey("graph_versions.id", ondelete="CASCADE"), nullable=False)
    parent_node_run_id = Column(BigInteger, nullable=True)
    status = Column(
        Enum("queued", "running", "paused", "completed", "failed", "cancelled"),
        nullable=False,
        default="queued"
    )
    trigger_type = Column(Enum("manual", "api", "schedule", "graph"), nullable=False, default="manual")
    trigger_id = Column(String(190), nullable=True)
    idempotency_key = Column(String(190), nullable=True)
    input_data = Column(JSON, nullable=False, default=dict)
    state_data = Column(JSON, nullable=False, default=dict)
    execution_policy = Column(JSON, nullable=False, default=dict)
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    graph = relationship("GraphDefinition", back_populates="runs")
    node_runs = relationship("GraphNodeRun", back_populates="graph_run", cascade="all, delete-orphan")
    events = relationship("GraphRunEvent", back_populates="graph_run", cascade="all, delete-orphan")

class GraphNodeRun(Base):
    __tablename__ = "graph_node_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    graph_run_id = Column(BigInteger, ForeignKey("graph_runs.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(BigInteger, ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False)
    node_key = Column(String(80), nullable=False)
    node_type = Column(String(40), nullable=False)
    status = Column(
        Enum("queued", "running", "waiting_approval", "completed", "failed", "skipped"),
        nullable=False,
        default="queued"
    )
    attempt_no = Column(Integer, nullable=False, default=1)
    input_data = Column(JSON, nullable=False, default=dict)
    output_data = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    graph_run = relationship("GraphRun", back_populates="node_runs")
    approvals = relationship("GraphApproval", back_populates="node_run", cascade="all, delete-orphan")

class GraphRunEvent(Base):
    __tablename__ = "graph_run_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    graph_run_id = Column(BigInteger, ForeignKey("graph_runs.id", ondelete="CASCADE"), nullable=False)
    node_run_id = Column(BigInteger, ForeignKey("graph_node_runs.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(80), nullable=False)
    level = Column(Enum("info", "warn", "error"), nullable=False, default="info")
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    graph_run = relationship("GraphRun", back_populates="events")

class GraphApproval(Base):
    __tablename__ = "graph_approvals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    node_run_id = Column(BigInteger, ForeignKey("graph_node_runs.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("pending", "approved", "rejected"), nullable=False, default="pending")
    requested_by = Column(String(120), nullable=False, default="system")
    reviewed_by = Column(String(120), nullable=True)
    review_comments = Column(Text, nullable=True)
    action_payload = Column(JSON, nullable=False, default=dict)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    node_run = relationship("GraphNodeRun", back_populates="approvals")
