from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Integer, Boolean
from db.session import Base

class CodeContract(Base):
    __tablename__ = "code_contracts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contract_id = Column(String(64), unique=True, nullable=False, index=True) # 如 CTR-TPM-PKG-001
    title = Column(String(256), nullable=False) # 契约标题
    category = Column(String(64), nullable=False, default="api") # api, dto, database_schema, event, rpc
    contract_type = Column(String(32), nullable=False, default="OpenAPI") # OpenAPI, JSONSchema, TypeScriptType, JavaDTO, Protobuf
    version = Column(String(32), nullable=False, default="1.0.0") # SemVer
    status = Column(String(32), nullable=False, default="active") # active, draft, deprecated, superseded
    owner = Column(String(128), nullable=False, default="ArchitectureTeam")
    service_name = Column(String(128), nullable=False, default="tpm-backend-app") # tpm-backend-app, tpm-frontend-web, agent-control, tpm-backend-file
    endpoint_or_path = Column(String(512), nullable=True) # 接口路径或包路径
    schema_content = Column(Text, nullable=False) # 契约规范完整文本 (OpenAPI YAML/JSON / Schema / DTO)
    description = Column(Text, nullable=True) # 业务语义与约定说明
    change_policy = Column(String(64), nullable=False, default="independent_pr_required") # independent_pr_required, breaking_freeze, standard
    consumers_count = Column(Integer, nullable=False, default=0)
    is_breaking_frozen = Column(Boolean, nullable=False, default=False) # 锁定禁止破坏性变更
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContractRevision(Base):
    __tablename__ = "contract_revisions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contract_id = Column(String(64), nullable=False, index=True)
    version = Column(String(32), nullable=False)
    revision_no = Column(Integer, nullable=False, default=1)
    change_type = Column(String(32), nullable=False, default="patch") # initial, patch, minor, major_breaking
    change_summary = Column(Text, nullable=False) # 变更摘要说明
    diff_content = Column(Text, nullable=True) # 变更对比内容
    schema_snapshot = Column(Text, nullable=False) # 历史快照
    git_commit = Column(String(64), nullable=True)
    pr_reference = Column(String(128), nullable=True)
    approved_by = Column(String(128), nullable=False, default="System")
    created_at = Column(DateTime, default=datetime.utcnow)

class ContractConsumer(Base):
    __tablename__ = "contract_consumers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contract_id = Column(String(64), nullable=False, index=True)
    consumer_type = Column(String(64), nullable=False, default="frontend_page") # frontend_page, backend_service, subagent, cron_job
    consumer_name = Column(String(256), nullable=False) # 如 CentralizedPackageView.vue / PurchasePlanAppService.java
    consumer_repo = Column(String(128), nullable=False, default="tpm-frontend-web") # tpm-frontend-web, tpm-backend-app, agent-control
    consumer_path = Column(String(512), nullable=True) # 文件相对路径
    binding_status = Column(String(32), nullable=False, default="verified") # verified, outdated, unverified
    test_suite_ref = Column(String(256), nullable=True) # 对应的契约测试用例路径
    last_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ArbitrationGuardLog(Base):
    __tablename__ = "arbitration_guard_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True) # 如 ARB-EVT-20261014-001
    contract_id = Column(String(64), nullable=True, index=True) # 关联契约编号，如 CTR-TPM-PKG-001
    event_type = Column(String(64), nullable=False, index=True) # test_assertion_weakened, test_deleted, lint_rule_ignored, threshold_lowered, contract_bypassed, layer_violation, protected_file_modified
    source_repo = Column(String(128), nullable=False, default="tpm-backend-app") # tpm-backend-app, tpm-frontend-web, agent-control
    target_file = Column(String(512), nullable=False) # 违规文件相对路径
    operator_or_agent = Column(String(128), nullable=False, default="AI-Assistant") # 涉事Agent或开发者
    rule_name = Column(String(256), nullable=False) # 命中的守卫规则名称
    diff_snippet = Column(Text, nullable=True) # 违规 diff 或关键片段
    interception_action = Column(String(64), nullable=False, default="blocked") # blocked, manual_confirmation_required, adr_exception_granted
    severity = Column(String(32), nullable=False, default="CRITICAL") # CRITICAL, HIGH, MEDIUM
    arbitration_decision = Column(Text, nullable=False) # 仲裁裁决与阻断原因
    adr_reference = Column(String(128), nullable=True) # 破例ADR编号（如 ADR-2026-TPM-012）
    adr_expires_at = Column(DateTime, nullable=True) # ADR例外过期时间
    status = Column(String(32), nullable=False, default="blocked") # blocked, confirmed_violation, waived_by_adr, pending_review
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
