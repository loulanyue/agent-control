from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.task import Task, TaskAttempt, TaskEvent, TaskArtifact
from app.models.agent import Agent
from app.schemas.task import TaskCreate, TaskClaimRequest, TaskHeartbeatRequest, TaskCompleteRequest
from app.core.security import generate_ulid
from app.core.config import settings

class TaskService:
    @staticmethod
    def create_task(db: Session, payload: TaskCreate, creator_id: str = "system") -> Task:
        public_id = generate_ulid("TASK")
        task = Task(
            public_id=public_id,
            external_id=payload.external_id,
            title=payload.title,
            objective=payload.objective,
            normative_constraint=payload.normative_constraint,
            instructions=payload.instructions,
            acceptance_criteria=payload.acceptance_criteria,
            context=payload.context,
            execution=payload.execution,
            metadata_=payload.metadata,
            priority=payload.priority,
            status="pending",
            source_type=payload.source_type,
            source_id=payload.source_id,
            due_at=payload.due_at,
            attempt_count=0,
            version=1
        )
        db.add(task)
        db.flush()

        event = TaskEvent(
            public_id=generate_ulid("TEVT"),
            task_id=task.id,
            event_type="task.created",
            actor_type="user" if creator_id != "system" else "system",
            actor_id=creator_id,
            from_status=None,
            to_status="pending",
            payload={"title": task.title, "priority": task.priority}
        )
        db.add(event)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def claim_task(db: Session, task_public_id: str, payload: TaskClaimRequest) -> TaskAttempt:
        agent = db.query(Agent).filter(Agent.public_id == payload.agent_public_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {payload.agent_public_id} not found")

        task = db.query(Task).filter(Task.public_id == task_public_id).with_for_update().first()
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_public_id} not found")

        now = datetime.utcnow()
        if task.status not in ["pending", "failed"]:
            if task.lease_expires_at and task.lease_expires_at > now:
                raise HTTPException(status_code=409, detail=f"Task is already claimed by {task.claimed_by}")

        req_caps = task.execution.get("required_capabilities", []) if task.execution else []
        agent_caps = set(agent.capabilities or [])
        for rc in req_caps:
            if rc not in agent_caps:
                raise HTTPException(
                    status_code=400,
                    detail=f"Agent missing required capability '{rc}'. Declared: {list(agent_caps)}"
                )

        lease_seconds = payload.lease_seconds or settings.DEFAULT_TASK_LEASE_SECONDS
        lease_expires = now + timedelta(seconds=lease_seconds)

        from_status = task.status
        task.status = "claimed"
        task.claimed_by = agent.public_id
        task.lease_expires_at = lease_expires
        task.attempt_count += 1
        task.version += 1

        attempt_id = generate_ulid("ATTEMPT")
        attempt = TaskAttempt(
            public_id=attempt_id,
            task_id=task.id,
            agent_id=agent.id,
            agent_public_id=agent.public_id,
            attempt_no=task.attempt_count,
            status="claimed",
            claimed_at=now,
            started_at=now,
            heartbeat_at=now,
            lease_expires_at=lease_expires,
            progress_percent=0,
            metadata_={}
        )
        db.add(attempt)
        db.flush()

        task.current_attempt_id = attempt.id

        event = TaskEvent(
            public_id=generate_ulid("TEVT"),
            task_id=task.id,
            attempt_id=attempt.id,
            event_type="task.claimed",
            actor_type="agent",
            actor_id=agent.public_id,
            from_status=from_status,
            to_status="claimed",
            payload={"attempt_no": task.attempt_count, "lease_expires_at": lease_expires.isoformat()}
        )
        db.add(event)
        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def heartbeat(db: Session, task_public_id: str, payload: TaskHeartbeatRequest) -> TaskAttempt:
        task = db.query(Task).filter(Task.public_id == task_public_id).first()
        if not task or not task.current_attempt_id:
            raise HTTPException(status_code=404, detail="Active task attempt not found")

        attempt = db.query(TaskAttempt).filter(TaskAttempt.id == task.current_attempt_id).with_for_update().first()
        if not attempt or attempt.status not in ["claimed", "running"]:
            raise HTTPException(status_code=400, detail="Attempt is not in active state")

        now = datetime.utcnow()
        lease_seconds = payload.lease_seconds or settings.DEFAULT_TASK_LEASE_SECONDS
        new_lease = now + timedelta(seconds=lease_seconds)

        attempt.heartbeat_at = now
        attempt.lease_expires_at = new_lease
        task.lease_expires_at = new_lease

        if payload.progress_percent is not None:
            attempt.progress_percent = payload.progress_percent
            attempt.status = "running"
            task.status = "running"

        if payload.summary:
            attempt.summary = payload.summary

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def complete_task(db: Session, task_public_id: str, payload: TaskCompleteRequest) -> Task:
        task = db.query(Task).filter(Task.public_id == task_public_id).with_for_update().first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.claimed_by != payload.agent_public_id:
            raise HTTPException(status_code=403, detail="Task was not claimed by this agent")

        now = datetime.utcnow()
        from_status = task.status
        task.status = "completed"
        task.completed_at = now
        task.lease_expires_at = None

        if task.current_attempt_id:
            attempt = db.query(TaskAttempt).filter(TaskAttempt.id == task.current_attempt_id).with_for_update().first()
            if attempt:
                attempt.status = "completed"
                attempt.finished_at = now
                attempt.progress_percent = 100
                attempt.summary = payload.summary
                attempt.result = payload.result

                for art in payload.artifacts:
                    artifact = TaskArtifact(
                        public_id=generate_ulid("ART"),
                        task_id=task.id,
                        attempt_id=attempt.id,
                        artifact_type=art.get("artifact_type", "output"),
                        name=art.get("name", "artifact"),
                        location=art.get("location", ""),
                        metadata_=art.get("metadata", {})
                    )
                    db.add(artifact)

        event = TaskEvent(
            public_id=generate_ulid("TEVT"),
            task_id=task.id,
            attempt_id=task.current_attempt_id,
            event_type="task.completed",
            actor_type="agent",
            actor_id=payload.agent_public_id,
            from_status=from_status,
            to_status="completed",
            payload={"summary": payload.summary, "artifacts_count": len(payload.artifacts)}
        )
        db.add(event)
        db.commit()
        db.refresh(task)
        return task
