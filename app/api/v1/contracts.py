import json
import yaml
from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func

from db.session import get_db
from app.models.contract import CodeContract, ContractRevision, ContractConsumer
from app.schemas.pagination import PageResult, paginate_query

router = APIRouter(prefix="/contracts", tags=["Code Contracts"])

# ----------------------------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------------------------
class ContractCreateRequest(BaseModel):
    contract_id: str = Field(..., description="唯一契约编号，如 CTR-TPM-PKG-001")
    title: str = Field(..., description="契约名称/接口定义说明")
    category: str = Field("api", description="契约大类: api / dto / database_schema / event / rpc")
    contract_type: str = Field("OpenAPI", description="格式类型: OpenAPI / JSONSchema / TypeScriptType / JavaDTO / Protobuf")
    version: str = Field("1.0.0", description="SemVer版本号，如 1.0.0")
    service_name: str = Field("tpm-backend-app", description="所属服务模块")
    endpoint_or_path: Optional[str] = Field(None, description="接口URL或包路径")
    schema_content: str = Field(..., description="机器可读的Schema定义规范文本")
    description: Optional[str] = Field(None, description="业务规则与语义契约")
    owner: str = Field("ArchitectureTeam", description="负责人/责任方")
    change_policy: str = Field("independent_pr_required", description="变更规约策略: independent_pr_required / breaking_freeze / standard")
    is_breaking_frozen: bool = Field(False, description="是否锁定禁止破坏性变更")

class ContractUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    contract_type: Optional[str] = None
    version: str = Field(..., description="新版本号 (遵循 SemVer 升级，如 1.1.0)")
    status: Optional[str] = None
    endpoint_or_path: Optional[str] = None
    schema_content: str = Field(..., description="变更后的新Schema规范文本")
    description: Optional[str] = None
    change_type: str = Field("minor", description="变更类型: minor / patch / major_breaking")
    change_summary: str = Field(..., description="变更原因与影响说明 (契约变更走独立审计流程)")
    git_commit: Optional[str] = Field(None, description="关联Git提交哈希")
    pr_reference: Optional[str] = Field(None, description="关联独立契约变更PR编号")
    approved_by: str = Field("SystemAdmin", description="审批人签名")
    change_policy: Optional[str] = None
    is_breaking_frozen: Optional[bool] = None

class ConsumerBindRequest(BaseModel):
    consumer_type: str = Field("frontend_page", description="消费方类型: frontend_page / backend_service / subagent / cron_job")
    consumer_name: str = Field(..., description="消费端名称，如 CentralizedPackageView.vue")
    consumer_repo: str = Field("tpm-frontend-web", description="消费端所属仓库")
    consumer_path: Optional[str] = Field(None, description="文件或组件绝对/相对路径")
    test_suite_ref: Optional[str] = Field(None, description="对应的契约自动化测试文件路径")
    binding_status: str = Field("verified", description="契约对齐校验状态: verified / outdated / unverified")

class SchemaVerifyRequest(BaseModel):
    contract_type: str = Field("OpenAPI", description="OpenAPI / JSONSchema / TypeScriptType / JavaDTO / Protobuf")
    content: str = Field(..., description="待校验的文本内容")

