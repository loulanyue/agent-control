from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.session import get_db
from app.models.agent import Agent, ApiClient
from app.models.task import Task, TaskAttempt, TaskArtifact, TaskNote
from app.models.graph import GraphDefinition, GraphRun
from app.models.rule import Rule, RuleSource
from app.models.schedule import TaskSchedule, ScheduleRun
from app.models.extensions import (
    HzTalentNotice, HzNoticeCrawlRun,
    HfTalentRecord, HfTalentCrawlRun,
    GithubPrLifecycle, GithubContribution,
    PartTimeOpportunity, PartTimeScanRun,
    JobPosition, JobRequirement,
    SoftExamKnowledgePoint, SelfProjectIteration,
    BitcoinMiningRun,
    AgentArchitecturePosition, AgentArchitectureRequirement,
    QccCompanyBid, QccBidCrawlRun
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    获取全局 12 大业务模块的统计指标与数据量概览
    """
    return {
        "talent": {
            "total_notices": db.query(func.count(HzTalentNotice.id)).scalar() or 0,
            "crawl_runs": db.query(func.count(HzNoticeCrawlRun.id)).scalar() or 0,
            "personal_notices": db.query(func.count(HzTalentNotice.id)).filter(HzTalentNotice.notice_type == "personal").scalar() or 0,
            "list_notices": db.query(func.count(HzTalentNotice.id)).filter(HzTalentNotice.notice_type == "list").scalar() or 0
        },
        "hf_talent": {
            "total_records": db.query(func.count(HfTalentRecord.id)).filter(HfTalentRecord.record_type == "publicity").scalar() or 0,
            "publicity_records": db.query(func.count(HfTalentRecord.id)).filter(HfTalentRecord.record_type == "publicity").scalar() or 0,
            "crawl_runs": db.query(func.count(HfTalentCrawlRun.id)).scalar() or 0
        },
        "github": {
            "contributions": db.query(func.count(GithubContribution.id)).scalar() or 0,
            "security_advisories": db.query(func.count(GithubContribution.id)).filter(GithubContribution.is_security == 1).scalar() or 0,
            "prs_lifecycle": db.query(func.count(GithubPrLifecycle.id)).scalar() or 0,
            "prs_merged": db.query(func.count(GithubPrLifecycle.id)).filter(GithubPrLifecycle.state == "MERGED").scalar() or 0
        },
        "jobs": {
            "positions": db.query(func.count(JobPosition.id)).scalar() or 0,
            "requirements": db.query(func.count(JobRequirement.id)).scalar() or 0
        },
        "agent_arch": {
            "positions": db.query(func.count(AgentArchitecturePosition.id)).scalar() or 0,
            "requirements": db.query(func.count(AgentArchitectureRequirement.id)).scalar() or 0
        },
        "part_time": {
            "opportunities": db.query(func.count(PartTimeOpportunity.opportunity_id)).scalar() or 0,
            "active_opportunities": db.query(func.count(PartTimeOpportunity.opportunity_id)).filter(PartTimeOpportunity.status == "active").scalar() or 0,
            "scan_runs": db.query(func.count(PartTimeScanRun.run_id)).scalar() or 0
        },
        "soft_exam": {
            "knowledge_points": db.query(func.count(SoftExamKnowledgePoint.id)).scalar() or 0,
            "five_star_points": db.query(func.count(SoftExamKnowledgePoint.id)).filter(SoftExamKnowledgePoint.recommended_stars == 5).scalar() or 0
        },
        "self_project": {
            "iterations": db.query(func.count(SelfProjectIteration.id)).scalar() or 0
        },
        "bitcoin": {
            "mining_runs": db.query(func.count(BitcoinMiningRun.id)).scalar() or 0
        },
        "tasks": {
            "total_tasks": db.query(func.count(Task.id)).scalar() or 0,
            "completed_tasks": db.query(func.count(Task.id)).filter(Task.status == "completed").scalar() or 0,
            "attempts": db.query(func.count(TaskAttempt.id)).scalar() or 0,
            "artifacts": db.query(func.count(TaskArtifact.id)).scalar() or 0,
            "notes": db.query(func.count(TaskNote.id)).scalar() or 0
        },
        "agents": {
            "total_agents": db.query(func.count(Agent.id)).scalar() or 0,
            "online_agents": db.query(func.count(Agent.id)).filter(Agent.status == "online").scalar() or 0,
            "api_clients": db.query(func.count(ApiClient.id)).scalar() or 0
        },
        "graphs": {
            "definitions": db.query(func.count(GraphDefinition.id)).scalar() or 0,
            "runs": db.query(func.count(GraphRun.id)).scalar() or 0
        },
        "rules": {
            "total_rules": db.query(func.count(Rule.id)).scalar() or 0,
            "rule_sources": db.query(func.count(RuleSource.id)).scalar() or 0
        },
        "schedules": {
            "total_schedules": db.query(func.count(TaskSchedule.id)).scalar() or 0,
            "schedule_runs": db.query(func.count(ScheduleRun.id)).scalar() or 0
        },
        "qcc_bids": {
            "total_bids": db.query(func.count(QccCompanyBid.id)).scalar() or 0,
            "crawl_runs": db.query(func.count(QccBidCrawlRun.id)).scalar() or 0
        }
    }


