import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.session import SessionLocal
from app.models.contract import CodeContract, ContractRevision, ContractConsumer

def seed_code_contracts():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(CodeContract).count()
        if existing > 0:
            print(f"Contracts table already contains {existing} records. Clearing for fresh seed...")
            db.query(ContractConsumer).delete()
            db.query(ContractRevision).delete()
            db.query(CodeContract).delete()
            db.commit()

        print("Seeding core TPM and Agent Control code contracts...")

        contracts_data = [
            {
                "contract": CodeContract(
                    contract_id="CTR-TPM-PKG-001",
                    title="采购需求集中打包与归口审核契约",
                    category="api",
                    contract_type="OpenAPI",
                    version="1.1.0",
                    status="active",
                    service_name="tpm-backend-app",
                    endpoint_or_path="/api/purchase/requirement/package",
                    schema_content="""openapi: 3.0.3
info:
  title: 采购需求集中打包与归口审核契约
  version: 1.1.0
  description: 规范集中打包时的归口部门接收、互斥校验与打包逻辑。操作后数据在其他归口部门消失。
paths:
  /api/purchase/requirement/package:
    post:
      summary: 创建或执行集中打包
      parameters:
        - in: header
          name: X-Department-Code
          required: true
          schema:
            type: string
          description: 操作省属/市级归口部门编码
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - package_name
                - requirement_ids
              properties:
                package_name:
                  type: string
                  minLength: 2
                  maxLength: 100
                requirement_ids:
                  type: array
                  items:
                    type: integer
                  minItems: 1
      responses:
        '200':
          description: 打包成功响应
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    example: 200
                  data:
                    type: object
                    properties:
                      package_id:
                        type: integer
                      status:
                        type: string
                        example: "PACKAGED"
                  message:
                    type: string
""",
                    description="严格约定集中打包原子互斥锁及归口部门数据可见性隔离契约。防并发重复打包。",
                    owner="集中采购组",
                    change_policy="independent_pr_required",
                    is_breaking_frozen=True
                ),
                "revisions": [
                    ContractRevision(
                        contract_id="CTR-TPM-PKG-001",
                        revision_no=1,
                        version="1.0.0",
                        change_type="minor",
                        change_summary="初始化采购需求集中打包接口契约草案",
                        schema_snapshot="openapi: 3.0.3\ninfo:\n  title: 采购需求集中打包与归口审核契约\n  version: 1.0.0",
                        git_commit="a1b2c3d4",
                        pr_reference="PR-CONTRACT-101",
                        approved_by="Architect-Leader"
                    ),
                    ContractRevision(
                        contract_id="CTR-TPM-PKG-001",
                        revision_no=2,
                        version="1.1.0",
                        change_type="minor",
                        change_summary="增加 X-Department-Code 归口部门请求头以及互斥排他校验声明，避免重复打包",
                        schema_snapshot="openapi: 3.0.3\ninfo:\n  title: 采购需求集中打包与归口审核契约\n  version: 1.1.0\n# 增加 X-Department-Code 约束",
                        git_commit="e5f6g7h8",
                        pr_reference="PR-CONTRACT-104",
                        approved_by="ChiefArchitect"
                    )
                ],
                "consumers": [
                    ContractConsumer(
                        contract_id="CTR-TPM-PKG-001",
                        consumer_type="frontend_page",
                        consumer_name="CentralizedPackageView.vue",
                        consumer_repo="tpm-frontend-web",
                        consumer_path="src/views/purchase/CentralizedPackageView.vue",
                        test_suite_ref="tests/unit/CentralizedPackage.spec.ts",
                        binding_status="verified"
                    ),
                    ContractConsumer(
                        contract_id="CTR-TPM-PKG-001",
                        consumer_type="backend_service",
                        consumer_name="RequirementPackageServiceImpl.java",
                        consumer_repo="tpm-backend-app",
                        consumer_path="src/main/java/com/tpm/service/impl/RequirementPackageServiceImpl.java",
                        test_suite_ref="src/test/java/com/tpm/contract/RequirementPackageContractTest.java",
                        binding_status="verified"
                    )
                ]
            },
            {
                "contract": CodeContract(
                    contract_id="CTR-TPM-PLAN-002",
                    title="采购计划调整申请与填报部门权限契约",
                    category="api",
                    contract_type="JSONSchema",
                    version="1.0.0",
                    status="active",
                    service_name="tpm-backend-app",
                    endpoint_or_path="/api/purchase/plan/adjust",
                    schema_content="""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PurchasePlanAdjustRequest",
  "type": "object",
  "required": ["plan_id", "adjust_type", "adjust_amount", "reason", "operator_dept_id"],
  "properties": {
    "plan_id": {
      "type": "integer",
      "description": "采购计划ID"
    },
    "adjust_type": {
      "type": "string",
      "enum": ["INCREASE", "DECREASE", "ITEM_TRANSFER"],
      "description": "调整类型"
    },
    "adjust_amount": {
      "type": "number",
      "minimum": 0.01,
      "description": "调整金额(万元)"
    },
    "reason": {
      "type": "string",
      "minLength": 10,
      "description": "详细申请调整原因"
    },
    "operator_dept_id": {
      "type": "string",
      "description": "填报部门组织机构代码，与用户鉴权Token必须一致"
    }
  }
}""",
                    description="采购计划调整必须严格校验填报部门本部门归属，禁止跨部门提报调整。",
                    owner="预算管理组",
                    change_policy="independent_pr_required",
                    is_breaking_frozen=False
                ),
                "revisions": [
                    ContractRevision(
                        contract_id="CTR-TPM-PLAN-002",
                        revision_no=1,
                        version="1.0.0",
                        change_type="minor",
                        change_summary="制定采购计划调整JSONSchema输入校验规约",
                        schema_snapshot="{ \"$schema\": \"http://json-schema.org/draft-07/schema#\", \"title\": \"PurchasePlanAdjustRequest\" }",
                        git_commit="b2c3d4e5",
                        pr_reference="PR-CONTRACT-098",
                        approved_by="SecurityReviewer"
                    )
                ],
                "consumers": [
                    ContractConsumer(
                        contract_id="CTR-TPM-PLAN-002",
                        consumer_type="frontend_page",
                        consumer_name="PurchasePlanAdjustModal.vue",
                        consumer_repo="tpm-frontend-web",
                        consumer_path="src/components/purchase/PurchasePlanAdjustModal.vue",
                        binding_status="verified"
                    ),
                    ContractConsumer(
                        contract_id="CTR-TPM-PLAN-002",
                        consumer_type="backend_service",
                        consumer_name="PurchasePlanController.java",
                        consumer_repo="tpm-backend-app",
                        consumer_path="src/main/java/com/tpm/controller/PurchasePlanController.java",
                        binding_status="verified"
                    )
                ]
            },
            {
                "contract": CodeContract(
                    contract_id="CTR-EXT-TALENT-001",
                    title="杭州企业高层次人才分类认定申报公示契约",
                    category="api",
                    contract_type="OpenAPI",
                    version="1.2.0",
                    status="active",
                    service_name="agent-control",
                    endpoint_or_path="/api/v1/extensions/talent-notices",
                    schema_content="""openapi: 3.0.3
info:
  title: 杭州企业高层次人才分类认定申报公示API契约
  version: 1.2.0
paths:
  /api/v1/extensions/talent-notices:
    get:
      summary: 分页检索杭州高层次人才认定公示公告
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
        - name: notice_type
          in: query
          schema:
            type: string
            enum: [personal, list]
        - name: keyword
          in: query
          schema:
            type: string
      responses:
        '200':
          description: 公示数据分页列表
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      type: object
                      properties:
                        title:
                          type: string
                        applicant_name:
                          type: string
                        company_name:
                          type: string
                        talent_level:
                          type: string
                        publish_date:
                          type: string
                  total:
                    type: integer
""",
                    description="保障杭州人才会客厅公示公告与个人清单在采集清洗后，对外提供稳定标准的RESTful查询接口。",
                    owner="数据治理组",
                    change_policy="breaking_freeze",
                    is_breaking_frozen=True
                ),
                "revisions": [
                    ContractRevision(
                        contract_id="CTR-EXT-TALENT-001",
                        revision_no=1,
                        version="1.0.0",
                        change_type="minor",
                        change_summary="初始建立人才公示数据查询规范",
                        schema_snapshot="openapi: 3.0.3\nversion: 1.0.0",
                        git_commit="c3d4e5f6",
                        pr_reference="PR-CONTRACT-050",
                        approved_by="DataGovernanceLead"
                    ),
                    ContractRevision(
                        contract_id="CTR-EXT-TALENT-001",
                        revision_no=2,
                        version="1.2.0",
                        change_type="minor",
                        change_summary="扩充 list 模式结构化解析字段，支持人才认定批次关联",
                        schema_snapshot="openapi: 3.0.3\nversion: 1.2.0",
                        git_commit="d4e5f6g7",
                        pr_reference="PR-CONTRACT-088",
                        approved_by="DataGovernanceLead"
                    )
                ],
                "consumers": [
                    ContractConsumer(
                        contract_id="CTR-EXT-TALENT-001",
                        consumer_type="frontend_page",
                        consumer_name="dashboard.html (Talent Tab)",
                        consumer_repo="agent-control",
                        consumer_path="app/templates/dashboard.html",
                        test_suite_ref="tests/test_talent_dashboard.py",
                        binding_status="verified"
                    ),
                    ContractConsumer(
                        contract_id="CTR-EXT-TALENT-001",
                        consumer_type="subagent",
                        consumer_name="hz-talent-crawler",
                        consumer_repo="agent-control",
                        consumer_path=".agents/skills/hz-talent-crawler/SKILL.md",
                        binding_status="verified"
                    )
                ]
            },
            {
                "contract": CodeContract(
                    contract_id="CTR-EXT-SUBSIDY-002",
                    title="杭州高层次人才购房与租赁补贴公示明细契约",
                    category="api",
                    contract_type="JSONSchema",
                    version="1.0.1",
                    status="active",
                    service_name="agent-control",
                    endpoint_or_path="/api/v1/extensions/housing-subsidies",
                    schema_content="""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HzHousingSubsidyRecordSchema",
  "type": "object",
  "required": ["applicant_name", "company_name", "talent_level", "subsidy_type"],
  "properties": {
    "applicant_name": {
      "type": "string"
    },
    "company_name": {
      "type": "string"
    },
    "talent_level": {
      "type": "string",
      "enum": ["A", "B", "C", "D", "E"]
    },
    "spouse_name": {
      "type": "string"
    },
    "spouse_company": {
      "type": "string"
    },
    "subsidy_type": {
      "type": "string",
      "enum": ["购房补贴", "租赁补贴"]
    },
    "publicity_start": {
      "type": "string",
      "format": "date"
    },
    "publicity_end": {
      "type": "string",
      "format": "date"
    }
  }
}""",
                    description="约束高层次人才住房补贴抓取及前端卡片展示字段规范。",
                    owner="数据治理组",
                    change_policy="independent_pr_required",
                    is_breaking_frozen=False
                ),
                "revisions": [
                    ContractRevision(
                        contract_id="CTR-EXT-SUBSIDY-002",
                        revision_no=1,
                        version="1.0.1",
                        change_type="patch",
                        change_summary="调整配偶单位字段为可选，避免单身申报时校验拦截",
                        schema_snapshot="{ \"$schema\": \"http://json-schema.org/draft-07/schema#\" }",
                        git_commit="f6g7h8i9",
                        pr_reference="PR-CONTRACT-092",
                        approved_by="DataGovernanceLead"
                    )
                ],
                "consumers": [
                    ContractConsumer(
                        contract_id="CTR-EXT-SUBSIDY-002",
                        consumer_type="frontend_page",
                        consumer_name="dashboard.html (Subsidy Tab)",
                        consumer_repo="agent-control",
                        consumer_path="app/templates/dashboard.html",
                        binding_status="verified"
                    )
                ]
            },
            {
                "contract": CodeContract(
                    contract_id="CTR-SYS-HEARTBEAT-001",
                    title="Agent管控节点分布式租约与心跳契约",
                    category="rpc",
                    contract_type="JSONSchema",
                    version="2.0.0",
                    status="active",
                    service_name="agent-control",
                    endpoint_or_path="/api/v1/agents/heartbeat",
                    schema_content="""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentNodeHeartbeatProtocol",
  "type": "object",
  "required": ["agent_id", "node_ip", "lease_token", "capabilities", "current_load"],
  "properties": {
    "agent_id": {
      "type": "string"
    },
    "node_ip": {
      "type": "string",
      "format": "ipv4"
    },
    "lease_token": {
      "type": "string"
    },
    "capabilities": {
      "type": "array",
      "items": { "type": "string" }
    },
    "current_load": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "status": {
      "type": "string",
      "enum": ["online", "busy", "draining", "offline"]
    }
  }
}""",
                    description="Agent管控节点分布式租约与健康心跳仲裁协议。超时60秒自动判定失联收回租约。",
                    owner="分布式系统组",
                    change_policy="breaking_freeze",
                    is_breaking_frozen=True
                ),
                "revisions": [
                    ContractRevision(
                        contract_id="CTR-SYS-HEARTBEAT-001",
                        revision_no=1,
                        version="1.0.0",
                        change_type="minor",
                        change_summary="初代节点心跳上报协议",
                        schema_snapshot="{\"version\": \"1.0.0\"}",
                        git_commit="11223344",
                        pr_reference="PR-CONTRACT-012",
                        approved_by="SystemArch"
                    ),
                    ContractRevision(
                        contract_id="CTR-SYS-HEARTBEAT-001",
                        revision_no=2,
                        version="2.0.0",
                        change_type="major_breaking",
                        change_summary="升级为分布式租约(lease_token)+负载因子自适应调度契约",
                        schema_snapshot="{\"version\": \"2.0.0\", \"lease\": true}",
                        git_commit="55667788",
                        pr_reference="PR-CONTRACT-076",
                        approved_by="PrincipalArchitect"
                    )
                ],
                "consumers": [
                    ContractConsumer(
                        contract_id="CTR-SYS-HEARTBEAT-001",
                        consumer_type="backend_service",
                        consumer_name="AgentService",
                        consumer_repo="agent-control",
                        consumer_path="app/services/agent_service.py",
                        binding_status="verified"
                    ),
                    ContractConsumer(
                        contract_id="CTR-SYS-HEARTBEAT-001",
                        consumer_type="subagent",
                        consumer_name="WorkerAgentsDaemon",
                        consumer_repo="agent-control",
                        consumer_path="daemon/worker.py",
                        binding_status="verified"
                    )
                ]
            },
            {
                "contract": CodeContract(
                    contract_id="CTR-ARCH-LAYER-001",
                    title="TPM分层架构依赖与Controller-Service调用规约",
                    category="dto",
                    contract_type="JavaDTO",
                    version="1.0.0",
                    status="active",
                    service_name="tpm-backend-app",
                    endpoint_or_path="com.tpm.common.dto.Result<T>",
                    schema_content="""package com.tpm.common.dto;

import lombok.Data;
import java.io.Serializable;

/**
 * 契约规范: Controller层统一响应结果包装
 * 契约ID: CTR-ARCH-LAYER-001
 * 规约: 禁止 Controller 返回裸实体或非规范 JSON
 */
@Data
public class Result<T> implements Serializable {
    private static final long serialVersionUID = 1L;

    private Integer code;
    private String message;
    private T data;
    private Long timestamp = System.currentTimeMillis();

    public static <T> Result<T> success(T data) {
        Result<T> r = new Result<>();
        r.setCode(200);
        r.setMessage("SUCCESS");
        r.setData(data);
        return r;
    }

    public static <T> Result<T> failure(Integer code, String message) {
        Result<T> r = new Result<>();
        r.setCode(code);
        r.setMessage(message);
        return r;
    }
}
""",
                    description="Java后端分层架构守卫基础契约：所有REST Controller必须通过统一Result<T>封装响应，禁止跨层直穿DAO。",
                    owner="架构守卫委员会",
                    change_policy="breaking_freeze",
                    is_breaking_frozen=True
                ),
                "revisions": [
                    ContractRevision(
                        contract_id="CTR-ARCH-LAYER-001",
                        revision_no=1,
                        version="1.0.0",
                        change_type="minor",
                        change_summary="制定后端全局统一响应契约与分层规约",
                        schema_snapshot="package com.tpm.common.dto;\npublic class Result<T>...",
                        git_commit="99aabbcc",
                        pr_reference="PR-CONTRACT-001",
                        approved_by="ArchitectureCommittee"
                    )
                ],
                "consumers": [
                    ContractConsumer(
                        contract_id="CTR-ARCH-LAYER-001",
                        consumer_type="backend_service",
                        consumer_name="tpm-backend-app (Controllers)",
                        consumer_repo="tpm-backend-app",
                        consumer_path="src/main/java/com/tpm/controller/",
                        test_suite_ref="src/test/java/com/tpm/arch/ArchitectureGuardTest.java",
                        binding_status="verified"
                    ),
                    ContractConsumer(
                        contract_id="CTR-ARCH-LAYER-001",
                        consumer_type="frontend_page",
                        consumer_name="request.js (Axios拦截器)",
                        consumer_repo="tpm-frontend-web",
                        consumer_path="src/utils/request.js",
                        binding_status="verified"
                    )
                ]
            }
        ]

        for item in contracts_data:
            c = item["contract"]
            db.add(c)
            db.commit()
            db.refresh(c)

            for rev in item["revisions"]:
                db.add(rev)
            for cons in item["consumers"]:
                db.add(cons)

            db.commit()

        print(f"Successfully seeded {len(contracts_data)} contracts with revisions and consumers!")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_code_contracts()