# ----------------------------------------------------------------------
# 1. 契约全局多维统计指标 (Stats) - 必须在动态路由前声明
# ----------------------------------------------------------------------
@router.get("/stats")
def get_contracts_stats(db: Session = Depends(get_db)):
    """
    获取契约中心全景统计指标：覆盖数量、服务分布、规范格式、消费者绑定、高危冻结等
    """
    total_contracts = db.query(func.count(CodeContract.id)).scalar() or 0
    active_contracts = db.query(func.count(CodeContract.id)).filter(CodeContract.status == "active").scalar() or 0
    draft_contracts = db.query(func.count(CodeContract.id)).filter(CodeContract.status == "draft").scalar() or 0
    frozen_contracts = db.query(func.count(CodeContract.id)).filter(CodeContract.is_breaking_frozen == True).scalar() or 0
    
    total_revisions = db.query(func.count(ContractRevision.id)).scalar() or 0
    total_consumers = db.query(func.count(ContractConsumer.id)).scalar() or 0

    # 按服务模块分布统计
    services_rows = db.query(CodeContract.service_name, func.count(CodeContract.id)).group_by(CodeContract.service_name).all()
    services_dist = [{"service": r[0], "count": r[1]} for r in services_rows]

    # 按格式规范类型分布
    types_rows = db.query(CodeContract.contract_type, func.count(CodeContract.id)).group_by(CodeContract.contract_type).all()
    types_dist = [{"type": r[0], "count": r[1]} for r in types_rows]

    # 按业务大类分布
    categories_rows = db.query(CodeContract.category, func.count(CodeContract.id)).group_by(CodeContract.category).all()
    categories_dist = [{"category": r[0], "count": r[1]} for r in categories_rows]

    return {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "draft_contracts": draft_contracts,
        "frozen_contracts": frozen_contracts,
        "total_revisions": total_revisions,
        "total_consumers": total_consumers,
        "summary": {
            "total_contracts": total_contracts,
            "active_contracts": active_contracts,
            "draft_contracts": draft_contracts,
            "frozen_contracts": frozen_contracts,
            "total_revisions": total_revisions,
            "total_consumers": total_consumers
        },
        "services_distribution": services_dist,
        "types_distribution": types_dist,
        "categories_distribution": categories_dist
    }

# ----------------------------------------------------------------------
# 2. 契约修订演进流水线列表 (Revisions Audit) - 声明在动态路由前
# ----------------------------------------------------------------------
@router.get("/revisions", response_model=PageResult[Any])
def list_all_contract_revisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    contract_id: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ContractRevision)
    if isinstance(contract_id, str) and contract_id.strip():
        query = query.filter(ContractRevision.contract_id == contract_id.strip())
    if isinstance(change_type, str) and change_type.strip():
        query = query.filter(ContractRevision.change_type == change_type.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                ContractRevision.contract_id.ilike(kw),
                ContractRevision.change_summary.ilike(kw),
                ContractRevision.pr_reference.ilike(kw),
                ContractRevision.git_commit.ilike(kw),
                ContractRevision.approved_by.ilike(kw)
            )
        )
    query = query.order_by(desc(ContractRevision.id))

    def serialize(r: ContractRevision):
        return {
            "id": r.id,
            "contract_id": r.contract_id,
            "version": r.version,
            "revision_no": r.revision_no,
            "change_type": r.change_type,
            "change_summary": r.change_summary,
            "diff_content": r.diff_content,
            "schema_snapshot": r.schema_snapshot,
            "git_commit": r.git_commit,
            "pr_reference": r.pr_reference,
            "approved_by": r.approved_by,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 3. 消费端绑定拓扑列表 (Consumers Topology) - 声明在动态路由前
# ----------------------------------------------------------------------
@router.get("/consumers", response_model=PageResult[Any])
def list_all_contract_consumers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    contract_id: Optional[str] = Query(None),
    consumer_repo: Optional[str] = Query(None),
    binding_status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ContractConsumer)
    if isinstance(contract_id, str) and contract_id.strip():
        query = query.filter(ContractConsumer.contract_id == contract_id.strip())
    if isinstance(consumer_repo, str) and consumer_repo.strip():
        query = query.filter(ContractConsumer.consumer_repo == consumer_repo.strip())
    if isinstance(binding_status, str) and binding_status.strip():
        query = query.filter(ContractConsumer.binding_status == binding_status.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                ContractConsumer.contract_id.ilike(kw),
                ContractConsumer.consumer_name.ilike(kw),
                ContractConsumer.consumer_path.ilike(kw),
                ContractConsumer.test_suite_ref.ilike(kw)
            )
        )
    query = query.order_by(desc(ContractConsumer.id))

    def serialize(c: ContractConsumer):
        return {
            "id": c.id,
            "contract_id": c.contract_id,
            "consumer_type": c.consumer_type,
            "consumer_name": c.consumer_name,
            "consumer_repo": c.consumer_repo,
            "consumer_path": c.consumer_path,
            "binding_status": c.binding_status,
            "test_suite_ref": c.test_suite_ref,
            "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 4. 实时 Schema 语法校验工具接口
# ----------------------------------------------------------------------
@router.post("/verify-schema")
def verify_contract_schema(payload: SchemaVerifyRequest):
    """在线语法解析校验：JSON / YAML / OpenAPI"""
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="契约规范文本内容不能为空")

    c_type = payload.contract_type.lower()
    try:
        if "json" in c_type:
            parsed = json.loads(content)
            return {"valid": True, "format": "JSON", "keys_count": len(parsed) if isinstance(parsed, dict) else len(parsed)}
        elif "openapi" in c_type or "yaml" in c_type:
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                return {"valid": False, "error": "YAML 内容必须解析为字典根对象"}
            has_openapi = "openapi" in parsed or "swagger" in parsed or "paths" in parsed or "components" in parsed
            return {"valid": True, "format": "YAML / OpenAPI", "is_openapi_spec": bool(has_openapi)}
        else:
            # DTO / TypeScript / Protobuf 基础非空与行数检查
            lines = [l for l in content.splitlines() if l.strip()]
            return {"valid": True, "format": payload.contract_type, "lines_count": len(lines)}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# ----------------------------------------------------------------------
