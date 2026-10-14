#!/usr/bin/env python3
"""
Seed realistic Anti-weakening Arbitration & Architecture Guard Logs into MySQL agent_control.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import SessionLocal
from app.models.contract import ArbitrationGuardLog

def seed_logs():
    db = SessionLocal()
    try:
        sample_logs = [
            {
                "event_id": "ARB-EVT-20261014-001",
                "contract_id": "CTR-TPM-PKG-001",
                "event_type": "test_assertion_weakened",
                "source_repo": "tpm-backend-app",
                "target_file": "src/test/java/com/sys/tpm/service/PackageServiceTest.java",
                "operator_or_agent": "AI-Refactor-Agent",
                "rule_name": "禁止弱化单元测试断言以规避打包校验异常",
                "diff_snippet": "- assertEquals(\"SUCCESS\", result.getStatus());\n- assertEquals(3, result.getItems().size());\n+ // assertEquals(\"SUCCESS\", result.getStatus());\n+ assertTrue(true); // temporary workaround for CI",
                "interception_action": "blocked",
                "severity": "CRITICAL",
                "arbitration_decision": "【硬阻断】检测到AI试图用 assertTrue(true) 伪造断言逃避单测失败。仲裁规则：优先级【契约 > 测试 > 架构规则 > 现有代码 > AI判断】，禁止放宽断言让构建通过。",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "blocked",
                "created_at": datetime.utcnow() - timedelta(hours=3, minutes=20)
            },
            {
                "event_id": "ARB-EVT-20261014-002",
                "contract_id": "CTR-TPM-EXP-002",
                "event_type": "lint_rule_ignored",
                "source_repo": "tpm-frontend-web",
                "target_file": "src/views/purchase/CentralizedPackageView.vue",
                "operator_or_agent": "AI-Frontend-Coder",
                "rule_name": "禁止在Vue单文件组件注入eslint-disable以规避类型审查",
                "diff_snippet": "+ /* eslint-disable @typescript-eslint/no-explicit-any */\n+ const handleExport = (rawPayload: any) => {\n+   console.log(rawPayload);\n+ }",
                "interception_action": "blocked",
                "severity": "HIGH",
                "arbitration_decision": "【硬阻断】检测到新增 eslint-disable 规避 any 类型校验。前端代码契约要求严格强类型约束，禁止添加忽略注释。",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "blocked",
                "created_at": datetime.utcnow() - timedelta(hours=2, minutes=45)
            },
            {
                "event_id": "ARB-EVT-20261014-003",
                "contract_id": "CTR-TPM-BUD-003",
                "event_type": "threshold_lowered",
                "source_repo": "tpm-backend-app",
                "target_file": "pom.xml",
                "operator_or_agent": "AI-CI-Helper",
                "rule_name": "禁止下调 JaCoCo 单元测试覆盖率门禁预算",
                "diff_snippet": "- <minimum>0.80</minimum>\n+ <minimum>0.55</minimum> <!-- Lowered because new module lacks tests -->",
                "interception_action": "blocked",
                "severity": "CRITICAL",
                "arbitration_decision": "【硬阻断】检测到pom.xml核心测试覆盖率阈值从80%下调至55%。仲裁层铁律：禁止调低预算指标掩盖单测缺失！",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "blocked",
                "created_at": datetime.utcnow() - timedelta(hours=2, minutes=10)
            },
            {
                "event_id": "ARB-EVT-20261014-004",
                "contract_id": "CTR-TPM-DEV-004",
                "event_type": "layer_violation",
                "source_repo": "tpm-backend-app",
                "target_file": "src/main/java/com/sys/tpm/controller/DeviceLedgerController.java",
                "operator_or_agent": "AI-Backend-Dev",
                "rule_name": "禁止Controller表现层跨层直接注入与调用DAO/Repository",
                "diff_snippet": "+ import com.sys.tpm.dao.DeviceLedgerDao;\n+ @Autowired\n+ private DeviceLedgerDao deviceLedgerDao;\n+\n+ @GetMapping(\"/quick-list\")\n+ public List<Device> quickList() {\n+   return deviceLedgerDao.selectAll();\n+ }",
                "interception_action": "blocked",
                "severity": "CRITICAL",
                "arbitration_decision": "【分层架构硬阻断】表现层Controller严禁跨过Service层直调DAO，破坏了领域事务、安全切面与分层边界。\n[人工仲裁确认违规阻断 - 2026-10-14 15:20:00 由 ArchCommittee]: 确认违反三层架构规约，已勒令整改重构为通过 DeviceLedgerAppService 调用。",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "confirmed_violation",
                "created_at": datetime.utcnow() - timedelta(hours=1, minutes=30),
                "resolved_at": datetime.utcnow() - timedelta(minutes=40)
            },
            {
                "event_id": "ARB-EVT-20261014-005",
                "contract_id": "CTR-TPM-PRC-005",
                "event_type": "test_deleted",
                "source_repo": "tpm-backend-app",
                "target_file": "src/test/java/com/sys/tpm/service/ProcurementContractTest.java",
                "operator_or_agent": "AI-Test-Optimizer",
                "rule_name": "禁止擅自删除失败的集成验收与边界测试用例",
                "diff_snippet": "- @Test\n- void testProcurementAmountValidationNegative() {\n-     assertThrows(IllegalArgumentException.class, () -> service.createPlan(-100));\n- }",
                "interception_action": "blocked",
                "severity": "CRITICAL",
                "arbitration_decision": "【破坏性拦截】检测到采购金额负向校验用例 testProcurementAmountValidationNegative 被直接删除。删除测试视为严重弱化系统防护网行为，立即阻断当前提交！",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "blocked",
                "created_at": datetime.utcnow() - timedelta(minutes=55)
            },
            {
                "event_id": "ARB-EVT-20261014-006",
                "contract_id": "CTR-TPM-PKG-001",
                "event_type": "protected_file_modified",
                "source_repo": "agent-control",
                "target_file": ".github/workflows/contract-guard.yml",
                "operator_or_agent": "AI-DevOps",
                "rule_name": "受保护CI工作流与守卫规则配置文件禁止私自篡改",
                "diff_snippet": "- - run: npm run guard:verify --fail-on-violation\n+ - run: npm run guard:verify || true",
                "interception_action": "blocked",
                "severity": "CRITICAL",
                "arbitration_decision": "【高危拦截】CODEOWNERS与受保护CI守卫配置被私自修改为 `|| true`，企图掩盖检查错误。已自动回滚并阻断PR流水线。",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "blocked",
                "created_at": datetime.utcnow() - timedelta(minutes=35)
            },
            {
                "event_id": "ARB-EVT-20261014-007",
                "contract_id": "CTR-TPM-AUTH-006",
                "event_type": "contract_bypassed",
                "source_repo": "tpm-backend-app",
                "target_file": "src/main/resources/contracts/auth-tokens.yaml",
                "operator_or_agent": "AI-Backend-Dev",
                "rule_name": "契约定义变更必须走独立审批PR流程",
                "diff_snippet": "+   /api/v1/auth/exchange-refresh:\n+     post:\n+       summary: 紧急新增Token置换端点 (未独立走契约审批)",
                "interception_action": "adr_exception_granted",
                "severity": "HIGH",
                "arbitration_decision": "【ADR破例特批】契约定义未经独立PR即跟随功能代码提交，原应阻断。因国庆上线紧急保活，由架构师特批短期例外。\n[ADR特批处置 - 2026-10-14 09:15:00 由 ChiefArchitect]: 破例理由: 生产网关容灾置换Token紧急兜底。关联ADR: ADR-2026-TPM-012，过期时间: 2026-11-14。",
                "adr_reference": "ADR-2026-TPM-012",
                "adr_expires_at": datetime.utcnow() + timedelta(days=30),
                "status": "waived_by_adr",
                "created_at": datetime.utcnow() - timedelta(hours=5),
                "resolved_at": datetime.utcnow() - timedelta(hours=4, minutes=50)
            },
            {
                "event_id": "ARB-EVT-20261014-008",
                "contract_id": "CTR-TPM-EXP-002",
                "event_type": "test_assertion_weakened",
                "source_repo": "tpm-frontend-web",
                "target_file": "src/views/purchase/__tests__/CentralizedPackage.spec.ts",
                "operator_or_agent": "AI-Frontend-Coder",
                "rule_name": "禁止吞掉异步请求错误断言或空catch块",
                "diff_snippet": "- expect(wrapper.find('.error-alert').exists()).toBe(true)\n+ // expect(wrapper.find('.error-alert').exists()).toBe(true)\n+ try { await flushPromises() } catch (e) {}",
                "interception_action": "manual_confirmation_required",
                "severity": "HIGH",
                "arbitration_decision": "【待人工确认】异步错误渲染断言被放宽并注入空catch块，触发卡点并挂起，等待测试组长人工确认。",
                "adr_reference": None,
                "adr_expires_at": None,
                "status": "pending_review",
                "created_at": datetime.utcnow() - timedelta(minutes=15)
            }
        ]

        inserted = 0
        for data in sample_logs:
            existing = db.query(ArbitrationGuardLog).filter(ArbitrationGuardLog.event_id == data["event_id"]).first()
            if not existing:
                log_entry = ArbitrationGuardLog(**data)
                db.add(log_entry)
                inserted += 1
        db.commit()
        print(f"Successfully seeded {inserted} arbitration guard log records.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_logs()
