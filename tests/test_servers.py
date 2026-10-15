import os
import tempfile
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.session import Base, get_db
from app.core.security import get_current_client
from app.core.vault import encrypt_secret, decrypt_secret, mask_secret, redact_sensitive_output
from app.models.server_credential import ServerCredential, ServerAccessLog


# 使用内存 SQLite 进行无外部依赖隔离单元测试
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_client():
    return {"id": 0, "public_id": "CLIENT_TEST", "name": "TestMaster", "scopes": ["*"], "is_master": True}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_client] = override_get_current_client
client = TestClient(app)


def test_vault_encryption_and_redaction():
    raw_pwd = "MySuperSecretPwd!2026#TPM"
    cipher = encrypt_secret(raw_pwd)
    assert cipher is not None
    assert raw_pwd not in cipher
    assert decrypt_secret(cipher) == raw_pwd
    assert mask_secret(cipher) == "********"

    noisy_output = f"Connecting with {raw_pwd}\nroot@10.0.0.1's password: \nDeployment finished."
    cleaned = redact_sensitive_output(noisy_output, [raw_pwd])
    assert raw_pwd not in cleaned
    assert "[REDACTED_SECRET]" in cleaned
    assert "Deployment finished." in cleaned


def test_server_crud_and_zero_password_exposure():
    # 1. 创建服务器凭据
    create_resp = client.post(
        "/api/v1/servers",
        json={
            "server_id": "SRV-TEST-001",
            "name": "测试应用服务器",
            "project_name": "tpm-backend-app",
            "environment": "test",
            "host": "10.20.30.40",
            "port": 2222,
            "username": "deploy",
            "auth_type": "password",
            "password": "PlainTextPasswordShouldNeverLeak123!",
            "default_workdir": "/opt/tpm-app",
            "tags": ["java", "spring"],
            "description": "自动化单元测试服务器",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()["server"]
    assert created["server_id"] == "SRV-TEST-001"
    assert created["has_password"] is True
    assert created["password_masked"] == "********"
    assert "PlainTextPasswordShouldNeverLeak123!" not in create_resp.text
    assert "password_cipher" not in created

    # 验证数据库中确实是密文存储
    db = TestingSessionLocal()
    row = db.query(ServerCredential).filter(ServerCredential.server_id == "SRV-TEST-001").first()
    assert row is not None
    assert row.password_cipher is not None
    assert "PlainTextPasswordShouldNeverLeak123!" not in row.password_cipher
    assert decrypt_secret(row.password_cipher) == "PlainTextPasswordShouldNeverLeak123!"
    db.close()

    # 2. 查询列表与详情，确保密码掩码保护
    list_resp = client.get("/api/v1/servers?project_name=tpm-backend-app")
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) >= 1
    assert items[0]["password_masked"] == "********"
    assert "PlainTextPasswordShouldNeverLeak123!" not in list_resp.text

    # 3. 更新服务器信息且密码留空，验证原加密密码保持不变
    upd_resp = client.put(
        "/api/v1/servers/SRV-TEST-001",
        json={
            "name": "测试应用服务器(已更新)",
            "password": "",  # 留空不覆盖
            "port": 2200,
        },
    )
    assert upd_resp.status_code == 200
    assert upd_resp.json()["server"]["name"] == "测试应用服务器(已更新)"
    assert upd_resp.json()["server"]["port"] == 2200

    db = TestingSessionLocal()
    row_after = db.query(ServerCredential).filter(ServerCredential.server_id == "SRV-TEST-001").first()
    assert decrypt_secret(row_after.password_cipher) == "PlainTextPasswordShouldNeverLeak123!"
    db.close()


@patch("app.api.v1.servers.execute_remote_command")
@patch("app.api.v1.servers.transfer_remote_file")
def test_agent_exec_upload_and_download_by_server_id(mock_transfer, mock_exec):
    mock_exec.return_value = {
        "success": True,
        "exit_code": 0,
        "output": "Linux tpm-node 5.15.0 x86_64",
        "duration_sec": 0.15,
    }
    mock_transfer.return_value = {
        "success": True,
        "direction": "upload",
        "local_path": "/tmp/a",
        "remote_path": "/opt/tpm-app/a",
        "exit_code": 0,
        "output": "Transfer complete",
        "duration_sec": 0.25,
    }

    # 1. 免密执行远程命令
    exec_resp = client.post(
        "/api/v1/servers/SRV-TEST-001/exec",
        json={"command": "uname -a", "operator": "Pytest-Agent"},
    )
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["success"] is True
    assert "Linux tpm-node" in exec_data["output"]

    # 2. 免密上传文件 (按内联文本内容或本地路径)
    up_resp = client.post(
        "/api/v1/servers/SRV-TEST-001/upload",
        json={
            "remote_path": "/opt/tpm-app/deploy.sh",
            "content_text": "#!/bin/bash\necho hello\n",
            "filename": "deploy.sh",
            "operator": "Pytest-Agent",
        },
    )
    assert up_resp.status_code == 200
    assert up_resp.json()["success"] is True

    # 3. 免密下载文件
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_dst = tf.name
    try:
        down_resp = client.post(
            "/api/v1/servers/SRV-TEST-001/download",
            json={
                "remote_path": "/opt/tpm-app/deploy.sh",
                "local_path": temp_dst,
                "operator": "Pytest-Agent",
            },
        )
        assert down_resp.status_code == 200
        assert down_resp.json()["success"] is True
    finally:
        if os.path.exists(temp_dst):
            os.remove(temp_dst)

    # 4. 检查审计日志已生成
    logs_resp = client.get("/api/v1/servers/logs?server_id=SRV-TEST-001")
    assert logs_resp.status_code == 200
    assert logs_resp.json()["total"] >= 3