# 5. 契约列表与基础分页 (Contracts List)
# ----------------------------------------------------------------------
@router.get("", response_model=PageResult[Any])
def list_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="契约大类"),
    service_name: Optional[str] = Query(None, description="服务模块"),
    contract_type: Optional[str] = Query(None, description="格式类型"),
    status: Optional[str] = Query(None, description="状态: active / draft / deprecated"),
    is_breaking_frozen: Optional[bool] = Query(None, description="是否锁定"),
    keyword: Optional[str] = Query(None, description="关键词匹配: 编号/标题/端点/负责人"),
    db: Session = Depends(get_db)
):
    query = db.query(CodeContract)
    if isinstance(status, str) and status.strip():
        query = query.filter(CodeContract.status == status.strip())
    if isinstance(category, str) and category.strip():
        query = query.filter(CodeContract.category == category.strip())
    if isinstance(service_name, str) and service_name.strip():
        query = query.filter(CodeContract.service_name == service_name.strip())
    if isinstance(contract_type, str) and contract_type.strip():
        query = query.filter(CodeContract.contract_type == contract_type.strip())
    if isinstance(is_breaking_frozen, bool):
        query = query.filter(CodeContract.is_breaking_frozen == is_breaking_frozen)
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                CodeContract.contract_id.ilike(kw),
                CodeContract.title.ilike(kw),
                CodeContract.endpoint_or_path.ilike(kw),
                CodeContract.owner.ilike(kw),
                CodeContract.description.ilike(kw)
            )
        )
    query = query.order_by(desc(CodeContract.id))

    def serialize(c: CodeContract):
        return {
            "id": c.id,
            "contract_id": c.contract_id,
            "title": c.title,
            "category": c.category,
            "contract_type": c.contract_type,
            "version": c.version,
            "status": c.status,
            "owner": c.owner,
            "service_name": c.service_name,
            "endpoint_or_path": c.endpoint_or_path,
            "schema_content": c.schema_content,
            "description": c.description,
            "change_policy": c.change_policy,
            "consumers_count": c.consumers_count,
            "is_breaking_frozen": c.is_breaking_frozen,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        }

    return paginate_query(query, page if isinstance(page, int) else 1, page_size if isinstance(page_size, int) else 20, serialize)

# ----------------------------------------------------------------------
# 6. 新增契约 (Code Contract Creation)
# ----------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreateRequest, db: Session = Depends(get_db)):
    cid = payload.contract_id.strip()
    existing = db.query(CodeContract).filter(CodeContract.contract_id == cid).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"契约编号 '{cid}' 已存在，不能重复创建")

    contract = CodeContract(
        contract_id=cid,
        title=payload.title.strip(),
        category=payload.category,
        contract_type=payload.contract_type,
        version=payload.version.strip(),
        status="active",
        owner=payload.owner.strip(),
        service_name=payload.service_name.strip(),
        endpoint_or_path=payload.endpoint_or_path.strip() if payload.endpoint_or_path else None,
        schema_content=payload.schema_content.strip(),
        description=payload.description.strip() if payload.description else None,
        change_policy=payload.change_policy,
        is_breaking_frozen=payload.is_breaking_frozen,
        consumers_count=0
    )
    db.add(contract)
    db.flush()

    # 自动创建 Initial 第 1 个版本修订历史
    revision = ContractRevision(
        contract_id=cid,
        version=payload.version.strip(),
        revision_no=1,
        change_type="initial",
        change_summary="契约初始建立并注册至架构仲裁库",
        diff_content="+ 契约初始规范基准建立",
        schema_snapshot=payload.schema_content.strip(),
        approved_by=payload.owner.strip(),
        created_at=datetime.utcnow()
    )
    db.add(revision)
    db.commit()
    db.refresh(contract)

    return {
        "success": True,
        "message": f"契约 {cid} 创建成功，并已确立初始规范基准 (v{contract.version})",
        "contract_id": contract.contract_id
    }

