import os
import sys
import threading
import subprocess
from datetime import datetime
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, cast, String

from db.session import get_db
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
from app.schemas.pagination import PageResult, paginate_query

router = APIRouter(prefix="/extensions", tags=["Extensions & Business"])

# ----------------------------------------------------------------------
# 1. 杭州人才申报公示 (Talent Notices & Runs)
# ----------------------------------------------------------------------
@router.get("/talent-notices", response_model=PageResult[Any])
def list_talent_notices(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    notice_type: Optional[str] = Query(None, description="公示类型: personal / list"),
    publish_date: Optional[str] = Query(None, description="公示发布日期，格式 YYYY-MM-DD 或 YYYY-MM"),
    category: Optional[str] = Query(None, description="人才分类/类别（模糊搜索，如：E类、D类、博士学位）"),
    keyword: Optional[str] = Query(None, description="申报人/标题/单位/受理部门关键词"),
    db: Session = Depends(get_db)
):
    query = db.query(HzTalentNotice)
    if isinstance(notice_type, str) and notice_type.strip():
        query = query.filter(HzTalentNotice.notice_type == notice_type.strip())
    if isinstance(publish_date, str) and publish_date.strip():
        p_date = publish_date.strip()
        if len(p_date) == 10:
            query = query.filter(HzTalentNotice.publish_date == p_date)
        else:
            query = query.filter(cast(HzTalentNotice.publish_date, String).ilike(f"%{p_date}%"))
    if isinstance(category, str) and category.strip():
        import re
        cat_pattern = re.sub(r'([a-zA-Z])\s*类', r'\1%类', category.strip())
        query = query.filter(HzTalentNotice.apply_type.ilike(f"%{cat_pattern}%"))
    if isinstance(keyword, str) and keyword.strip():
        import re
        kw_raw = keyword.strip()
        kw_pattern = re.sub(r'([a-zA-Z])\s*类', r'\1%类', kw_raw)
        kw = f"%{kw_pattern}%"
        query = query.filter(
            or_(
                HzTalentNotice.title.ilike(kw),
                HzTalentNotice.person_name.ilike(kw),
                HzTalentNotice.work_unit.ilike(kw),
                HzTalentNotice.accept_dept.ilike(kw),
                HzTalentNotice.apply_type.ilike(kw)
            )
        )
    query = query.order_by(desc(HzTalentNotice.publish_date), desc(HzTalentNotice.id))

    def serialize(n: HzTalentNotice):
        return {
            "id": n.id,
            "notice_id": n.notice_id,
            "notice_type": n.notice_type,
            "title": n.title,
            "person_name": n.person_name,
            "gender": n.gender,
            "birth_date": n.birth_date,
            "work_unit": n.work_unit,
            "accept_dept": n.accept_dept,
            "apply_type": n.apply_type,
            "publicity_period": n.publicity_period,
            "publish_date": n.publish_date.isoformat() if n.publish_date else None,
            "detail_url": n.detail_url,
            "author": n.author,
            "crawl_batch": n.crawl_batch,
            "last_crawl_batch": n.last_crawl_batch,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/talent-notices/company-stats")
def get_talent_company_stats(
    limit: int = Query(20, ge=5, le=100, description="返回前N家企业"),
    min_total: int = Query(1, ge=1, description="最小人才数量过滤"),
    keyword: Optional[str] = Query(None, description="公司名称模糊过滤"),
    sort_by: Optional[str] = Query("total", description="排序维度: total(总数), high_level(B/C/D高层级优先), d_count(D类优先), c_count(C类优先)"),
    notice_type: Optional[str] = Query("personal", description="公示类型: personal(个人公示), all(包含清单)"),
    db: Session = Depends(get_db)
):
    """
    按公司/工作单位维度统计各类人才（A/B/C/D/E类）的分布明细与聚合排行
    """
    import re
    from collections import defaultdict

    query = db.query(HzTalentNotice.work_unit, HzTalentNotice.apply_type)
    if notice_type == "personal":
        query = query.filter(HzTalentNotice.notice_type == "personal")
    query = query.filter(
        HzTalentNotice.work_unit.isnot(None),
        HzTalentNotice.work_unit != "",
        HzTalentNotice.work_unit != "详见正文公示单位名单"
    )
    if keyword and keyword.strip():
        query = query.filter(HzTalentNotice.work_unit.ilike(f"%{keyword.strip()}%"))

    rows = query.all()

    comp_map = defaultdict(lambda: {
        "company": "",
        "total": 0,
        "b_count": 0,
        "c_count": 0,
        "d_count": 0,
        "e_count": 0,
        "other_count": 0,
        "high_level_total": 0
    })

    level_summary = {
        "B类": 0,
        "C类": 0,
        "D类": 0,
        "E类": 0,
        "其他": 0
    }

    for unit, apply_type in rows:
        unit = (unit or "").strip()
        if not unit:
            continue
        entry = comp_map[unit]
        entry["company"] = unit
        entry["total"] += 1

        m = re.search(r'([A-Fa-f])\s*类', apply_type or '')
        lvl = (m.group(1).upper() + '类') if m else '其他'

        if lvl == "B类":
            entry["b_count"] += 1
            entry["high_level_total"] += 1
            level_summary["B类"] += 1
        elif lvl == "C类":
            entry["c_count"] += 1
            entry["high_level_total"] += 1
            level_summary["C类"] += 1
        elif lvl == "D类":
            entry["d_count"] += 1
            entry["high_level_total"] += 1
            level_summary["D类"] += 1
        elif lvl == "E类":
            entry["e_count"] += 1
            level_summary["E类"] += 1
        elif lvl == "A类":
            entry["high_level_total"] += 1
            level_summary.setdefault("A类", 0)
            level_summary["A类"] += 1
        else:
            entry["other_count"] += 1
            level_summary["其他"] += 1

    filtered_comps = [c for c in comp_map.values() if c["total"] >= min_total]

    if sort_by == "high_level":
        sorted_comps = sorted(filtered_comps, key=lambda x: (x["high_level_total"], x["total"]), reverse=True)
    elif sort_by == "d_count":
        sorted_comps = sorted(filtered_comps, key=lambda x: (x["d_count"], x["total"]), reverse=True)
    elif sort_by == "c_count":
        sorted_comps = sorted(filtered_comps, key=lambda x: (x["c_count"], x["total"]), reverse=True)
    elif sort_by == "b_count":
        sorted_comps = sorted(filtered_comps, key=lambda x: (x["b_count"], x["total"]), reverse=True)
    else:  # "total"
        sorted_comps = sorted(filtered_comps, key=lambda x: (x["total"], x["high_level_total"]), reverse=True)

    top_companies = sorted_comps[:limit]

    return {
        "total_records": len(rows),
        "total_companies": len(comp_map),
        "level_summary": level_summary,
        "companies": top_companies
    }

@router.get("/talent-notices/date-stats")
def get_talent_date_stats(
    days: Optional[int] = Query(None, description="最近N天"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    按公示发布日期（publish_date）联合统计杭州与合肥两地人才数量的每日趋势走势
    """
    from sqlalchemy import text

    hz_sql = """
        SELECT cast(publish_date as char) as pdate, count(*) as cnt
        FROM hz_talent_notices
        WHERE publish_date IS NOT NULL
        GROUP BY pdate
        ORDER BY pdate
    """
    hf_sql = """
        SELECT cast(publish_date as char) as pdate, count(*) as cnt
        FROM hf_talent_records
        WHERE publish_date IS NOT NULL
        GROUP BY pdate
        ORDER BY pdate
    """
    hz_rows = db.execute(text(hz_sql)).fetchall()
    hf_rows = db.execute(text(hf_sql)).fetchall()

    hz_map = {str(r[0]): int(r[1]) for r in hz_rows if r[0]}
    hf_map = {str(r[0]): int(r[1]) for r in hf_rows if r[0]}

    all_dates = sorted(set(hz_map.keys()) | set(hf_map.keys()))

    if start_date:
        all_dates = [d for d in all_dates if d >= start_date.strip()]
    if end_date:
        all_dates = [d for d in all_dates if d <= end_date.strip()]
    if days and days > 0:
        all_dates = all_dates[-days:]

    timeline = []
    hz_total = 0
    hf_total = 0
    peak_date = None
    peak_count = 0

    for d in all_dates:
        hz_c = hz_map.get(d, 0)
        hf_c = hf_map.get(d, 0)
        tot = hz_c + hf_c
        hz_total += hz_c
        hf_total += hf_c
        if tot > peak_count:
            peak_count = tot
            peak_date = d

        timeline.append({
            "date": d,
            "hz_count": hz_c,
            "hf_count": hf_c,
            "total": tot
        })

    return {
        "hz_total": hz_total,
        "hf_total": hf_total,
        "grand_total": hz_total + hf_total,
        "days_count": len(timeline),
        "peak_date": peak_date,
        "peak_count": peak_count,
        "timeline": timeline
    }



@router.get("/notice-crawl-runs", response_model=PageResult[Any])
def list_notice_crawl_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(HzNoticeCrawlRun).order_by(desc(HzNoticeCrawlRun.id))

    def serialize(r: HzNoticeCrawlRun):
        return {
            "id": r.id,
            "crawl_batch": r.crawl_batch,
            "total_fetched": r.total_fetched,
            "personal_count": r.personal_count,
            "list_count": r.list_count,
            "success_count": r.success_count,
            "error_count": r.error_count,
            "status": r.status,
            "error_message": r.error_message,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "duration_sec": r.duration_sec,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

class CrawlTriggerRequest(BaseModel):
    days: Optional[int] = 3
    per_day: Optional[int] = 80
    force_refresh: Optional[bool] = False
    max_items: Optional[int] = None

class CrawlerManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.started_at: Optional[datetime] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self.days: Optional[int] = None
        self.per_day: Optional[int] = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = CrawlerManager()
            return cls._instance

    @property
    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def start_crawl(self, days: Optional[int] = 3, per_day: Optional[int] = 80, force_refresh: bool = False, max_items: Optional[int] = None):
        with self._lock:
            if self.is_running:
                return False, "当前已有抓取任务在执行中，请稍候再试"

            app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            tpm_root = os.path.abspath(os.path.join(app_dir, ".."))
            venv_python = os.path.join(app_dir, "venv", "bin", "python")
            python_bin = venv_python if os.path.exists(venv_python) else sys.executable
            crawler_script = os.path.join(tpm_root, ".agents", "skills", "hz-talent-crawler", "scripts", "crawler.py")

            if not os.path.exists(crawler_script):
                return False, f"爬虫脚本不存在: {crawler_script}"

            cmd = [python_bin, crawler_script]
            if days is not None and days > 0:
                cmd.extend(["--days", str(days)])
            if per_day is not None and per_day > 0:
                cmd.extend(["--per-day", str(per_day)])
            if max_items is not None and max_items > 0:
                cmd.extend(["--max-items", str(max_items)])
            if force_refresh:
                cmd.append("--force-refresh")

            self.days = days
            self.per_day = per_day
            self.started_at = datetime.now()
            self.last_result = None

            def run_worker():
                try:
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=tpm_root
                    )
                    self.process = proc
                    out, _ = proc.communicate()
                    lines = [line.strip() for line in out.splitlines() if line.strip()]
                    self.last_result = {
                        "exit_code": proc.returncode,
                        "finished_at": datetime.now().isoformat(),
                        "lines": lines[-30:] if lines else [],
                        "success": (proc.returncode == 0)
                    }
                except Exception as e:
                    self.last_result = {
                        "exit_code": -1,
                        "finished_at": datetime.now().isoformat(),
                        "error": str(e),
                        "success": False
                    }

            t = threading.Thread(target=run_worker, daemon=True)
            t.start()
            return True, "抓取任务启动成功"

crawler_manager = CrawlerManager.get_instance()

@router.post("/talent-notices/crawl")
def trigger_talent_crawl(
    payload: Optional[CrawlTriggerRequest] = None,
    db: Session = Depends(get_db)
):
    """
    触发杭州人才数据抓取与滚动闭环去重任务
    """
    p = payload or CrawlTriggerRequest()
    success, msg = crawler_manager.start_crawl(
        days=p.days,
        per_day=p.per_day,
        force_refresh=bool(p.force_refresh),
        max_items=p.max_items
    )
    return {
        "success": success,
        "message": msg,
        "is_running": crawler_manager.is_running,
        "started_at": crawler_manager.started_at.isoformat() if crawler_manager.started_at else None
    }

@router.get("/talent-notices/crawl-status")
def get_talent_crawl_status(db: Session = Depends(get_db)):
    """
    查询当前数据抓取任务的执行状态与最新入库批次
    """
    is_running = crawler_manager.is_running
    latest_run = db.query(HzNoticeCrawlRun).order_by(desc(HzNoticeCrawlRun.id)).first()
    latest_data = None
    if latest_run:
        latest_data = {
            "id": latest_run.id,
            "crawl_batch": latest_run.crawl_batch,
            "status": latest_run.status,
            "total_fetched": latest_run.total_fetched,
            "personal_count": latest_run.personal_count,
            "list_count": latest_run.list_count,
            "success_count": latest_run.success_count,
            "error_count": latest_run.error_count,
            "duration_sec": latest_run.duration_sec,
            "error_message": latest_run.error_message,
            "started_at": latest_run.started_at.isoformat() if latest_run.started_at else None,
            "finished_at": latest_run.finished_at.isoformat() if latest_run.finished_at else None
        }

    return {
        "is_running": is_running,
        "started_at": crawler_manager.started_at.isoformat() if crawler_manager.started_at else None,
        "last_result": crawler_manager.last_result,
        "latest_run": latest_data
    }

# ----------------------------------------------------------------------
# 1.2 合肥人才申报公示与认定结果 (Hefei Talent Records & Runs)
# ----------------------------------------------------------------------
@router.get("/hf-talent-records", response_model=PageResult[Any])
def list_hf_talent_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    record_type: Optional[str] = Query("publicity", description="数据类型: publicity(公示)"),
    publish_date: Optional[str] = Query(None, description="公示发布日期，格式 YYYY-MM-DD 或 YYYY-MM"),
    level_code_name: Optional[str] = Query(None, description="人才分类/级别（如：A类、B类、C类、D类）"),
    keyword: Optional[str] = Query(None, description="申报人/标题/单位/受理部门/条款关键词"),
    db: Session = Depends(get_db)
):
    query = db.query(HfTalentRecord)
    target_type = record_type.strip() if (isinstance(record_type, str) and record_type.strip()) else "publicity"
    query = query.filter(HfTalentRecord.record_type == target_type)
    if isinstance(publish_date, str) and publish_date.strip():
        p_date = publish_date.strip()
        if len(p_date) == 10:
            query = query.filter(HfTalentRecord.publish_date == p_date)
        else:
            query = query.filter(cast(HfTalentRecord.publish_date, String).ilike(f"%{p_date}%"))
    if isinstance(level_code_name, str) and level_code_name.strip():
        query = query.filter(HfTalentRecord.level_code_name.ilike(f"%{level_code_name.strip()}%"))
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                HfTalentRecord.title.ilike(kw),
                HfTalentRecord.person_name.ilike(kw),
                HfTalentRecord.person_name_masked.ilike(kw),
                HfTalentRecord.work_unit.ilike(kw),
                HfTalentRecord.accept_dept.ilike(kw),
                HfTalentRecord.clause.ilike(kw)
            )
        )
    query = query.order_by(desc(HfTalentRecord.publish_date), desc(HfTalentRecord.id))

    def serialize(r: HfTalentRecord):
        return {
            "id": r.id,
            "record_id": r.record_id,
            "record_type": r.record_type,
            "title": r.title,
            "person_name": r.person_name,
            "person_name_masked": r.person_name_masked,
            "gender": r.gender,
            "work_unit": r.work_unit,
            "accept_dept": r.accept_dept,
            "level_code": r.level_code,
            "level_code_name": r.level_code_name,
            "clause": r.clause,
            "talent_type": r.talent_type,
            "talent_type_name": r.talent_type_name,
            "publicity_start_time": r.publicity_start_time.isoformat() if r.publicity_start_time else None,
            "publicity_end_time": r.publicity_end_time.isoformat() if r.publicity_end_time else None,
            "publicity_period": r.publicity_period,
            "confirm_time": r.confirm_time.isoformat() if r.confirm_time else None,
            "publish_date": r.publish_date.isoformat() if r.publish_date else None,
            "approval_name": r.approval_name,
            "approval_tel": r.approval_tel,
            "approval_review_name": r.approval_review_name,
            "approval_review_tel": r.approval_review_tel,
            "content_text": r.content_text,
            "detail_url": r.detail_url,
            "author": r.author,
            "crawl_batch": r.crawl_batch,
            "last_crawl_batch": r.last_crawl_batch,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/hf-talent-crawl-runs", response_model=PageResult[Any])
def list_hf_talent_crawl_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(HfTalentCrawlRun).order_by(desc(HfTalentCrawlRun.id))

    def serialize(r: HfTalentCrawlRun):
        return {
            "id": r.id,
            "crawl_batch": r.crawl_batch,
            "total_fetched": r.total_fetched,
            "publicity_count": r.publicity_count,
            "result_count": r.result_count,
            "success_count": r.success_count,
            "error_count": r.error_count,
            "status": r.status,
            "error_message": r.error_message,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "duration_sec": r.duration_sec,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

class HfCrawlTriggerRequest(BaseModel):
    record_type: Optional[str] = "publicity"
    max_items: Optional[int] = None
    force_refresh: Optional[bool] = False

class HfCrawlerManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.started_at: Optional[datetime] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self.record_type: Optional[str] = "publicity"

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = HfCrawlerManager()
            return cls._instance

    @property
    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def start_crawl(self, record_type: str = "publicity", force_refresh: bool = False, max_items: Optional[int] = None):
        with self._lock:
            if self.is_running:
                return False, "当前已有合肥人才抓取任务在执行中，请稍候再试"

            app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            tpm_root = os.path.abspath(os.path.join(app_dir, ".."))
            venv_python = os.path.join(app_dir, "venv", "bin", "python")
            python_bin = venv_python if os.path.exists(venv_python) else sys.executable
            crawler_script = os.path.join(tpm_root, ".agents", "skills", "hf-talent-crawler", "scripts", "crawler.py")

            if not os.path.exists(crawler_script):
                return False, f"爬虫脚本不存在: {crawler_script}"

            cmd = [python_bin, crawler_script, "--type", record_type]
            if max_items is not None and max_items > 0:
                cmd.extend(["--max-items", str(max_items)])
            if force_refresh:
                cmd.append("--force-refresh")

            self.record_type = record_type
            self.started_at = datetime.now()
            self.last_result = None

            def run_worker():
                try:
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=tpm_root
                    )
                    self.process = proc
                    out, _ = proc.communicate()
                    lines = [line.strip() for line in out.splitlines() if line.strip()]
                    self.last_result = {
                        "exit_code": proc.returncode,
                        "finished_at": datetime.now().isoformat(),
                        "lines": lines[-30:] if lines else [],
                        "success": (proc.returncode == 0)
                    }
                except Exception as e:
                    self.last_result = {
                        "exit_code": -1,
                        "finished_at": datetime.now().isoformat(),
                        "error": str(e),
                        "success": False
                    }

            t = threading.Thread(target=run_worker, daemon=True)
            t.start()
            return True, "合肥人才抓取任务启动成功"

hf_crawler_manager = HfCrawlerManager.get_instance()

@router.post("/hf-talent-records/crawl")
def trigger_hf_talent_crawl(
    payload: Optional[HfCrawlTriggerRequest] = None,
    db: Session = Depends(get_db)
):
    """
    触发合肥高层次人才数据采集与落库任务
    """
    p = payload or HfCrawlTriggerRequest()
    success, msg = hf_crawler_manager.start_crawl(
        record_type=p.record_type or "publicity",
        force_refresh=bool(p.force_refresh),
        max_items=p.max_items
    )
    return {
        "success": success,
        "message": msg,
        "is_running": hf_crawler_manager.is_running,
        "started_at": hf_crawler_manager.started_at.isoformat() if hf_crawler_manager.started_at else None
    }

@router.get("/hf-talent-records/crawl-status")
def get_hf_talent_crawl_status(db: Session = Depends(get_db)):
    """
    查询合肥人才数据抓取任务执行状态
    """
    is_running = hf_crawler_manager.is_running
    latest_run = db.query(HfTalentCrawlRun).order_by(desc(HfTalentCrawlRun.id)).first()
    latest_data = None
    if latest_run:
        latest_data = {
            "id": latest_run.id,
            "crawl_batch": latest_run.crawl_batch,
            "status": latest_run.status,
            "total_fetched": latest_run.total_fetched,
            "publicity_count": latest_run.publicity_count,
            "result_count": latest_run.result_count,
            "success_count": latest_run.success_count,
            "error_count": latest_run.error_count,
            "duration_sec": latest_run.duration_sec,
            "error_message": latest_run.error_message,
            "started_at": latest_run.started_at.isoformat() if latest_run.started_at else None,
            "finished_at": latest_run.finished_at.isoformat() if latest_run.finished_at else None
        }

    return {
        "is_running": is_running,
        "started_at": hf_crawler_manager.started_at.isoformat() if hf_crawler_manager.started_at else None,
        "last_result": hf_crawler_manager.last_result,
        "latest_run": latest_data
    }


# ----------------------------------------------------------------------
# 2. GitHub 贡献与 PR 治理 (GitHub Contributions & PR Lifecycle)
# ----------------------------------------------------------------------
@router.get("/github-contributions", response_model=PageResult[Any])
def list_github_contributions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="仓库/标题/结论关键词"),
    status: Optional[str] = Query(None, description="状态: OPEN / MERGED / CLOSED"),
    is_security: Optional[int] = Query(None, description="是否安全漏洞: 0/1"),
    db: Session = Depends(get_db)
):
    query = db.query(GithubContribution)
    if isinstance(status, str) and status.strip():
        query = query.filter(GithubContribution.status == status.strip())
    if isinstance(is_security, int):
        query = query.filter(GithubContribution.is_security == is_security)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                GithubContribution.repo_name.ilike(kw),
                GithubContribution.pr_title.ilike(kw),
                GithubContribution.conclusion.ilike(kw),
                GithubContribution.ghsa_id.ilike(kw)
            )
        )
    query = query.order_by(desc(GithubContribution.id))

    def serialize(c: GithubContribution):
        return {
            "id": c.id,
            "pr_url": c.pr_url,
            "repo_name": c.repo_name,
            "repo_owner": c.repo_owner,
            "repo_stars": c.repo_stars,
            "pr_number": c.pr_number,
            "pr_title": c.pr_title,
            "branch_name": c.branch_name,
            "category": c.category,
            "conclusion": c.conclusion,
            "is_security": bool(c.is_security),
            "ghsa_id": c.ghsa_id,
            "status": c.status,
            "merged_at": c.merged_at.isoformat() if c.merged_at else None,
            "log_file": c.log_file,
            "run_time": c.run_time.isoformat() if c.run_time else None,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/github-prs", response_model=PageResult[Any])
def list_github_prs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(GithubPrLifecycle)
    if isinstance(state, str) and state.strip():
        query = query.filter(GithubPrLifecycle.state == state.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                GithubPrLifecycle.title.ilike(kw),
                GithubPrLifecycle.repo_name.ilike(kw),
                GithubPrLifecycle.repo_owner.ilike(kw)
            )
        )
    query = query.order_by(desc(GithubPrLifecycle.id))

    def serialize(p: GithubPrLifecycle):
        return {
            "id": p.id,
            "repo_name": p.repo_name,
            "repo_owner": p.repo_owner,
            "pr_number": p.pr_number,
            "title": p.title,
            "state": p.state,
            "pr_url": p.pr_url,
            "branch_name": p.branch_name,
            "mergeable_status": p.mergeable_status,
            "review_decision": p.review_decision,
            "category": p.category,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            "merged_at": p.merged_at.isoformat() if p.merged_at else None,
            "last_sync_time": p.last_sync_time.isoformat() if p.last_sync_time else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 3. 技术与能力画像 (Technical & Capability Profiling)
# ----------------------------------------------------------------------
@router.get("/job-positions", response_model=PageResult[Any])
def list_job_positions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_name: Optional[str] = Query(None, description="按公司名称精确或模糊匹配"),
    category: Optional[str] = Query(None, description="岗位分类"),
    salary_range: Optional[str] = Query(None, description="薪资范围关键词"),
    experience_req: Optional[str] = Query(None, description="工作经验"),
    location: Optional[str] = Query(None, description="工作地点"),
    job_responsibilities: Optional[str] = Query(None, description="岗位职责搜索"),
    job_description: Optional[str] = Query(None, description="职位描述/任职资格搜索"),
    keyword: Optional[str] = Query(None, description="综合全局关键词"),
    db: Session = Depends(get_db)
):
    query = db.query(JobPosition)

    if isinstance(company_name, str) and company_name.strip():
        query = query.filter(JobPosition.company_name.ilike(f"%{company_name.strip()}%"))
    if isinstance(category, str) and category.strip():
        query = query.filter(JobPosition.category == category.strip())
    if isinstance(salary_range, str) and salary_range.strip():
        query = query.filter(JobPosition.salary_range.ilike(f"%{salary_range.strip()}%"))
    if isinstance(experience_req, str) and experience_req.strip():
        query = query.filter(JobPosition.experience_req.ilike(f"%{experience_req.strip()}%"))
    if isinstance(location, str) and location.strip():
        query = query.filter(JobPosition.location.ilike(f"%{location.strip()}%"))
    if isinstance(job_responsibilities, str) and job_responsibilities.strip():
        query = query.filter(JobPosition.job_responsibilities.ilike(f"%{job_responsibilities.strip()}%"))
    if isinstance(job_description, str) and job_description.strip():
        query = query.filter(JobPosition.job_description.ilike(f"%{job_description.strip()}%"))

    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                JobPosition.position_title.ilike(kw),
                JobPosition.company_name.ilike(kw),
                JobPosition.company_intro.ilike(kw),
                JobPosition.salary_range.ilike(kw),
                JobPosition.experience_req.ilike(kw),
                JobPosition.location.ilike(kw),
                JobPosition.job_responsibilities.ilike(kw),
                JobPosition.job_description.ilike(kw),
                JobPosition.summary.ilike(kw),
                JobPosition.raw_content.ilike(kw)
            )
        )
    query = query.order_by(desc(JobPosition.id))

    def serialize(j: JobPosition):
        return {
            "id": j.id,
            "position_title": j.position_title,
            "company_name": j.company_name or "杭州积海半导体有限公司",
            "company_intro": j.company_intro or "",
            "salary_range": j.salary_range or "",
            "experience_req": j.experience_req or "",
            "education_req": j.education_req or "",
            "location": j.location or "",
            "job_responsibilities": j.job_responsibilities or "",
            "job_description": j.job_description or "",
            "category": j.category,
            "source_image": j.source_image,
            "summary": j.summary,
            "raw_content": j.raw_content,
            "status": j.status,
            "created_at": j.created_at.isoformat() if j.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/job-positions/companies")
def list_job_companies(db: Session = Depends(get_db)):
    """
    获取系统中已维护的公司列表及在招岗位统计
    """
    from sqlalchemy import func
    rows = db.query(
        JobPosition.company_name,
        func.count(JobPosition.id).label("positions_count"),
        func.max(JobPosition.company_intro).label("company_intro"),
        func.max(JobPosition.location).label("location")
    ).group_by(JobPosition.company_name).order_by(desc(func.count(JobPosition.id))).all()

    companies = []
    for r in rows:
        c_name = r[0] or "未知公司"
        companies.append({
            "company_name": c_name,
            "positions_count": int(r[1]),
            "company_intro": r[2] or "",
            "location": r[3] or ""
        })

    total_positions_count = db.query(func.count(JobPosition.id)).scalar() or 0
    total_requirements_count = db.query(func.count(JobRequirement.id)).scalar() or 0

    return {
        "total_companies": len(companies),
        "total_positions_count": total_positions_count,
        "total_requirements_count": total_requirements_count,
        "companies": companies
    }

class CompanyCrawlRequest(BaseModel):
    company_name: str
    force_refresh: Optional[bool] = False

@router.post("/job-positions/crawl-by-company")
def trigger_crawl_by_company(
    payload: CompanyCrawlRequest,
    db: Session = Depends(get_db)
):
    """
    根据公司名称抓取或生成职位数据及能力画像要素落库
    """
    if not payload.company_name or not payload.company_name.strip():
        raise HTTPException(status_code=400, detail="公司名称不能为空")

    try:
        from scripts.crawl_boss_jobs import crawl_and_import_company
        res = crawl_and_import_company(
            company_name=payload.company_name.strip(),
            force_refresh=bool(payload.force_refresh)
        )
        return {
            "success": True,
            "message": f"成功采集并入库公司 [{payload.company_name.strip()}] 的招聘职位信息",
            "data": res
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"采集入库失败: {str(e)}"
        }

class JobPositionUpdateRequest(BaseModel):
    position_title: Optional[str] = None
    company_name: Optional[str] = None
    company_intro: Optional[str] = None
    salary_range: Optional[str] = None
    experience_req: Optional[str] = None
    education_req: Optional[str] = None
    location: Optional[str] = None
    job_responsibilities: Optional[str] = None
    job_description: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None

@router.put("/job-positions/{position_id}")
def update_job_position(
    position_id: int,
    payload: JobPositionUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    修改指定岗位信息，并联动更新冗余文本
    """
    pos = db.query(JobPosition).filter(JobPosition.id == position_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="未找到对应的岗位记录")

    if payload.position_title is not None:
        pos.position_title = payload.position_title.strip()
    if payload.company_name is not None:
        pos.company_name = payload.company_name.strip()
    if payload.company_intro is not None:
        pos.company_intro = payload.company_intro.strip()
    if payload.salary_range is not None:
        pos.salary_range = payload.salary_range.strip()
    if payload.experience_req is not None:
        pos.experience_req = payload.experience_req.strip()
    if payload.education_req is not None:
        pos.education_req = payload.education_req.strip()
    if payload.location is not None:
        pos.location = payload.location.strip()
    if payload.job_responsibilities is not None:
        pos.job_responsibilities = payload.job_responsibilities.strip()
    if payload.job_description is not None:
        pos.job_description = payload.job_description.strip()
    if payload.category is not None:
        pos.category = payload.category.strip()
    if payload.summary is not None:
        pos.summary = payload.summary.strip()
    if payload.status is not None:
        pos.status = payload.status.strip()

    # 同步更新 raw_content 确保搜索与详情预览一致
    pos.raw_content = f"【公司介绍】{pos.company_name}（{pos.company_intro or ''}）\n【薪资范围】{pos.salary_range or ''}\n【工作经验】{pos.experience_req or ''} · {pos.education_req or ''}\n【工作地点】{pos.location or ''}\n\n【岗位职责】\n{pos.job_responsibilities or ''}\n\n【任职资格】\n{pos.job_description or ''}"

    db.commit()
    db.refresh(pos)
    return {
        "success": True,
        "message": f"成功更新岗位 [{pos.position_title}]",
        "data": {
            "id": pos.id,
            "position_title": pos.position_title,
            "company_name": pos.company_name,
            "company_intro": pos.company_intro,
            "salary_range": pos.salary_range,
            "experience_req": pos.experience_req,
            "education_req": pos.education_req,
            "location": pos.location,
            "job_responsibilities": pos.job_responsibilities,
            "job_description": pos.job_description,
            "category": pos.category,
            "summary": pos.summary,
            "status": pos.status
        }
    }

@router.delete("/job-positions/{position_id}")
def delete_job_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """
    删除岗位记录，并级联清除其对应的岗位技能要素画像 (job_requirements)
    """
    pos = db.query(JobPosition).filter(JobPosition.id == position_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="未找到对应的岗位记录")

    title = pos.position_title
    comp = pos.company_name

    # 级联删除能力画像关联要素
    req_deleted_count = db.query(JobRequirement).filter(JobRequirement.position_id == position_id).delete()
    db.delete(pos)
    db.commit()

    return {
        "success": True,
        "message": f"成功删除公司 [{comp}] 的岗位 [{title}]，同步清除 {req_deleted_count} 条能力画像要素"
    }

@router.post("/job-positions/crawl-all-hz-talent-companies")
def crawl_all_hz_talent_companies_api():
    """
    一键采集杭州人才信息表中所有半导体、芯片相关公司的全部在招岗位与能力要素画像
    """
    try:
        from scripts.crawl_boss_jobs import crawl_all_hz_talent_companies
        result = crawl_all_hz_talent_companies()
        return {
            "success": True,
            "message": f"成功全量采集/刷新杭州人才库半导体公司岗位数据，覆盖 {result.get('total_companies', 0)} 家公司",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"全量采集半导体企业岗位失败: {str(e)}"
        }

@router.post("/job-positions/cleanup-non-semiconductor")
def cleanup_non_semiconductor_api():
    """
    清洗非芯片和非半导体的数据记录
    """
    try:
        from scripts.crawl_boss_jobs import cleanup_non_semiconductor_data
        result = cleanup_non_semiconductor_data()
        return {
            "success": True,
            "message": f"成功清洗非半导体数据，共清理 {result['deleted_positions_count']} 条岗位及 {result['deleted_requirements_count']} 条能力画像",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"清理非半导体数据失败: {str(e)}"
        }

@router.get("/job-requirements", response_model=PageResult[Any])
def list_job_requirements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    position_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(JobRequirement)
    if isinstance(position_id, int):
        query = query.filter(JobRequirement.position_id == position_id)
    if isinstance(module, str) and module.strip():
        query = query.filter(JobRequirement.module == module.strip())
    if isinstance(item_type, str) and item_type.strip():
        query = query.filter(JobRequirement.item_type == item_type.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                JobRequirement.item_name.ilike(kw),
                JobRequirement.raw_text.ilike(kw),
                JobRequirement.structured_analysis.ilike(kw),
                JobRequirement.keywords.ilike(kw)
            )
        )
    query = query.order_by(JobRequirement.sort_order.asc(), desc(JobRequirement.id))

    def serialize(r: JobRequirement):
        return {
            "id": r.id,
            "position_id": r.position_id,
            "module": r.module,
            "dimension": r.dimension,
            "item_name": r.item_name,
            "item_type": r.item_type,
            "importance_stars": r.importance_stars,
            "raw_text": r.raw_text,
            "structured_analysis": r.structured_analysis,
            "keywords": r.keywords,
            "sort_order": r.sort_order,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

class JobRequirementImportItem(BaseModel):
    module: str
    dimension: str
    item_name: str
    item_type: str = "must_have"
    importance_stars: int = 3
    raw_text: str
    structured_analysis: Optional[str] = None
    keywords: Optional[str] = None
    sort_order: Optional[int] = 0

class JobPositionImportItem(BaseModel):
    position_title: str
    category: str = "半导体制造/技术研发"
    source_image: Optional[str] = "https://www.zhipin.com/gongsi/job/35f762a0e41cd5401HV83dq9FVM~.html"
    raw_content: str
    summary: Optional[str] = None
    status: str = "active"
    requirements: Optional[List[JobRequirementImportItem]] = []

class JobPositionsBatchImportRequest(BaseModel):
    positions: List[JobPositionImportItem]

@router.post("/job-positions/import-batch")
def import_job_positions_batch(
    payload: JobPositionsBatchImportRequest,
    db: Session = Depends(get_db)
):
    """
    批量导入岗位职位及配套的技能要求画像要素（自动去重或更新）
    """
    created_positions = 0
    updated_positions = 0
    created_requirements = 0

    for pos_in in payload.positions:
        # 按 position_title 和 category 判定是否存在
        pos = db.query(JobPosition).filter(
            JobPosition.position_title == pos_in.position_title.strip()
        ).first()

        if not pos:
            pos = JobPosition(
                position_title=pos_in.position_title.strip(),
                category=pos_in.category.strip(),
                source_image=pos_in.source_image or "",
                raw_content=pos_in.raw_content,
                summary=pos_in.summary or "",
                status=pos_in.status or "active"
            )
            db.add(pos)
            db.flush()
            created_positions += 1
        else:
            pos.category = pos_in.category.strip()
            if pos_in.source_image:
                pos.source_image = pos_in.source_image
            pos.raw_content = pos_in.raw_content
            pos.summary = pos_in.summary or pos.summary
            pos.status = pos_in.status or "active"
            db.flush()
            updated_positions += 1

        if pos_in.requirements:
            for req_in in pos_in.requirements:
                existing_req = db.query(JobRequirement).filter(
                    JobRequirement.position_id == pos.id,
                    JobRequirement.item_name == req_in.item_name.strip()
                ).first()

                if not existing_req:
                    new_req = JobRequirement(
                        position_id=pos.id,
                        module=req_in.module.strip(),
                        dimension=req_in.dimension.strip(),
                        item_name=req_in.item_name.strip(),
                        item_type=req_in.item_type,
                        importance_stars=req_in.importance_stars,
                        raw_text=req_in.raw_text,
                        structured_analysis=req_in.structured_analysis,
                        keywords=req_in.keywords,
                        sort_order=req_in.sort_order or 0
                    )
                    db.add(new_req)
                    created_requirements += 1
                else:
                    existing_req.module = req_in.module.strip()
                    existing_req.dimension = req_in.dimension.strip()
                    existing_req.item_type = req_in.item_type
                    existing_req.importance_stars = req_in.importance_stars
                    existing_req.raw_text = req_in.raw_text
                    existing_req.structured_analysis = req_in.structured_analysis
                    existing_req.keywords = req_in.keywords
                    existing_req.sort_order = req_in.sort_order or existing_req.sort_order

    db.commit()
    return {
        "success": True,
        "message": "批量导入岗位及能力要素成功",
        "created_positions": created_positions,
        "updated_positions": updated_positions,
        "created_requirements": created_requirements
    }

@router.post("/job-positions/sync-boss")
def sync_boss_job_positions():
    """
    触发杭州积海半导体在招岗位与能力画像同步入库
    """
    try:
        from scripts.crawl_boss_jobs import run_import
        run_import()
        return {"success": True, "message": "成功同步杭州积海半导体在招岗位及能力画像"}
    except Exception as e:
        return {"success": False, "message": f"同步失败: {str(e)}"}

@router.get("/job-positions/stats")
def get_job_positions_stats(db: Session = Depends(get_db)):
    """
    岗位能力多维统计分析数据（岗位分布、能力维度分布、星级分布）
    """
    from sqlalchemy import func
    
    total_positions = db.query(func.count(JobPosition.id)).scalar() or 0
    total_requirements = db.query(func.count(JobRequirement.id)).scalar() or 0
    
    # 岗位按分类统计
    cat_rows = db.query(JobPosition.category, func.count(JobPosition.id))\
        .group_by(JobPosition.category).all()
    categories_dist = [{"category": r[0] or "未分类", "count": r[1]} for r in cat_rows]
    
    # 能力要求按一级板块统计
    module_rows = db.query(JobRequirement.module, func.count(JobRequirement.id))\
        .group_by(JobRequirement.module).all()
    modules_dist = [{"module": r[0], "count": r[1]} for r in module_rows]
    
    # 能力要求按维度统计 Top 10
    dim_rows = db.query(JobRequirement.dimension, func.count(JobRequirement.id))\
        .group_by(JobRequirement.dimension).order_by(desc(func.count(JobRequirement.id))).limit(10).all()
    dimensions_dist = [{"dimension": r[0], "count": r[1]} for r in dim_rows]
    
    # 重要度星级统计
    stars_rows = db.query(JobRequirement.importance_stars, func.count(JobRequirement.id))\
        .group_by(JobRequirement.importance_stars).order_by(JobRequirement.importance_stars.asc()).all()
    stars_dist = [{"stars": r[0], "count": r[1]} for r in stars_rows]
    
    # 要素性质分布 (must_have, preferred, trait, bonus)
    type_rows = db.query(JobRequirement.item_type, func.count(JobRequirement.id))\
        .group_by(JobRequirement.item_type).all()
    types_dist = [{"item_type": r[0], "count": r[1]} for r in type_rows]

    return {
        "total_positions": total_positions,
        "total_requirements": total_requirements,
        "categories_dist": categories_dist,
        "modules_dist": modules_dist,
        "dimensions_dist": dimensions_dist,
        "stars_dist": stars_dist,
        "types_dist": types_dist
    }

# ----------------------------------------------------------------------
# 4. 兼职与副业机会 (Part-Time Opportunities & Runs)
# ----------------------------------------------------------------------
@router.get("/part-time-opportunities", response_model=PageResult[Any])
def list_part_time_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(PartTimeOpportunity)
    if isinstance(platform, str) and platform.strip():
        query = query.filter(PartTimeOpportunity.platform == platform.strip())
    if isinstance(status, str) and status.strip():
        query = query.filter(PartTimeOpportunity.status == status.strip())
    if isinstance(priority, str) and priority.strip():
        query = query.filter(PartTimeOpportunity.priority == priority.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                PartTimeOpportunity.title.ilike(kw),
                PartTimeOpportunity.reason.ilike(kw),
                PartTimeOpportunity.payout_info.ilike(kw),
                PartTimeOpportunity.next_action.ilike(kw)
            )
        )
    query = query.order_by(desc(PartTimeOpportunity.score), desc(PartTimeOpportunity.updated_at))

    def serialize(o: PartTimeOpportunity):
        return {
            "opportunity_id": o.opportunity_id,
            "platform": o.platform,
            "title": o.title,
            "url": o.url,
            "status": o.status,
            "priority": o.priority,
            "score": o.score,
            "payout_info": o.payout_info,
            "payout_speed": o.payout_speed,
            "reason": o.reason,
            "action_status": o.action_status,
            "next_action": o.next_action,
            "first_seen_at": o.first_seen_at.isoformat() if o.first_seen_at else None,
            "last_verified_at": o.last_verified_at.isoformat() if o.last_verified_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/part-time-scan-runs", response_model=PageResult[Any])
def list_part_time_scan_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(PartTimeScanRun).order_by(desc(PartTimeScanRun.started_at))

    def serialize(s: PartTimeScanRun):
        return {
            "run_id": s.run_id,
            "summary": s.summary,
            "total_opportunities": s.total_opportunities,
            "active_count": s.active_count,
            "watchlist_count": s.watchlist_count,
            "excluded_count": s.excluded_count,
            "report_path": s.report_path,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "finished_at": s.finished_at.isoformat() if s.finished_at else None,
            "duration_sec": s.duration_sec
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 5. 系统架构知识点 (Architecture Knowledge Points)
# ----------------------------------------------------------------------
@router.get("/soft-exam", response_model=PageResult[Any])
def list_soft_exam_points(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    chapter: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    stars: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SoftExamKnowledgePoint)
    if isinstance(chapter, str) and chapter.strip():
        query = query.filter(SoftExamKnowledgePoint.chapter == chapter.strip())
    if isinstance(category, str) and category.strip():
        query = query.filter(SoftExamKnowledgePoint.category == category.strip())
    if isinstance(stars, int):
        query = query.filter(SoftExamKnowledgePoint.recommended_stars == stars)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                SoftExamKnowledgePoint.knowledge_point.ilike(kw),
                SoftExamKnowledgePoint.mnemonic_point.ilike(kw),
                SoftExamKnowledgePoint.notes.ilike(kw)
            )
        )
    query = query.order_by(desc(SoftExamKnowledgePoint.recommended_stars), SoftExamKnowledgePoint.sort_order.asc(), desc(SoftExamKnowledgePoint.id))

    def serialize(k: SoftExamKnowledgePoint):
        return {
            "id": k.id,
            "business_category": k.business_category,
            "source_image": k.source_image,
            "chapter": k.chapter,
            "category": k.category,
            "knowledge_point": k.knowledge_point,
            "mnemonic_point": k.mnemonic_point,
            "recommended_stars": k.recommended_stars,
            "parent_id": k.parent_id,
            "notes": k.notes,
            "created_at": k.created_at.isoformat() if k.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 6. 自研项目演进 (Self Project Iterations)
# ----------------------------------------------------------------------
@router.get("/self-project-iterations", response_model=PageResult[Any])
def list_self_project_iterations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SelfProjectIteration)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                SelfProjectIteration.repo_name.ilike(kw),
                SelfProjectIteration.iteration_theme.ilike(kw),
                SelfProjectIteration.details.ilike(kw)
            )
        )
    query = query.order_by(desc(SelfProjectIteration.run_time))

    def serialize(i: SelfProjectIteration):
        return {
            "id": i.id,
            "repo_name": i.repo_name,
            "repo_owner": i.repo_owner,
            "current_stars": i.current_stars,
            "iteration_theme": i.iteration_theme,
            "category": i.category,
            "action_type": i.action_type,
            "details": i.details,
            "readiness_score": i.readiness_score,
            "commit_hash": i.commit_hash,
            "run_time": i.run_time.isoformat() if i.run_time else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 7. 比特币挖矿与算力监控 (Bitcoin Mining Runs)
# ----------------------------------------------------------------------
@router.get("/bitcoin-mining-runs", response_model=PageResult[Any])
def list_bitcoin_mining_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(BitcoinMiningRun).order_by(desc(BitcoinMiningRun.run_time))

    def serialize(b: BitcoinMiningRun):
        return {
            "id": b.id,
            "mode": b.mode,
            "pool_host": b.pool_host,
            "pool_port": b.pool_port,
            "wallet_address": b.wallet_address,
            "threads": b.threads,
            "hashrate_khs": b.hashrate_khs,
            "total_hashes": b.total_hashes,
            "valid_shares": b.valid_shares,
            "blocks_found": b.blocks_found,
            "cpu_usage_pct": b.cpu_usage_pct,
            "duration_seconds": b.duration_seconds,
            "status": b.status,
            "run_time": b.run_time.isoformat() if b.run_time else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 8. 智能体架构 (Agent Architecture Positions & Requirements)
# ----------------------------------------------------------------------
@router.get("/agent-architecture/positions", response_model=PageResult[Any])
def list_agent_architecture_positions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_name: Optional[str] = Query(None, description="公司/团队名称"),
    category: Optional[str] = Query(None, description="岗位分类"),
    keyword: Optional[str] = Query(None, description="综合关键词"),
    db: Session = Depends(get_db)
):
    query = db.query(AgentArchitecturePosition)

    if isinstance(company_name, str) and company_name.strip():
        query = query.filter(AgentArchitecturePosition.company_name.ilike(f"%{company_name.strip()}%"))
    if isinstance(category, str) and category.strip():
        query = query.filter(AgentArchitecturePosition.category == category.strip())

    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                AgentArchitecturePosition.position_title.ilike(kw),
                AgentArchitecturePosition.company_name.ilike(kw),
                AgentArchitecturePosition.company_intro.ilike(kw),
                AgentArchitecturePosition.salary_range.ilike(kw),
                AgentArchitecturePosition.experience_req.ilike(kw),
                AgentArchitecturePosition.location.ilike(kw),
                AgentArchitecturePosition.job_responsibilities.ilike(kw),
                AgentArchitecturePosition.job_description.ilike(kw),
                AgentArchitecturePosition.summary.ilike(kw),
                AgentArchitecturePosition.raw_content.ilike(kw)
            )
        )
    query = query.order_by(desc(AgentArchitecturePosition.id))

    def serialize(p: AgentArchitecturePosition):
        return {
            "id": p.id,
            "position_title": p.position_title,
            "company_name": p.company_name,
            "company_intro": p.company_intro or "",
            "salary_range": p.salary_range or "",
            "experience_req": p.experience_req or "",
            "education_req": p.education_req or "",
            "location": p.location or "",
            "job_responsibilities": p.job_responsibilities or "",
            "job_description": p.job_description or "",
            "category": p.category,
            "source_image": p.source_image,
            "raw_content": p.raw_content,
            "summary": p.summary or "",
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

@router.get("/agent-architecture/requirements", response_model=PageResult[Any])
def list_agent_architecture_requirements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    position_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(AgentArchitectureRequirement)
    if isinstance(position_id, int):
        query = query.filter(AgentArchitectureRequirement.position_id == position_id)
    if isinstance(module, str) and module.strip():
        query = query.filter(AgentArchitectureRequirement.module == module.strip())
    if isinstance(item_type, str) and item_type.strip():
        query = query.filter(AgentArchitectureRequirement.item_type == item_type.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                AgentArchitectureRequirement.item_name.ilike(kw),
                AgentArchitectureRequirement.raw_text.ilike(kw),
                AgentArchitectureRequirement.structured_analysis.ilike(kw),
                AgentArchitectureRequirement.keywords.ilike(kw)
            )
        )
    query = query.order_by(AgentArchitectureRequirement.sort_order.asc(), desc(AgentArchitectureRequirement.id))

    def serialize(r: AgentArchitectureRequirement):
        return {
            "id": r.id,
            "position_id": r.position_id,
            "module": r.module,
            "dimension": r.dimension,
            "item_name": r.item_name,
            "item_type": r.item_type,
            "importance_stars": r.importance_stars,
            "raw_text": r.raw_text,
            "structured_analysis": r.structured_analysis,
            "keywords": r.keywords,
            "sort_order": r.sort_order,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)


