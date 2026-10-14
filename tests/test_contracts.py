import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)
auth_headers = {"Authorization": f"Bearer {settings.effective_api_key}"}

def test_contracts_auth_protection():
    """验证未提供Token时拦截401"""
    resp = client.get("/api/v1/contracts")
    assert resp.status_code == 401

    resp = client.get("/api/v1/contracts/stats")
    assert resp.status_code == 401

def test_contracts_list_and_pagination():
    """验证契约列表查询与标准分页结构"""
    resp = client.get("/api/v1/contracts?page=1&page_size=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 6
    assert len(data["items"]) <= 5

    # 验证字段完整性
    first = data["items"][0]
    assert "contract_id" in first
    assert "title" in first
    assert "version" in first
    assert "service_name" in first
    assert "change_policy" in first

def test_contracts_filter():
    """验证按服务与类型过滤"""
    resp = client.get("/api/v1/contracts?service_name=tpm-backend-app", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["service_name"] == "tpm-backend-app"

    resp_kw = client.get("/api/v1/contracts?keyword=集中打包", headers=auth_headers)
    assert resp_kw.status_code == 200
    kw_data = resp_kw.json()
    assert kw_data["total"] >= 1
    assert any(c["contract_id"] == "CTR-TPM-PKG-001" for c in kw_data["items"])

def test_contracts_stats():
    """验证契约全局度量统计API"""
    resp = client.get("/api/v1/contracts/stats", headers=auth_headers)
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_contracts"] >= 6
    assert stats["total_revisions"] >= 6
    assert stats["total_consumers"] >= 6
    assert "categories_distribution" in stats
    assert "types_distribution" in stats

def test_contracts_revisions_and_consumers_endpoints():
    """验证修订流水线和消费端拓扑独立列表API"""
    rev_resp = client.get("/api/v1/contracts/revisions?page=1&page_size=10", headers=auth_headers)
    assert rev_resp.status_code == 200
    rev_data = rev_resp.json()
    assert rev_data["total"] >= 6
    assert "change_summary" in rev_data["items"][0]

    cons_resp = client.get("/api/v1/contracts/consumers?page=1&page_size=10", headers=auth_headers)
    assert cons_resp.status_code == 200
    cons_data = cons_resp.json()
    assert cons_data["total"] >= 6
    assert "consumer_name" in cons_data["items"][0]

def test_contract_detail_with_relations():
    """验证单条契约详情及其级联关系"""
    resp = client.get("/api/v1/contracts/CTR-TPM-PKG-001", headers=auth_headers)
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["contract_id"] == "CTR-TPM-PKG-001"
    assert detail["revisions_count"] >= 2
    assert len(detail["revisions"]) >= 2
    assert len(detail["consumers"]) >= 2
    assert detail["is_breaking_frozen"] is True

def test_contract_verify_schema():
    """验证契约Schema语法校验器"""
    # 验证有效 JSONSchema
    valid_json = '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object"}'
    resp = client.post("/api/v1/contracts/verify-schema", headers=auth_headers, json={
        "contract_type": "JSONSchema",
        "content": valid_json
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is True

    # 验证无效 JSON
    invalid_json = '{"$schema": "http://json-schema.org/draft-07/schema#", "type": '
    resp_inv = client.post("/api/v1/contracts/verify-schema", headers=auth_headers, json={
        "contract_type": "JSONSchema",
        "content": invalid_json
    })
    assert resp_inv.status_code == 200
    assert resp_inv.json()["valid"] is False
    assert "error" in resp_inv.json()

def test_contract_lifecycle_create_update_and_consumer():
    """验证契约完整生命周期: 创建 -> 升级变更生成Revision -> 绑定消费者 -> 删除"""
    test_id = "CTR-TEST-AUTOTEST-999"
    # 幂等清理
    client.delete(f"/api/v1/contracts/{test_id}", headers=auth_headers)

    # 1. 创建契约
    create_payload = {
        "contract_id": test_id,
        "title": "单元自动化测试契约",
        "category": "api",
        "contract_type": "JSONSchema",
        "version": "1.0.0",
        "service_name": "test-service",
        "endpoint_or_path": "/api/test/auto",
        "schema_content": '{"type": "object", "properties": {"id": {"type": "integer"}}}',
        "description": "临时自动化契约用于测试审计流",
        "owner": "QA-Agent",
        "change_policy": "independent_pr_required",
        "is_breaking_frozen": False
    }
    c_resp = client.post("/api/v1/contracts", headers=auth_headers, json=create_payload)
    assert c_resp.status_code == 201
    res_data = c_resp.json()
    assert res_data["contract_id"] == test_id

    # 2. 升级版本（触发独立变更审计）
    update_payload = {
        "title": "单元自动化测试契约(升级版)",
        "version": "1.1.0",
        "schema_content": '{"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}',
        "change_type": "minor",
        "change_summary": "增加 name 字段契约声明",
        "git_commit": "1234abcd",
        "pr_reference": "PR-TEST-999",
        "approved_by": "TestReviewer"
    }
    u_resp = client.put(f"/api/v1/contracts/{test_id}", headers=auth_headers, json=update_payload)
    assert u_resp.status_code == 200
    updated_data = u_resp.json()
    assert updated_data["new_version"] == "1.1.0"
    assert updated_data["revision_no"] == 2

    # 3. 绑定消费者
    cons_payload = {
        "consumer_type": "frontend_page",
        "consumer_name": "TestAutoView.vue",
        "consumer_repo": "tpm-frontend-web",
        "consumer_path": "src/views/TestAutoView.vue",
        "binding_status": "verified"
    }
    bind_resp = client.post(f"/api/v1/contracts/{test_id}/consumers", headers=auth_headers, json=cons_payload)
    assert bind_resp.status_code == 201
    assert bind_resp.json()["consumer_name"] == "TestAutoView.vue"

    # 4. 删除清理
    del_resp = client.delete(f"/api/v1/contracts/{test_id}", headers=auth_headers)
    assert del_resp.status_code == 200