# ----------------------------------------------------------------------
# 7. 获取单个契约详情 (含Revisions与Consumers)
# ----------------------------------------------------------------------
@router.get("/{contract_id}")
def get_contract_detail(contract_id: str, db: Session = Depends(get_db)):
    cid = contract_id.strip()
    contract = db.query(CodeContract).filter(CodeContract.contract_id == cid).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"未找到契约编号为 '{cid}' 的契约记录")

    revisions = db.query(ContractRevision).filter(ContractRevision.contract_id == cid).order_by(desc(ContractRevision.revision_no)).all()
    consumers = db.query(ContractConsumer).filter(ContractConsumer.contract_id == cid).order_by(desc(ContractConsumer.id)).all()

    return {
        "id": contract.id,
        "contract_id": contract.contract_id,
        "title": contract.title,
        "category": contract.category,
        "contract_type": contract.contract_type,
        "version": contract.version,
        "status": contract.status,
        "owner": contract.owner,
        "service_name": contract.service_name,
        "endpoint_or_path": contract.endpoint_or_path,
        "schema_content": contract.schema_content,
        "description": contract.description,
        "change_policy": contract.change_policy,
        "consumers_count": len(consumers),
        "revisions_count": len(revisions),
        "is_breaking_frozen": contract.is_breaking_frozen,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
        "updated_at": contract.updated_at.isoformat() if contract.updated_at else None,
        "revisions": [
            {
                "id": r.id,
                "version": r.version,
                "revision_no": r.revision_no,
                "change_type": r.change_type,
                "change_summary": r.change_summary,
                "diff_content": r.diff_content,
                "git_commit": r.git_commit,
                "pr_reference": r.pr_reference,
                "approved_by": r.approved_by,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in revisions
        ],
        "consumers": [
            {
                "id": c.id,
                "consumer_type": c.consumer_type,
                "consumer_name": c.consumer_name,
                "consumer_repo": c.consumer_repo,
                "consumer_path": c.consumer_path,
                "binding_status": c.binding_status,
                "test_suite_ref": c.test_suite_ref,
                "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None
            }
            for c in consumers
        ]
    }

# ----------------------------------------------------------------------
# 8. 独立契约变更审批流程 (Contract Update & Revisions Locking)
# ----------------------------------------------------------------------
@router.put("/{contract_id}")
def update_contract(contract_id: str, payload: ContractUpdateRequest, db: Session = Depends(get_db)):
    cid = contract_id.strip()
    contract = db.query(CodeContract).filter(CodeContract.contract_id == cid).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"未找到契约编号为 '{cid}' 的记录")

    # 破坏性冻结检查
    if contract.is_breaking_frozen and payload.change_type == "major_breaking":
        raise HTTPException(
            status_code=403,
            detail=f"契约 '{cid}' 处于破坏性冻结状态 (Breaking Change Frozen)，禁止提交重大破坏性变更！"
        )

    # 必须提供变更说明
    if not payload.change_summary.strip():
        raise HTTPException(status_code=400, detail="契约变更必须填写独立审查与仲裁摘要 (change_summary)")

    old_version = contract.version
    old_schema = contract.schema_content

    # 更新契约实体
    if payload.title: contract.title = payload.title.strip()
    if payload.category: contract.category = payload.category
    if payload.contract_type: contract.contract_type = payload.contract_type
    if payload.status: contract.status = payload.status
    if payload.endpoint_or_path is not None: contract.endpoint_or_path = payload.endpoint_or_path.strip()
    if payload.description is not None: contract.description = payload.description.strip()
    if payload.change_policy: contract.change_policy = payload.change_policy
    if payload.is_breaking_frozen is not None: contract.is_breaking_frozen = payload.is_breaking_frozen
    
    contract.version = payload.version.strip()
    contract.schema_content = payload.schema_content.strip()
    contract.updated_at = datetime.utcnow()

    # 查寻最新修订号
    latest_rev = db.query(func.max(ContractRevision.revision_no)).filter(ContractRevision.contract_id == cid).scalar() or 1
    new_rev_no = latest_rev + 1

    # 生成简易变更对比摘要
    diff_text = f"--- v{old_version}\n+++ v{contract.version}\n变更类型: {payload.change_type}\n审批人: {payload.approved_by}"

    revision = ContractRevision(
        contract_id=cid,
        version=contract.version,
        revision_no=new_rev_no,
        change_type=payload.change_type,
        change_summary=payload.change_summary.strip(),
        diff_content=diff_text,
        schema_snapshot=contract.schema_content,
        git_commit=payload.git_commit.strip() if payload.git_commit else None,
        pr_reference=payload.pr_reference.strip() if payload.pr_reference else None,
        approved_by=payload.approved_by.strip(),
        created_at=datetime.utcnow()
    )
    db.add(revision)
    db.commit()
    db.refresh(contract)

    return {
        "success": True,
        "message": f"契约 {cid} 已通过独立变更流程升级至 v{contract.version} (Revision #{new_rev_no})",
        "contract_id": contract.contract_id,
        "new_version": contract.version,
        "revision_no": new_rev_no
    }

