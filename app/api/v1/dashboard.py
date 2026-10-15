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
    HzTalentNotice, HzHousingSubsidyRecord, HzNoticeCrawlRun,
    HfTalentRecord, HfTalentCrawlRun,
    GithubPrLifecycle, GithubContribution,
    PartTimeOpportunity, PartTimeScanRun,
    JobPosition, JobRequirement,
    SoftExamKnowledgePoint, SelfProjectIteration,
    BitcoinMiningRun,
    AgentArchitecturePosition, AgentArchitectureRequirement,
    QccCompanyBid, QccBidCrawlRun,
    TwitterFrontierTechPost
)
from app.models.contract import CodeContract, ContractRevision, ContractConsumer
from app.models.server_credential import ServerCredential, ServerAccessLog
from app.api.v1.servers import ensure_server_tables_initialized

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    获取全局业务模块的统计指标与数据量概览
    """
    ensure_server_tables_initialized(db)
    return {
        "talent": {
            "total_notices": db.query(func.count(HzTalentNotice.id)).scalar() or 0,
            "crawl_runs": db.query(func.count(HzNoticeCrawlRun.id)).scalar() or 0,
            "personal_notices": db.query(func.count(HzTalentNotice.id)).filter(HzTalentNotice.notice_type == "personal").scalar() or 0,
            "list_notices": db.query(func.count(HzTalentNotice.id)).filter(HzTalentNotice.notice_type == "list").scalar() or 0,
            "housing_subsidies": db.query(func.count(HzHousingSubsidyRecord.id)).scalar() or 0
        },
        "hf_talent": {
            "total_records": db.query(func.count(HfTalentRecord.id)).filter(HfTalentRecord.record_type == "publicity").scalar() or 0,
            "publicity_records": db.query(func.count(HfTalentRecord.id)).filter(HfTalentRecord.record_type == "publicity").scalar() or 0,
            "crawl_runs": db.query(func.count(HfTalentCrawlRun.id)).scalar() or 0
        },
        "github": {
            "contributions": db.query(func.count(GithubContribution.id)).filter(
                GithubContribution.repo_owner != "loulanyue",
                ~GithubContribution.pr_url.like("https://github.com/loulanyue/%")
            ).scalar() or 0,
            "security_advisories": db.query(func.count(GithubContribution.id)).filter(
                GithubContribution.is_security == 1,
                GithubContribution.repo_owner != "loulanyue",
                ~GithubContribution.pr_url.like("https://github.com/loulanyue/%")
            ).scalar() or 0,
            "prs_lifecycle": db.query(func.count(GithubPrLifecycle.id)).filter(
                GithubPrLifecycle.repo_owner != "loulanyue",
                ~GithubPrLifecycle.pr_url.like("https://github.com/loulanyue/%")
            ).scalar() or 0,
            "prs_merged": db.query(func.count(GithubPrLifecycle.id)).filter(
                GithubPrLifecycle.state == "MERGED",
                GithubPrLifecycle.repo_owner != "loulanyue",
                ~GithubPrLifecycle.pr_url.like("https://github.com/loulanyue/%")
            ).scalar() or 0
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
        },
        "frontier_tech": {
            "total_posts": db.query(func.count(TwitterFrontierTechPost.id)).scalar() or 0,
            "translated_posts": db.query(func.count(TwitterFrontierTechPost.id)).filter(
                TwitterFrontierTechPost.content_zh.isnot(None),
                TwitterFrontierTechPost.content_zh != ""
            ).scalar() or 0
        },
        "contracts": {
            "total_contracts": db.query(func.count(CodeContract.id)).scalar() or 0,
            "total_revisions": db.query(func.count(ContractRevision.id)).scalar() or 0,
            "total_consumers": db.query(func.count(ContractConsumer.id)).scalar() or 0,
            "frozen_contracts": db.query(func.count(CodeContract.id)).filter(CodeContract.is_breaking_frozen == True).scalar() or 0
        },
        "servers": {
            "total_servers": db.query(func.count(ServerCredential.id)).scalar() or 0,
            "active_servers": db.query(func.count(ServerCredential.id)).filter(ServerCredential.status == "active").scalar() or 0,
            "online_servers": db.query(func.count(ServerCredential.id)).filter(ServerCredential.last_check_status == "online").scalar() or 0,
            "access_logs": db.query(func.count(ServerAccessLog.id)).scalar() or 0
        }
    }