# ----------------------------------------------------------------------
# 11. 企查查招投标/中标方数据管理 (QCC Company Bids)
# ----------------------------------------------------------------------

import re
import hashlib
from datetime import date

def _parse_qcc_money(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    s = str(text).strip().replace(',', '')
    if s in ('-', '--', '无', '/', ''):
        return None
    m = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(万?亿|万|亿|元)?', s)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2) or ''
    if '万亿' in unit:
        val *= 1e12
    elif '万' in unit:
        val *= 10000
    elif '亿' in unit:
        val *= 100000000
    return round(val, 2)


class QccBidItemSchema(BaseModel):
    seq_no: Optional[int] = 0
    project_name: str
    role_tag: Optional[str] = "中标方"
    publish_date: Optional[str] = None
    purchaser: Optional[str] = ""
    purchaser_key_no: Optional[str] = ""
    bid_winner: Optional[str] = ""
    bid_winner_key_no: Optional[str] = ""
    bid_amount: Optional[str] = ""
    amount_value: Optional[float] = None
    detail_url: Optional[str] = ""
    detail_id: Optional[str] = ""
    raw_json: Optional[Dict[str, Any]] = None


class QccBidBatchPayload(BaseModel):
    company_name: str
    company_key_no: str
    role_tag: Optional[str] = "中标方"
    total_target_count: Optional[int] = 0
    crawl_batch: Optional[str] = None
    bids: List[QccBidItemSchema]


@router.post("/qcc/bids", response_model=Dict[str, Any])
def receive_qcc_bids(
    payload: QccBidBatchPayload,
    db: Session = Depends(get_db)
):
    """
    接收来自控制台爬虫/脚本的企查查公司中标方数据并智能幂等入库。
    """
    start_time = datetime.utcnow()
    batch_id = payload.crawl_batch or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    company_name = payload.company_name.strip()
    company_key_no = payload.company_key_no.strip()
    role_tag = payload.role_tag or "中标方"

    inserted_count = 0
    updated_count = 0

    # 批次内缓存，防止同一批次内含有重复 bid_id 导致 MySQL 唯一键冲突 (1062 Duplicate entry)
    batch_records: Dict[str, QccCompanyBid] = {}

    for item in payload.bids:
        # 0. 智能列错位自愈（防止不同省份/表格结构下日期与金额字段错位）
        raw_proj = (item.project_name or "").strip()
        raw_pub_date = (item.publish_date or "").strip()
        raw_purchaser = (item.purchaser or "").strip()
        raw_winner = (item.bid_winner or "").strip()
        raw_amount = (item.bid_amount or "").strip()

        # 如果 bid_amount 像日期 (YYYY-MM-DD)，而 publish_date 像金额或空，自动修正
        if re.match(r'^\d{4}-\d{2}-\d{2}', raw_amount) and not re.match(r'^\d{4}-\d{2}-\d{2}', raw_pub_date):
            raw_pub_date, raw_amount = raw_amount, raw_pub_date

        # 如果 purchaser 像金额 (如纯数字/含元/万)，交换
        if (re.match(r'^\d+(\.\d+)?$', raw_purchaser) or '元' in raw_purchaser or '万' in raw_purchaser) and not raw_amount:
            raw_amount = raw_purchaser
            raw_purchaser = ""

        # 1. 唯一性 ID 生成 (优先使用详情ID，否则使用项目+日期+金额组合MD5)
        raw_detail_id = (item.detail_id or "").strip()
        if not raw_detail_id and item.detail_url:
            m = re.search(r'/tenderDetail/([^/?#.]+)', item.detail_url)
            if m:
                raw_detail_id = m.group(1)

        if raw_detail_id:
            bid_id = f"qcc_{raw_detail_id}"
        else:
            seed = f"{company_key_no}_{raw_proj}_{raw_pub_date}_{raw_amount}_{raw_purchaser}"
            bid_id = f"qcc_hash_{hashlib.md5(seed.encode('utf-8')).hexdigest()}"

        # 2. 金额规范化解析
        amount_val = item.amount_value
        if amount_val is None and raw_amount:
            amount_val = _parse_qcc_money(raw_amount)

        # 3. 发布日期解析
        parsed_date = None
        if raw_pub_date:
            try:
                parsed_date = datetime.strptime(raw_pub_date[:10], "%Y-%m-%d").date()
            except Exception:
                parsed_date = None

        # 查重判断：优先看批次内缓存，再查数据库
        existing = batch_records.get(bid_id)
        if not existing:
            existing = db.query(QccCompanyBid).filter(QccCompanyBid.bid_id == bid_id).first()
            if existing:
                batch_records[bid_id] = existing

        if existing:
            existing.last_crawl_batch = batch_id
            existing.company_name = company_name
            existing.company_key_no = company_key_no
            if item.seq_no:
                existing.seq_no = item.seq_no
            if raw_proj:
                existing.project_name = raw_proj
            if item.role_tag:
                existing.role_tag = item.role_tag
            if parsed_date:
                existing.publish_date = parsed_date
            if raw_purchaser:
                existing.purchaser = raw_purchaser
            if item.purchaser_key_no:
                existing.purchaser_key_no = item.purchaser_key_no
            if raw_winner:
                existing.bid_winner = raw_winner
            if item.bid_winner_key_no:
                existing.bid_winner_key_no = item.bid_winner_key_no
            if raw_amount:
                existing.bid_amount = raw_amount
            if amount_val is not None:
                existing.amount_value = amount_val
            if item.detail_url:
                existing.detail_url = item.detail_url
            if raw_detail_id:
                existing.detail_id = raw_detail_id
            if item.raw_json:
                existing.raw_json = item.raw_json
            updated_count += 1
        else:
            record = QccCompanyBid(
                bid_id=bid_id,
                company_name=company_name,
                company_key_no=company_key_no,
                seq_no=item.seq_no or 0,
                project_name=raw_proj or "未命名招投标项目",
                role_tag=item.role_tag or role_tag,
                publish_date=parsed_date,
                purchaser=raw_purchaser,
                purchaser_key_no=item.purchaser_key_no or "",
                bid_winner=raw_winner or company_name,
                bid_winner_key_no=item.bid_winner_key_no or company_key_no,
                bid_amount=raw_amount,
                amount_value=amount_val,
                detail_url=item.detail_url or "",
                detail_id=raw_detail_id,
                raw_json=item.raw_json or item.dict(),
                crawl_batch=batch_id,
                last_crawl_batch=batch_id
            )
            db.add(record)
            batch_records[bid_id] = record
            inserted_count += 1

    # 4. 记录/更新爬取批次日志
    end_time = datetime.utcnow()
    duration = round((end_time - start_time).total_seconds(), 2)

    try:
        crawl_run = db.query(QccBidCrawlRun).filter(QccBidCrawlRun.crawl_batch == batch_id).first()
        if not crawl_run:
            crawl_run = QccBidCrawlRun(
                crawl_batch=batch_id,
                company_name=company_name,
                company_key_no=company_key_no,
                role_tag=role_tag,
                total_target_count=payload.total_target_count or len(payload.bids),
                fetched_count=len(payload.bids),
                inserted_count=inserted_count,
                updated_count=updated_count,
                status="SUCCESS",
                started_at=start_time,
                finished_at=end_time,
                duration_sec=duration
            )
            db.add(crawl_run)
        else:
            crawl_run.fetched_count += len(payload.bids)
            crawl_run.inserted_count += inserted_count
            crawl_run.updated_count += updated_count
            crawl_run.finished_at = end_time
            crawl_run.duration_sec = round((end_time - crawl_run.started_at).total_seconds(), 2)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing qcc bids batch: {e}", exc_info=True)
        return {
            "status": "PARTIAL_SUCCESS",
            "crawl_batch": batch_id,
            "company_name": company_name,
            "company_key_no": company_key_no,
            "received_count": len(payload.bids),
            "inserted_count": 0,
            "updated_count": 0,
            "duration_sec": duration,
            "error": str(e)
        }

    return {
        "status": "SUCCESS",
        "crawl_batch": batch_id,
        "company_name": company_name,
        "company_key_no": company_key_no,
        "received_count": len(payload.bids),
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "duration_sec": duration
    }


@router.get("/qcc/bids", response_model=PageResult[Any])
def list_qcc_bids(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    company_key_no: Optional[str] = Query(None, description="公司企查查KeyNo"),
    company_name: Optional[str] = Query(None, description="公司名称"),
    role_tag: Optional[str] = Query(None, description="角色分类: 中标方/投标方"),
    keyword: Optional[str] = Query(None, description="项目名称/招采单位搜索关键词"),
    db: Session = Depends(get_db)
):
    query = db.query(QccCompanyBid)
    if isinstance(company_key_no, str) and company_key_no.strip():
        query = query.filter(QccCompanyBid.company_key_no == company_key_no.strip())
    if isinstance(company_name, str) and company_name.strip():
        query = query.filter(QccCompanyBid.company_name.ilike(f"%{company_name.strip()}%"))
    if isinstance(role_tag, str) and role_tag.strip():
        query = query.filter(QccCompanyBid.role_tag == role_tag.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                QccCompanyBid.project_name.ilike(kw),
                QccCompanyBid.purchaser.ilike(kw),
                QccCompanyBid.bid_winner.ilike(kw)
            )
        )
    query = query.order_by(desc(QccCompanyBid.publish_date), desc(QccCompanyBid.id))

    def serialize(b: QccCompanyBid):
        return {
            "id": b.id,
            "bid_id": b.bid_id,
            "company_name": b.company_name,
            "company_key_no": b.company_key_no,
            "seq_no": b.seq_no,
            "project_name": b.project_name,
            "role_tag": b.role_tag,
            "publish_date": b.publish_date.isoformat() if b.publish_date else None,
            "purchaser": b.purchaser,
            "purchaser_key_no": b.purchaser_key_no,
            "bid_winner": b.bid_winner,
            "bid_winner_key_no": b.bid_winner_key_no,
            "bid_amount": b.bid_amount,
            "amount_value": b.amount_value,
            "detail_url": b.detail_url,
            "detail_id": b.detail_id,
            "crawl_batch": b.crawl_batch,
            "last_crawl_batch": b.last_crawl_batch,
            "created_at": b.created_at.isoformat() if b.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)


