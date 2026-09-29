from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Text, JSON, DateTime, Date,
    Enum, Integer, Float, SmallInteger
)
from db.session import Base

class HzTalentNotice(Base):
    __tablename__ = "hz_talent_notices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    notice_id = Column(String(64), unique=True, nullable=False, index=True)
    notice_type = Column(Enum("personal", "list"), nullable=False, default="personal")
    title = Column(String(512), nullable=False)
    publish_date = Column(Date, nullable=True)
    detail_url = Column(String(512), nullable=False)
    author = Column(String(128), default="")
    wenhao = Column(String(128), default="")
    person_name = Column(String(128), default="")
    gender = Column(String(16), default="")
    birth_date = Column(String(32), default="")
    work_unit = Column(String(256), default="")
    accept_dept = Column(String(256), default="")
    apply_type = Column(String(512), default="")
    publicity_period = Column(String(128), default="")
    content_text = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    crawl_batch = Column(String(32), nullable=False)
    last_crawl_batch = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HzNoticeCrawlRun(Base):
    __tablename__ = "hz_notice_crawl_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    crawl_batch = Column(String(32), unique=True, nullable=False)
    total_fetched = Column(Integer, nullable=False, default=0)
    personal_count = Column(Integer, nullable=False, default=0)
    list_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="SUCCESS")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    duration_sec = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HfTalentRecord(Base):
    __tablename__ = "hf_talent_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id = Column(String(64), unique=True, nullable=False, index=True)
    record_type = Column(Enum("publicity", "result"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    publish_date = Column(Date, nullable=True, index=True)
    detail_url = Column(String(512), nullable=False)
    author = Column(String(128), default="合肥市人力资源和社会保障局 合肥市人才办")
    
    person_name = Column(String(128), nullable=False, index=True)
    person_name_masked = Column(String(128), default="")
    gender = Column(String(16), default="")
    work_unit = Column(String(256), default="", index=True)
    accept_dept = Column(String(256), default="")
    
    level_code = Column(String(32), default="")
    level_code_name = Column(String(64), default="", index=True)
    clause = Column(String(512), default="")
    talent_type = Column(String(32), default="")
    talent_type_name = Column(String(128), default="")
    
    publicity_start_time = Column(DateTime, nullable=True)
    publicity_end_time = Column(DateTime, nullable=True)
    publicity_period = Column(String(128), default="")
    confirm_time = Column(DateTime, nullable=True)
    
    approval_name = Column(String(128), default="")
    approval_tel = Column(String(64), default="")
    approval_review_name = Column(String(128), default="")
    approval_review_tel = Column(String(64), default="")
    
    content_text = Column(Text, nullable=True)
    raw_json = Column(JSON, nullable=True)
    
    crawl_batch = Column(String(32), nullable=False, index=True)
    last_crawl_batch = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HfTalentCrawlRun(Base):
    __tablename__ = "hf_talent_crawl_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    crawl_batch = Column(String(32), unique=True, nullable=False)
    total_fetched = Column(Integer, nullable=False, default=0)
    publicity_count = Column(Integer, nullable=False, default=0)
    result_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="SUCCESS")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    duration_sec = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class GithubPrLifecycle(Base):
    __tablename__ = "github_prs_lifecycle"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    repo_name = Column(String(128), nullable=False)
    repo_owner = Column(String(64), nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String(512), nullable=False)
    state = Column(String(32), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    pr_url = Column(String(512), unique=True, nullable=False)
    branch_name = Column(String(128), nullable=True)
    mergeable_status = Column(String(32), default="UNKNOWN")
    review_decision = Column(String(32), default="NONE")
    category = Column(String(64), default="upstream")
    last_sync_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GithubContribution(Base):
    __tablename__ = "github_contributions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pr_url = Column(String(512), unique=True, nullable=False)
    repo_name = Column(String(128), nullable=False)
    repo_owner = Column(String(64), nullable=False)
    repo_stars = Column(String(32), default="")
    pr_number = Column(Integer, nullable=True)
    pr_title = Column(String(512), default="")
    branch_name = Column(String(128), default="")
    category = Column(String(64), default="")
    conclusion = Column(Text, nullable=False)
    is_security = Column(SmallInteger, nullable=False, default=0)
    ghsa_id = Column(String(64), default="")
    status = Column(String(32), nullable=False, default="OPEN")
    merged_at = Column(DateTime, nullable=True)
    log_file = Column(String(256), nullable=False)
    run_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PartTimeOpportunity(Base):
    __tablename__ = "part_time_opportunities"

    opportunity_id = Column(String(128), primary_key=True)
    platform = Column(String(64), nullable=False)
    title = Column(String(512), nullable=False)
    url = Column(String(512), nullable=False)
    status = Column(
        Enum("active", "watchlist", "excluded", "applied"),
        nullable=False,
        default="active"
    )
    priority = Column(String(16), default="P3")
    score = Column(Integer, nullable=False, default=0)
    payout_info = Column(Text, nullable=True)
    payout_speed = Column(String(128), default="")
    fingerprint = Column(String(128), default="")
    reason = Column(Text, nullable=True)
    action_status = Column(String(128), default="")
    next_action = Column(Text, nullable=True)
    artifacts = Column(JSON, nullable=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    last_run_id = Column(String(64), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PartTimeScanRun(Base):
    __tablename__ = "part_time_scan_runs"

    run_id = Column(String(64), primary_key=True)
    summary = Column(Text, nullable=True)
    total_opportunities = Column(Integer, nullable=False, default=0)
    active_count = Column(Integer, nullable=False, default=0)
    watchlist_count = Column(Integer, nullable=False, default=0)
    excluded_count = Column(Integer, nullable=False, default=0)
    report_path = Column(String(256), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    duration_sec = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class JobPosition(Base):
    __tablename__ = "job_positions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_title = Column(String(150), nullable=False)
    company_name = Column(String(150), nullable=False, default="杭州积海半导体有限公司")
    company_intro = Column(String(500), nullable=True)
    salary_range = Column(String(64), nullable=True)
    experience_req = Column(String(64), nullable=True)
    education_req = Column(String(64), nullable=True)
    location = Column(String(128), nullable=True)
    job_responsibilities = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="AI Agent")
    source_image = Column(String(255), default="media_1788048860408.png")
    raw_content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_id = Column(BigInteger, nullable=False)
    module = Column(String(64), nullable=False)
    dimension = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_type = Column(
        Enum("must_have", "preferred", "trait", "bonus"),
        nullable=False,
        default="must_have"
    )
    importance_stars = Column(SmallInteger, nullable=False, default=3)
    raw_text = Column(Text, nullable=False)
    structured_analysis = Column(Text, nullable=True)
    keywords = Column(String(255), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SoftExamKnowledgePoint(Base):
    __tablename__ = "soft_exam_knowledge_points"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_category = Column(String(150), nullable=False)
    source_image = Column(String(255), nullable=False)
    chapter = Column(String(100), nullable=False)
    category = Column(String(150), nullable=False)
    knowledge_point = Column(String(255), nullable=False)
    mnemonic_point = Column(Text, nullable=True)
    recommended_stars = Column(SmallInteger, nullable=False, default=1)
    parent_id = Column(BigInteger, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SelfProjectIteration(Base):
    __tablename__ = "self_project_iterations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    repo_name = Column(String(128), nullable=False)
    repo_owner = Column(String(64), nullable=False, default="loulanyue")
    current_stars = Column(Integer, default=0)
    iteration_theme = Column(String(256), nullable=False)
    category = Column(String(64), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)
    readiness_score = Column(Integer, default=0)
    log_file = Column(String(256), nullable=True)
    commit_hash = Column(String(64), nullable=True)
    run_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BitcoinMiningRun(Base):
    __tablename__ = "bitcoin_mining_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mode = Column(String(32), nullable=False, default="simulation")
    pool_host = Column(String(128), nullable=True)
    pool_port = Column(Integer, nullable=True)
    wallet_address = Column(String(128), nullable=True)
    threads = Column(Integer, default=1)
    hashrate_khs = Column(Float, default=0)
    total_hashes = Column(BigInteger, default=0)
    valid_shares = Column(Integer, default=0)
    blocks_found = Column(Integer, default=0)
    cpu_usage_pct = Column(Float, default=0)
    duration_seconds = Column(Integer, default=0)
    status = Column(String(32), nullable=False, default="COMPLETED")
    log_file = Column(String(256), nullable=True)
    run_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentArchitecturePosition(Base):
    __tablename__ = "agent_architecture_positions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_title = Column(String(150), nullable=False)
    company_name = Column(String(150), nullable=False)
    company_intro = Column(String(500), nullable=True)
    salary_range = Column(String(64), nullable=True)
    experience_req = Column(String(64), nullable=True)
    education_req = Column(String(64), nullable=True)
    location = Column(String(128), nullable=True)
    job_responsibilities = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="智能体架构")
    source_image = Column(String(255), nullable=True)
    raw_content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentArchitectureRequirement(Base):
    __tablename__ = "agent_architecture_requirements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_id = Column(BigInteger, nullable=False)
    module = Column(String(64), nullable=False)
    dimension = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_type = Column(
        Enum("must_have", "preferred", "trait", "bonus"),
        nullable=False,
        default="must_have"
    )
    importance_stars = Column(SmallInteger, nullable=False, default=3)
    raw_text = Column(Text, nullable=False)
    structured_analysis = Column(Text, nullable=True)
    keywords = Column(String(255), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QccCompanyBid(Base):
    __tablename__ = "qcc_company_bids"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    bid_id = Column(String(128), unique=True, nullable=False, index=True)
    company_name = Column(String(256), nullable=False, index=True)
    company_key_no = Column(String(64), nullable=False, index=True)
    seq_no = Column(Integer, default=0)
    project_name = Column(String(512), nullable=False)
    role_tag = Column(String(32), default="中标方")
    publish_date = Column(Date, nullable=True, index=True)
    purchaser = Column(String(256), default="")
    purchaser_key_no = Column(String(64), default="")
    bid_winner = Column(String(256), default="")
    bid_winner_key_no = Column(String(64), default="")
    bid_amount = Column(String(64), default="")
    amount_value = Column(Float, nullable=True)
    detail_url = Column(String(512), default="")
    detail_id = Column(String(128), default="")
    raw_json = Column(JSON, nullable=True)
    crawl_batch = Column(String(32), nullable=False, index=True)
    last_crawl_batch = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QccBidCrawlRun(Base):
    __tablename__ = "qcc_bid_crawl_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    crawl_batch = Column(String(32), unique=True, nullable=False)
    company_name = Column(String(256), nullable=False)
    company_key_no = Column(String(64), nullable=False)
    role_tag = Column(String(32), default="中标方")
    total_target_count = Column(Integer, default=0)
    fetched_count = Column(Integer, default=0)
    inserted_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    status = Column(String(32), default="SUCCESS")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    duration_sec = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)



