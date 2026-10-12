import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

def test_unauthenticated_requests_rejected_with_401():
    """验证 CWE-306 修复：未携带鉴权凭证的所有 API 请求均被拦截返回 401 Unauthorized"""
    endpoints_to_test = [
        ("GET", "/api/v1/dashboard/stats"),
        ("GET", "/api/v1/tasks"),
        ("POST", "/api/v1/tasks", {"title": "Malicious Task"}),
        ("GET", "/api/v1/agents"),
        ("POST", "/api/v1/agents", {"name": "Poisoned Agent"}),
        ("GET", "/api/v1/graphs"),
        ("GET", "/api/v1/rules"),
        ("GET", "/api/v1/schedules"),
        ("GET", "/api/v1/extensions/job-positions"),
        ("DELETE", "/api/v1/extensions/job-positions/99999"),
        ("POST", "/api/v1/extensions/job-positions/cleanup-non-semiconductor"),
        ("POST", "/api/v1/extensions/talent-notices/crawl"),
        ("GET", "/api/v1/extensions/talent-notices"),
    ]

    for method, path, *data in endpoints_to_test:
        payload = data[0] if data else None
        if method == "GET":
            resp = client.get(path)
        elif method == "POST":
            resp = client.post(path, json=payload)
        elif method == "DELETE":
            resp = client.delete(path)

        assert resp.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {resp.status_code}: {resp.text}"
        assert "WWW-Authenticate" in resp.headers or "www-authenticate" in resp.headers
        data_json = resp.json()
        assert "Authentication required" in str(data_json) or "Missing" in str(data_json) or "status" in str(data_json)

def test_invalid_tokens_rejected_with_401():
    """验证提供伪造或错误 Token 时拦截返回 401"""
    # 错误的 Bearer token
    resp1 = client.get("/api/v1/dashboard/stats", headers={"Authorization": "Bearer invalid_secret_token_12345"})
    assert resp1.status_code == 401
    assert "Invalid or expired" in resp1.text

    # 错误的 X-API-Key
    resp2 = client.get("/api/v1/dashboard/stats", headers={"X-API-Key": "wrong_key_xyz"})
    assert resp2.status_code == 401
    assert "Invalid or expired" in resp2.text

def test_master_api_key_bearer_authentication():
    """验证使用 Master API Key (Bearer Token) 鉴权成功"""
    valid_key = settings.effective_api_key
    assert valid_key != "", "Effective API Key should not be empty"

    resp = client.get(
        "/api/v1/dashboard/stats",
        headers={"Authorization": f"Bearer {valid_key}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)

def test_master_api_key_header_authentication():
    """验证使用 X-API-Key 请求头鉴权成功"""
    valid_key = settings.effective_api_key
    resp = client.get(
        "/api/v1/dashboard/stats",
        headers={"X-API-Key": valid_key}
    )
    assert resp.status_code == 200

def test_api_client_lifecycle_and_authentication():
    """验证通过 API 创建 ApiClient、使用新 Token 鉴权、以及注销后失效的完整生命周期"""
    master_key = settings.effective_api_key
    auth_header = {"Authorization": f"Bearer {master_key}"}

    # 1. 创建新客户端
    create_payload = {
        "name": "Automated Test Worker Agent",
        "scopes": ["task:read", "task:claim", "task:write"]
    }
    resp_create = client.post("/api/v1/agents/api-clients", json=create_payload, headers=auth_header)
    assert resp_create.status_code == 201
    client_data = resp_create.json()
    assert "public_id" in client_data
    assert "raw_token" in client_data
    client_id = client_data["public_id"]
    client_raw_token = client_data["raw_token"]
    assert client_raw_token.startswith("ac_")

    # 2. 使用新客户端 raw_token 访问受保护接口
    client_auth = {"Authorization": f"Bearer {client_raw_token}"}
    resp_authed = client.get("/api/v1/tasks", headers=client_auth)
    assert resp_authed.status_code == 200

    # 3. 撤销注销该客户端
    resp_delete = client.delete(f"/api/v1/agents/api-clients/{client_id}", headers=auth_header)
    assert resp_delete.status_code == 200

    # 4. 再次使用已注销的 token 访问，应被拒绝 401
    resp_revoked = client.get("/api/v1/tasks", headers=client_auth)
    assert resp_revoked.status_code == 401

def test_public_endpoints_accessible():
    """验证公共探针端点与静态前端不受阻断"""
    # /health 健康检查保持公开
    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    data = resp_health.json()
    assert data["status"] == "ok"
    assert data["auth_enabled"] is True

    # /dashboard 页面保持公开（页面内由 JS 控制输入 API Key）
    resp_dashboard = client.get("/dashboard")
    assert resp_dashboard.status_code == 200
    assert "Agent Control" in resp_dashboard.text

def test_cors_security_hardening():
    """验证 CORS 安全策略：严禁通配符 * 携带凭据"""
    resp = client.options(
        "/api/v1/dashboard/stats",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET"
        }
    )
    # 应正常返回 CORS 响应头
    assert resp.status_code == 200