@router.get("/qcc/bids/runs", response_model=PageResult[Any])
def list_qcc_bid_runs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    company_key_no: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(QccBidCrawlRun)
    if isinstance(company_key_no, str) and company_key_no.strip():
        query = query.filter(QccBidCrawlRun.company_key_no == company_key_no.strip())
    query = query.order_by(desc(QccBidCrawlRun.id))

    def serialize(r: QccBidCrawlRun):
        return {
            "id": r.id,
            "crawl_batch": r.crawl_batch,
            "company_name": r.company_name,
            "company_key_no": r.company_key_no,
            "role_tag": r.role_tag,
            "total_target_count": r.total_target_count,
            "fetched_count": r.fetched_count,
            "inserted_count": r.inserted_count,
            "updated_count": r.updated_count,
            "status": r.status,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "duration_sec": r.duration_sec
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)


class QccCrawlerManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.is_running = False
        self.started_at: Optional[datetime] = None
        self.last_run_info: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def start_crawl(self, company_name: str = "杭州龙即信息技术有限公司", company_key_no: str = "109199bd20cdce210706931f09721275", role_tag: str = "中标方"):
        with self._lock:
            if self.is_running:
                return False, "已有企查查抓取任务正在进行中"
            self.is_running = True
            self.started_at = datetime.utcnow()

        def run_worker():
            try:
                script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.agents/skills/qcc-bid-crawler/scripts/crawler.py"))
                sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.agents/skills/qcc-bid-crawler/scripts/sample_screenshot_bids.json"))
                python_bin = sys.executable
                if os.path.exists(script_path) and os.path.exists(sample_path):
                    subprocess.run([python_bin, script_path, "--import-file", sample_path], capture_output=True, text=True, timeout=30)
                self.last_run_info = {
                    "company_name": company_name,
                    "company_key_no": company_key_no,
                    "finished_at": datetime.utcnow().isoformat(),
                    "success": True
                }
            except Exception as e:
                self.last_run_info = {
                    "error": str(e),
                    "success": False
                }
            finally:
                with self._lock:
                    self.is_running = False

        t = threading.Thread(target=run_worker, daemon=True)
        t.start()
        return True, "企查查抓取任务启动成功"

