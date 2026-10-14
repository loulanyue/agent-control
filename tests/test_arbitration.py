import os
import sys
import uuid
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)
auth_headers = {"Authorization": f"Bearer {settings.effective_api_key}"}

def test_arbitration_auth_protection():
    """验证未提供Token时拦截401"""
    resp = client.get("/api/v1/contracts/arbitration/stats")
    assert resp.status_code == 401

    resp = client.get("/api/v1/contracts/arbitration/logs")
    assert resp.status_code == 401

    resp = client.post("/api/v1/contracts/arbitration/simulate-detector", json={
        "file_path": "src/test/java/Test.java",
        "diff_content": "+ assertTrue(true);"
    })
    assert resp.status_code == 401

def test_arbitration_stats():
    """验证防弱化与架构仲裁全景度量API"""
    resp = client.get("/api/v1/contracts/arbitration/stats", headers=auth_headers)
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_interceptions" in stats
    assert "blocked_count" in stats
    assert "blocked_rate" in stats
    assert "by_event_type" in stats
    assert "by_repo" in stats
    assert "by_severity" in stats
    assert "recent_events" in stats
    assert stats["total_interceptions"] >= 8
    assert len(stats["recent_events"]) <= 6

def test_arbitration_logs_pagination_and_filter():
    """验证防弱化拦截日志分页、过滤与关键词搜索"""
    # 1. 分页查询
    resp = client.get("/api/v1/contracts/arbitration/logs?page=1&page_size=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 8
    assert len(data["items"]) <= 5

    first = data["items"][0]
    assert "event_id" in first
    assert "rule_name" in first
    assert "severity" in first
    assert "interception_action" in first
    assert "status" in first

    # 2. 按事件类型过滤
    resp_type = client.get("/api/v1/contracts/arbitration/logs?event_type=test_assertion_weakened", headers=auth_headers)
    assert resp_type.status_code == 200
    data_type = resp_type.json()
    assert data_type["total"] >= 1
    for item in data_type["items"]:
        assert item["event_type"] == "test_assertion_weakened"

    # 3. 按仓库过滤
    resp_repo = client.get("/api/v1/contracts/arbitration/logs?source_repo=tpm-frontend-web", headers=auth_headers)
    assert resp_repo.status_code == 200
    data_repo = resp_repo.json()
    assert data_repo["total"] >= 1
    for item in data_repo["items"]:
        assert item["source_repo"] == "tpm-frontend-web"

    # 4. 关键词搜索
    resp_kw = client.get("/api/v1/contracts/arbitration/logs?keyword=eslint-disable", headers=auth_headers)
    assert resp_kw.status_code == 200
    data_kw = resp_kw.json()
    assert data_kw["total"] >= 1

def test_arbitration_log_lifecycle_and_action():
    """验证拦截事件上报、人工确认与ADR破例特批流转"""
    test_event_id = f"ARB-EVT-TEST-{uuid.uuid4().hex[:8].upper()}"

    # 1. 上报新拦截日志
    create_payload = {
        "event_id": test_event_id,
        "contract_id": "CTR-TPM-TEST-999",
        "event_type": "test_assertion_weakened",
        "source_repo": "tpm-backend-app",
        "target_file": "src/test/java/com/sys/tpm/TestSample.java",
        "operator_or_agent": "AI-Pytest-Agent",
        "rule_name": "禁止弱化单测断言以逃避构建错误",
        "diff_snippet": "+ // assertEquals(true, result);\n+ assertTrue(true);",
        "interception_action": "blocked",
        "severity": "CRITICAL",
        "arbitration_decision": "依据契约仲裁优先级，禁止放宽断言，已执行阻断！",
        "status": "blocked"
    }
    resp = client.post("/api/v1/contracts/arbitration/logs", json=create_payload, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["event_id"] == test_event_id

    # 2. 模拟人工仲裁确认违规
    action_payload = {
        "action": "confirm_blocked",
        "operator": "ArchLead",
        "reason": "人工核验确认违规，维持硬阻断！"
    }
    resp_act = client.post(f"/api/v1/contracts/arbitration/logs/{test_event_id}/action", json=action_payload, headers=auth_headers)
    assert resp_act.status_code == 200
    assert resp_act.json()["status"] == "confirmed_violation"

    # 3. 授予 ADR 破例特批
    adr_payload = {
        "action": "grant_adr_exception",
        "operator": "ChiefArchitect",
        "adr_reference": "ADR-2026-TPM-999",
        "reason": "国庆上线故障容灾紧急特批，限期30天整改"
    }
    resp_adr = client.post(f"/api/v1/contracts/arbitration/logs/{test_event_id}/action", json=adr_payload, headers=auth_headers)
    assert resp_adr.status_code == 200
    assert resp_adr.json()["status"] == "waived_by_adr"

    # 4. 再次查询核验
    resp_check = client.get(f"/api/v1/contracts/arbitration/logs?keyword={test_event_id}", headers=auth_headers)
    assert resp_check.status_code == 200
    items = resp_check.json()["items"]
    assert len(items) == 1
    assert items[0]["adr_reference"] == "ADR-2026-TPM-999"
    assert items[0]["status"] == "waived_by_adr"

def test_anti_weakening_simulate_detector():
    """验证防弱化仿真探测器多维卡点规则"""
    # 场景 1: 恒真断言与空 catch
    sim_1 = client.post("/api/v1/contracts/arbitration/simulate-detector", json={
        "file_path": "src/test/java/com/sys/tpm/OrderTest.java",
        "diff_content": "+ assertTrue(true);\n+ catch(Exception e) {}",
        "repo_name": "tpm-backend-app"
    }, headers=auth_headers)
    assert sim_1.status_code == 200
    res_1 = sim_1.json()
    assert res_1["violation_detected"] is True
    assert res_1["action"] == "blocked"
    assert res_1["severity"] == "CRITICAL"
    assert any("恒真虚假断言" in r["pattern_matched"] for r in res_1["matched_rules"])
    assert any("空白 catch" in r["pattern_matched"] for r in res_1["matched_rules"])

    # 场景 2: 前端注入 eslint-disable
    sim_2 = client.post("/api/v1/contracts/arbitration/simulate-detector", json={
        "file_path": "src/views/Main.vue",
        "diff_content": "+ /* eslint-disable @typescript-eslint/no-explicit-any */\n+ const a: any = 1;",
        "repo_name": "tpm-frontend-web"
    }, headers=auth_headers)
    assert sim_2.status_code == 200
    res_2 = sim_2.json()
    assert res_2["violation_detected"] is True
    assert any("ESLint" in r["pattern_matched"] for r in res_2["matched_rules"])

    # 场景 3: 架构跨层 Controller 直调 DAO
    sim_3 = client.post("/api/v1/contracts/arbitration/simulate-detector", json={
        "file_path": "src/main/java/com/sys/tpm/controller/UserController.java",
        "diff_content": "+ import com.sys.tpm.dao.UserDao;\n+ @Autowired\n+ private UserDao userDao;",
        "repo_name": "tpm-backend-app"
    }, headers=auth_headers)
    assert sim_3.status_code == 200
    res_3 = sim_3.json()
    assert res_3["violation_detected"] is True
    assert any("跨层直调持久层" in r["rule_name"] for r in res_3["matched_rules"])

    # 场景 4: 篡改受保护核心工作流
    sim_4 = client.post("/api/v1/contracts/arbitration/simulate-detector", json={
        "file_path": ".github/workflows/ci.yml",
        "diff_content": "- npm test\n+ npm test || true",
        "repo_name": "agent-control"
    }, headers=auth_headers)
    assert sim_4.status_code == 200
    res_4 = sim_4.json()
    assert res_4["violation_detected"] is True
    assert any("受保护" in r["rule_name"] for r in res_4["matched_rules"])

    # 场景 5: 正常合规代码修改 (允许通过)
    sim_clean = client.post("/api/v1/contracts/arbitration/simulate-detector", json={
        "file_path": "src/main/java/com/sys/tpm/service/UserService.java",
        "diff_content": "+ public String getFullName(String first, String last) {\n+     return first + ' ' + last;\n+ }",
        "repo_name": "tpm-backend-app"
    }, headers=auth_headers)
    assert sim_clean.status_code == 200
    res_clean = sim_clean.json()
    assert res_clean["violation_detected"] is False
    assert res_clean["action"] == "allowed"
    assert len(res_clean["matched_rules"]) == 0