# ----------------------------------------------------------------------
# 9. 消费端绑定 (Consumer Binding)
# ----------------------------------------------------------------------
@router.post("/{contract_id}/consumers", status_code=status.HTTP_201_CREATED)
def bind_contract_consumer(contract_id: str, payload: ConsumerBindRequest, db: Session = Depends(get_db)):
    cid = contract_id.strip()
    contract = db.query(CodeContract).filter(CodeContract.contract_id == cid).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"未找到契约 '{cid}'")

    consumer = ContractConsumer(
        contract_id=cid,
        consumer_type=payload.consumer_type,
        consumer_name=payload.consumer_name.strip(),
        consumer_repo=payload.consumer_repo.strip(),
        consumer_path=payload.consumer_path.strip() if payload.consumer_path else None,
        test_suite_ref=payload.test_suite_ref.strip() if payload.test_suite_ref else None,
        binding_status=payload.binding_status,
        last_verified_at=datetime.utcnow()
    )
    db.add(consumer)
    contract.consumers_count = (contract.consumers_count or 0) + 1
    db.commit()
    db.refresh(consumer)

    return {
        "success": True,
        "message": f"消费端 '{consumer.consumer_name}' 已成功与契约 {cid} 建立绑定拓扑",
        "consumer_id": consumer.id,
        "consumer_name": consumer.consumer_name
    }

# ----------------------------------------------------------------------
# 10. 解绑消费端
# ----------------------------------------------------------------------
@router.delete("/{contract_id}/consumers/{consumer_id}")
def unbind_contract_consumer(contract_id: str, consumer_id: int, db: Session = Depends(get_db)):
    cid = contract_id.strip()
    consumer = db.query(ContractConsumer).filter(
        ContractConsumer.id == consumer_id,
        ContractConsumer.contract_id == cid
    ).first()
    if not consumer:
        raise HTTPException(status_code=404, detail="未找到对应的契约消费端绑定记录")

    db.delete(consumer)
    contract = db.query(CodeContract).filter(CodeContract.contract_id == cid).first()
    if contract and contract.consumers_count > 0:
        contract.consumers_count -= 1
    db.commit()

    return {
        "success": True,
        "message": f"消费端绑定已成功解除"
    }

# ----------------------------------------------------------------------
# 11. 删除契约 (含级联清理修订历史与消费端)
# ----------------------------------------------------------------------
@router.delete("/{contract_id}")
def delete_contract(contract_id: str, db: Session = Depends(get_db)):
    cid = contract_id.strip()
    contract = db.query(CodeContract).filter(CodeContract.contract_id == cid).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"未找到契约编号为 '{cid}' 的契约")

    # 级联删除消费者与修订历史
    db.query(ContractConsumer).filter(ContractConsumer.contract_id == cid).delete()
    db.query(ContractRevision).filter(ContractRevision.contract_id == cid).delete()
    db.delete(contract)
    db.commit()

    return {
        "success": True,
        "message": f"契约 {cid} 及其关联的所有修订快照和消费端拓扑已成功删除"
    }