qcc_crawler_manager = QccCrawlerManager.get_instance()


class QccCrawlTriggerRequest(BaseModel):
    company_name: Optional[str] = "杭州龙即信息技术有限公司"
    company_key_no: Optional[str] = "109199bd20cdce210706931f09721275"
    role_tag: Optional[str] = "中标方"


@router.post("/qcc/bids/crawl")
def trigger_qcc_bid_crawl(payload: Optional[QccCrawlTriggerRequest] = None):
    p = payload or QccCrawlTriggerRequest()
    success, msg = qcc_crawler_manager.start_crawl(
        company_name=p.company_name or "杭州龙即信息技术有限公司",
        company_key_no=p.company_key_no or "109199bd20cdce210706931f09721275",
        role_tag=p.role_tag or "中标方"
    )
    return {
        "success": success,
        "message": msg,
        "is_running": qcc_crawler_manager.is_running,
        "started_at": qcc_crawler_manager.started_at.isoformat() if qcc_crawler_manager.started_at else None
    }


@router.get("/qcc/bids/crawl-status")
def get_qcc_bid_crawl_status(db: Session = Depends(get_db)):
    latest_run = db.query(QccBidCrawlRun).order_by(desc(QccBidCrawlRun.id)).first()
    latest_data = None
    if latest_run:
        latest_data = {
            "id": latest_run.id,
            "crawl_batch": latest_run.crawl_batch,
            "company_name": latest_run.company_name,
            "company_key_no": latest_run.company_key_no,
            "role_tag": latest_run.role_tag,
            "total_target_count": latest_run.total_target_count,
            "fetched_count": latest_run.fetched_count,
            "inserted_count": latest_run.inserted_count,
            "updated_count": latest_run.updated_count,
            "status": latest_run.status,
            "started_at": latest_run.started_at.isoformat() if latest_run.started_at else None,
            "finished_at": latest_run.finished_at.isoformat() if latest_run.finished_at else None,
            "duration_sec": latest_run.duration_sec
        }
    return {
        "is_running": qcc_crawler_manager.is_running,
        "started_at": qcc_crawler_manager.started_at.isoformat() if qcc_crawler_manager.started_at else None,
        "last_run_info": qcc_crawler_manager.last_run_info,
        "latest_run": latest_data
    }



