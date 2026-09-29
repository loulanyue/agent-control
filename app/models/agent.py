from datetime import datetime
from sqlalchemy import Column, BigInteger, String, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from db.session import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    agent_type = Column(String(80), nullable=False, default="generic")
    capabilities = Column(JSON, nullable=False, default=list)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    status = Column(
        Enum("online", "offline", "busy", "disabled"),
        nullable=False,
        default="offline"
    )
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attempts = relationship("TaskAttempt", back_populates="agent")

class ApiClient(Base):
    __tablename__ = "api_clients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    token_hash = Column(String(64), nullable=False)
    scopes = Column(JSON, nullable=False, default=list)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
