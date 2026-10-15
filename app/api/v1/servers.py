import base64
import os
import tempfile
from datetime import datetime
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func

from db.session import get_db
from app.models.server_credential import ServerCredential, ServerAccessLog
from app.schemas.pagination import PageResult, paginate_query
from app.core.vault import (
    encrypt_secret,
    mask_secret,
    test_tcp_and_ssh_banner,
    execute_remote_command,
    transfer_remote_file,
)

router = APIRouter(prefix="/servers", tags=["Server Credentials & Agent Vault"])

_TABLES_INITIALIZED = False


def ensure_server_tables_initialized(db: Session) -> None:
    """
    惰性幂等初始化：确保 server_credentials 与 server_access_logs 表已创建并在空表时写入初始示例数据。
    """
    global _TABLES_INITIALIZED
    if _TABLES_INITIALIZED:
        return
    try:
        bind = db.get_bind()
        ServerCredential.__table__.create(bind=bind, checkfirst=True)
        ServerAccessLog.__table__.create(bind=bind, checkfirst=True)
        count = db.query(func.count(ServerCredential.id)).scalar() or 0
        if count == 0 and bind.dialect.name != "sqlite":
            from scripts.seed_servers import seed_server_credentials
            seed_server_credentials()
        _TABLES_INITIALIZED = True
    except Exception:
        pass


# ----------------------------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------------------------
class ServerCreateRequest(BaseModel):
    server_id: str = Field(..., description="唯一服务器标识/别名，如 SRV-TPM-PROD-01，供 Agent 免密调用")
    name: str = Field(..., description="服务器名称，如 TPM 生产应用服务器")
    project_name: str = Field("tpm-backend-app", description="所属项目名称")
    environment: str = Field("prod", description="所属环境: prod / staging / test / dev")
    host: str = Field(..., description="服务器 IP 地址或域名")
    port: int = Field(22, ge=1, le=65535, description="SSH 端口，默认 22")
    username: str = Field("root", description="登录用户名")
    auth_type: str = Field("password", description="认证方式: password / ssh_key")
    password: Optional[str] = Field(None, description="登录密码明文（仅入库加密使用，绝不回显）")
    private_key: Optional[str] = Field(None, description="SSH 私钥明文（仅入库加密使用，绝不回显）")
    default_workdir: Optional[str] = Field("/opt/app", description="默认远程工作目录")
    tags: Optional[List[str]] = Field(default_factory=list, description="服务器用途标签")
    description: Optional[str] = Field(None, description="服务器用途说明与部署组件备注")
    status: str = Field("active", description="状态: active / disabled")
    created_by: str = Field("Admin", description="创建人")


class ServerUpdateRequest(BaseModel):
    name: Optional[str] = None
    project_name: Optional[str] = None
    environment: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = None
    auth_type: Optional[str] = None
    password: Optional[str] = Field(None, description="留空或传 ******** 表示保持原密码不变")
    private_key: Optional[str] = Field(None, description="留空或传 ******** 表示保持原私钥不变")
    default_workdir: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[str] = None
    operator: str = Field("Admin", description="操作人")


class ServerExecRequest(BaseModel):
    command: str = Field(..., description="要在目标服务器执行的 Shell 命令")
    workdir: Optional[str] = Field(None, description="执行工作目录（不传则使用服务器 default_workdir）")
    timeout: int = Field(60, ge=5, le=600, description="超时秒数")
    operator: str = Field("Agent", description="调用方标识: MCP-Agent / SDK / Dashboard")


class ServerUploadRequest(BaseModel):
    local_path: Optional[str] = Field(None, description="宿主机本地文件或目录绝对路径")
    remote_path: str = Field(..., description="目标服务器远程路径，如 /opt/app/app.jar")
    content_text: Optional[str] = Field(None, description="可选：直接传入文本内容生成文件并上传")
    content_base64: Optional[str] = Field(None, description="可选：直接传入 Base64 编码二进制内容并上传")
    filename: Optional[str] = Field(None, description="当使用 content_text/content_base64 时的文件名")
    recursive: bool = Field(False, description="是否递归上传目录 (-r)")
    timeout: int = Field(120, ge=5, le=1800, description="超时秒数")
    operator: str = Field("Agent", description="调用方标识")


class ServerDownloadRequest(BaseModel):
    remote_path: str = Field(..., description="目标服务器上的源文件路径")
    local_path: Optional[str] = Field(None, description="下载保存到宿主机本地的目标路径（可选）")
    recursive: bool = Field(False, description="是否递归下载目录 (-r)")
    return_content: bool = Field(False, description="是否直接在响应中返回文件内容预览/Base64")
    timeout: int = Field(120, ge=5, le=1800, description="超时秒数")
    operator: str = Field("Agent", description="调用方标识")


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _serialize_server(s: ServerCredential) -> Dict[str, Any]:
    """
    安全序列化服务器信息：
    严禁返回 password_cipher 或 private_key_cipher，统一返回掩码 ******** 与布尔状态位。
    """
    has_pwd = bool(s.password_cipher)
    has_key = bool(s.private_key_cipher)
    return {
        "id": s.id,
        "server_id": s.server_id,
        "name": s.name,
        "project_name": s.project_name,
        "environment": s.environment,
        "host": s.host,
        "port": s.port,
        "username": s.username,
        "auth_type": s.auth_type,
        "has_password": has_pwd,
        "has_private_key": has_key,
        "password_masked": mask_secret(s.password_cipher) if has_pwd else (mask_secret(s.private_key_cipher) if has_key else ""),
        "default_workdir": s.default_workdir or "/opt/app",
        "tags": s.tags if isinstance(s.tags, list) else [],
        "description": s.description or "",
        "status": s.status,
        "last_check_status": s.last_check_status or "unknown",
        "last_check_message": s.last_check_message or "",
        "last_check_at": s.last_check_at.isoformat() if s.last_check_at else None,
        "created_by": s.created_by,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        "agent_usage": {
            "mcp_exec": f'control_exec_server_command(server_id="{s.server_id}", command="...")',
            "mcp_upload": f'control_upload_server_file(server_id="{s.server_id}", local_path="...", remote_path="{s.default_workdir or "/opt/app"}/...")',
            "mcp_download": f'control_download_server_file(server_id="{s.server_id}", remote_path="...", local_path="...")',
            "cli_cmd": f'python3 agent-control/scripts/agent_ssh.py exec {s.server_id} "ls -la {s.default_workdir or "/opt/app"}"',
        },
    }


def _resolve_server(db: Session, server_ref: str) -> ServerCredential:
    """支持通过 server_id、数据库主键 id 或服务器 IP (host) 检索服务器凭据"""
    ref = (server_ref or "").strip()
    srv = db.query(ServerCredential).filter(ServerCredential.server_id == ref).first()
    if not srv and ref.isdigit():
        srv = db.query(ServerCredential).filter(ServerCredential.id == int(ref)).first()
    if not srv:
        srv = db.query(ServerCredential).filter(ServerCredential.host == ref).first()
    if not srv:
        raise HTTPException(status_code=404, detail=f"未找到服务器凭据配置: '{ref}'")
    return srv


# ----------------------------------------------------------------------
# 1. 全局统计指标 (Stats)
# ----------------------------------------------------------------------
@router.get("/stats")
def get_servers_stats(db: Session = Depends(get_db)):
    ensure_server_tables_initialized(db)
    total_servers = db.query(func.count(ServerCredential.id)).scalar() or 0
    active_servers = db.query(func.count(ServerCredential.id)).filter(ServerCredential.status == "active").scalar() or 0
    online_servers = db.query(func.count(ServerCredential.id)).filter(ServerCredential.last_check_status == "online").scalar() or 0
    unreachable_servers = db.query(func.count(ServerCredential.id)).filter(ServerCredential.last_check_status == "unreachable").scalar() or 0
    total_logs = db.query(func.count(ServerAccessLog.id)).scalar() or 0

    proj_rows = (
        db.query(ServerCredential.project_name, func.count(ServerCredential.id))
        .group_by(ServerCredential.project_name)
        .all()
    )
    projects_dist = [{"project_name": r[0], "count": r[1]} for r in proj_rows]

    env_rows = (
        db.query(ServerCredential.environment, func.count(ServerCredential.id))
        .group_by(ServerCredential.environment)
        .all()
    )
    environments_dist = [{"environment": r[0], "count": r[1]} for r in env_rows]

    return {
        "total_servers": total_servers,
        "active_servers": active_servers,
        "online_servers": online_servers,
        "unreachable_servers": unreachable_servers,
        "total_logs": total_logs,
        "projects_distribution": projects_dist,
        "environments_distribution": environments_dist,
    }


# ----------------------------------------------------------------------
# 2. 审计日志分页查询 (Access Logs)
# ----------------------------------------------------------------------
@router.get("/logs", response_model=PageResult[Any])
def list_server_access_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    server_id: Optional[str] = Query(None),
    project_name: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    ensure_server_tables_initialized(db)
    query = db.query(ServerAccessLog)
    if isinstance(server_id, str) and server_id.strip():
        query = query.filter(ServerAccessLog.server_id == server_id.strip())
    if isinstance(project_name, str) and project_name.strip():
        query = query.filter(ServerAccessLog.project_name == project_name.strip())
    if isinstance(action_type, str) and action_type.strip():
        query = query.filter(ServerAccessLog.action_type == action_type.strip())
    if isinstance(status, str) and status.strip():
        query = query.filter(ServerAccessLog.status == status.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                ServerAccessLog.server_id.ilike(kw),
                ServerAccessLog.host.ilike(kw),
                ServerAccessLog.operator.ilike(kw),
                ServerAccessLog.command_or_path.ilike(kw),
                ServerAccessLog.output_summary.ilike(kw),
            )
        )
    query = query.order_by(desc(ServerAccessLog.id))

    def serialize(log: ServerAccessLog):
        return {
            "id": log.id,
            "server_id": log.server_id,
            "project_name": log.project_name,
            "host": log.host,
            "action_type": log.action_type,
            "operator": log.operator,
            "command_or_path": log.command_or_path,
            "exit_code": log.exit_code,
            "status": log.status,
            "output_summary": log.output_summary,
            "duration_sec": log.duration_sec,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }

    return paginate_query(
        query,
        page if isinstance(page, int) else 1,
        page_size if isinstance(page_size, int) else 20,
        serialize,
    )


# ----------------------------------------------------------------------
# 3. 服务器凭据分页列表 (Servers List - 密码全程掩码)
# ----------------------------------------------------------------------
@router.get("", response_model=PageResult[Any])
def list_servers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_name: Optional[str] = Query(None, description="所属项目过滤"),
    environment: Optional[str] = Query(None, description="环境过滤: prod / staging / test / dev"),
    status: Optional[str] = Query(None, description="状态过滤: active / disabled"),
    last_check_status: Optional[str] = Query(None, description="连通状态过滤: online / unreachable / unknown"),
    keyword: Optional[str] = Query(None, description="搜索编号、名称、IP、账号或备注"),
    db: Session = Depends(get_db),
):
    ensure_server_tables_initialized(db)
    query = db.query(ServerCredential)
    if isinstance(project_name, str) and project_name.strip():
        query = query.filter(ServerCredential.project_name == project_name.strip())
    if isinstance(environment, str) and environment.strip():
        query = query.filter(ServerCredential.environment == environment.strip())
    if isinstance(status, str) and status.strip():
        query = query.filter(ServerCredential.status == status.strip())
    if isinstance(last_check_status, str) and last_check_status.strip():
        query = query.filter(ServerCredential.last_check_status == last_check_status.strip())
    if isinstance(keyword, str) and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                ServerCredential.server_id.ilike(kw),
                ServerCredential.name.ilike(kw),
                ServerCredential.project_name.ilike(kw),
                ServerCredential.host.ilike(kw),
                ServerCredential.username.ilike(kw),
                ServerCredential.description.ilike(kw),
            )
        )
    query = query.order_by(desc(ServerCredential.id))

    return paginate_query(
        query,
        page if isinstance(page, int) else 1,
        page_size if isinstance(page_size, int) else 20,
        _serialize_server,
    )


# ----------------------------------------------------------------------
# 4. 新增服务器凭据 (Create Server Credential)
# ----------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
def create_server(payload: ServerCreateRequest, db: Session = Depends(get_db)):
    sid = payload.server_id.strip()
    if not sid:
        raise HTTPException(status_code=400, detail="server_id 不能为空")
    existing = db.query(ServerCredential).filter(ServerCredential.server_id == sid).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"服务器标识 '{sid}' 已存在，请使用其他标识或直接编辑")

    pwd_cipher = encrypt_secret(payload.password) if payload.password else None
    key_cipher = encrypt_secret(payload.private_key) if payload.private_key else None

    srv = ServerCredential(
        server_id=sid,
        name=payload.name.strip(),
        project_name=payload.project_name.strip() or "tpm-backend-app",
        environment=payload.environment.strip() or "prod",
        host=payload.host.strip(),
        port=payload.port or 22,
        username=payload.username.strip() or "root",
        auth_type=payload.auth_type.strip() or "password",
        password_cipher=pwd_cipher,
        private_key_cipher=key_cipher,
        default_workdir=(payload.default_workdir or "/opt/app").strip(),
        tags=payload.tags or [],
        description=payload.description.strip() if payload.description else "",
        status=payload.status or "active",
        last_check_status="unknown",
        created_by=payload.created_by.strip() or "Admin",
    )
    db.add(srv)
    db.flush()

    log_entry = ServerAccessLog(
        server_id=sid,
        project_name=srv.project_name,
        host=srv.host,
        action_type="credential_update",
        operator=srv.created_by,
        command_or_path=f"注册服务器凭据 {srv.username}@{srv.host}:{srv.port}",
        exit_code=0,
        status="SUCCESS",
        output_summary="服务器登录凭据已通过 Vault 加密入库（明文已销毁）",
        duration_sec=0.0,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(srv)

    return {
        "success": True,
        "message": f"服务器 {sid} ({srv.host}) 凭据已加密保存",
        "server": _serialize_server(srv),
    }


# ----------------------------------------------------------------------
# 5. 获取单个服务器详情 (Get Server Detail)
# ----------------------------------------------------------------------
@router.get("/{server_id}")
def get_server_detail(server_id: str, db: Session = Depends(get_db)):
    srv = _resolve_server(db, server_id)
    recent_logs = (
        db.query(ServerAccessLog)
        .filter(ServerAccessLog.server_id == srv.server_id)
        .order_by(desc(ServerAccessLog.id))
        .limit(15)
        .all()
    )
    data = _serialize_server(srv)
    data["recent_logs"] = [
        {
            "id": l.id,
            "action_type": l.action_type,
            "operator": l.operator,
            "command_or_path": l.command_or_path,
            "exit_code": l.exit_code,
            "status": l.status,
            "output_summary": l.output_summary,
            "duration_sec": l.duration_sec,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in recent_logs
    ]
    return data


# ----------------------------------------------------------------------
# 6. 更新服务器凭据 (Update Server Credential - 留空保持原密文不变)
# ----------------------------------------------------------------------
@router.put("/{server_id}")
def update_server(server_id: str, payload: ServerUpdateRequest, db: Session = Depends(get_db)):
    srv = _resolve_server(db, server_id)

    if payload.name is not None:
        srv.name = payload.name.strip()
    if payload.project_name is not None:
        srv.project_name = payload.project_name.strip()
    if payload.environment is not None:
        srv.environment = payload.environment.strip()
    if payload.host is not None:
        srv.host = payload.host.strip()
    if payload.port is not None:
        srv.port = payload.port
    if payload.username is not None:
        srv.username = payload.username.strip()
    if payload.auth_type is not None:
        srv.auth_type = payload.auth_type.strip()
    if payload.default_workdir is not None:
        srv.default_workdir = payload.default_workdir.strip()
    if payload.tags is not None:
        srv.tags = payload.tags
    if payload.description is not None:
        srv.description = payload.description.strip()
    if payload.status is not None:
        srv.status = payload.status.strip()

    secret_updated = False
    if payload.password is not None and payload.password.strip() != "" and payload.password.strip() != "********":
        srv.password_cipher = encrypt_secret(payload.password)
        secret_updated = True
    if payload.private_key is not None and payload.private_key.strip() != "" and payload.private_key.strip() != "********":
        srv.private_key_cipher = encrypt_secret(payload.private_key)
        secret_updated = True

    srv.updated_at = datetime.utcnow()

    log_entry = ServerAccessLog(
        server_id=srv.server_id,
        project_name=srv.project_name,
        host=srv.host,
        action_type="credential_update",
        operator=payload.operator or "Admin",
        command_or_path=f"更新服务器配置 {srv.username}@{srv.host}:{srv.port}",
        exit_code=0,
        status="SUCCESS",
        output_summary="已更新服务器元数据" + ("并重新加密登录凭据" if secret_updated else "（保持原加密凭据不变）"),
        duration_sec=0.0,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(srv)

    return {
        "success": True,
        "message": f"服务器 {srv.server_id} 更新成功",
        "server": _serialize_server(srv),
    }


# ----------------------------------------------------------------------
# 7. 删除服务器凭据 (Delete Server Credential)
# ----------------------------------------------------------------------
@router.delete("/{server_id}")
def delete_server(server_id: str, db: Session = Depends(get_db)):
    srv = _resolve_server(db, server_id)
    sid = srv.server_id
    db.delete(srv)
    db.commit()
    return {"success": True, "message": f"服务器凭据 {sid} 已删除"}


# ----------------------------------------------------------------------
# 8. 测试服务器连通性 (Test Server Connectivity)
# ----------------------------------------------------------------------
@router.post("/{server_id}/test-connection")
def test_server_connection(
    server_id: str,
    verify_ssh_auth: bool = Query(False, description="是否同时测试 SSH 登录认证执行"),
    operator: str = Query("Dashboard", description="操作人/调用方"),
    db: Session = Depends(get_db),
):
    srv = _resolve_server(db, server_id)
    probe = test_tcp_and_ssh_banner(srv.host, srv.port, timeout=5.0)
    duration_sec = round((probe.get("latency_ms") or 0) / 1000.0, 3)

    if probe["reachable"] and verify_ssh_auth:
        auth_res = execute_remote_command(
            host=srv.host,
            port=srv.port,
            username=srv.username,
            command="echo Connected_OK && uname -sr",
            password_cipher=srv.password_cipher,
            private_key_cipher=srv.private_key_cipher,
            timeout=12,
        )
        duration_sec = auth_res["duration_sec"]
        if auth_res["success"]:
            probe["message"] = f"SSH 认证通过 ({duration_sec}s): {auth_res['output']}"
            probe["status"] = "online"
        else:
            probe["message"] = f"端口可达但 SSH 认证失败: {auth_res['output']}"
            probe["status"] = "auth_failed"

    srv.last_check_status = probe["status"]
    srv.last_check_message = (probe["message"] or "")[:500]
    srv.last_check_at = datetime.utcnow()

    log_entry = ServerAccessLog(
        server_id=srv.server_id,
        project_name=srv.project_name,
        host=srv.host,
        action_type="test_conn",
        operator=operator,
        command_or_path=f"TCP/SSH 探测 {srv.host}:{srv.port}",
        exit_code=0 if probe["reachable"] else 1,
        status="SUCCESS" if probe["reachable"] else "FAILED",
        output_summary=srv.last_check_message,
        duration_sec=duration_sec,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(srv)

    return {
        "success": probe["reachable"],
        "server_id": srv.server_id,
        "host": srv.host,
        "port": srv.port,
        "status": srv.last_check_status,
        "latency_ms": probe.get("latency_ms"),
        "message": srv.last_check_message,
        "server": _serialize_server(srv),
    }


# ----------------------------------------------------------------------
# 9. Agent 免密托管执行远程命令 (Zero-Exposure Remote Command Execution)
# ----------------------------------------------------------------------
@router.post("/{server_id}/exec")
def exec_on_server(server_id: str, payload: ServerExecRequest, db: Session = Depends(get_db)):
    srv = _resolve_server(db, server_id)
    if srv.status != "active":
        raise HTTPException(status_code=403, detail=f"服务器 {srv.server_id} 当前处于禁用状态 ({srv.status})")

    workdir = payload.workdir if payload.workdir is not None else srv.default_workdir
    res = execute_remote_command(
        host=srv.host,
        port=srv.port,
        username=srv.username,
        command=payload.command,
        password_cipher=srv.password_cipher,
        private_key_cipher=srv.private_key_cipher,
        workdir=workdir,
        timeout=payload.timeout,
    )

    if res["success"]:
        srv.last_check_status = "online"
        srv.last_check_message = f"最近命令执行成功 ({res['duration_sec']}s)"
        srv.last_check_at = datetime.utcnow()

    log_entry = ServerAccessLog(
        server_id=srv.server_id,
        project_name=srv.project_name,
        host=srv.host,
        action_type="exec_cmd",
        operator=payload.operator or "Agent",
        command_or_path=f"[{workdir or '~'}] $ {payload.command}",
        exit_code=res["exit_code"],
        status="SUCCESS" if res["success"] else "FAILED",
        output_summary=(res["output"] or "")[:2000],
        duration_sec=res["duration_sec"],
    )
    db.add(log_entry)
    db.commit()

    return {
        "success": res["success"],
        "server_id": srv.server_id,
        "host": srv.host,
        "username": srv.username,
        "workdir": workdir,
        "exit_code": res["exit_code"],
        "output": res["output"],
        "duration_sec": res["duration_sec"],
    }


# ----------------------------------------------------------------------
# 10. Agent 免密托管上传文件 (Zero-Exposure SCP File Upload)
# ----------------------------------------------------------------------
@router.post("/{server_id}/upload")
def upload_to_server(server_id: str, payload: ServerUploadRequest, db: Session = Depends(get_db)):
    srv = _resolve_server(db, server_id)
    if srv.status != "active":
        raise HTTPException(status_code=403, detail=f"服务器 {srv.server_id} 当前处于禁用状态 ({srv.status})")

    temp_file_path = None
    try:
        local_src = (payload.local_path or "").strip()
        if not local_src:
            if payload.content_base64 is not None:
                raw_bytes = base64.b64decode(payload.content_base64)
                suffix = f"_{payload.filename}" if payload.filename else ""
                fd, temp_file_path = tempfile.mkstemp(prefix="ac_upload_", suffix=suffix)
                with os.fdopen(fd, "wb") as f:
                    f.write(raw_bytes)
                local_src = temp_file_path
            elif payload.content_text is not None:
                suffix = f"_{payload.filename}" if payload.filename else ""
                fd, temp_file_path = tempfile.mkstemp(prefix="ac_upload_", suffix=suffix)
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(payload.content_text)
                local_src = temp_file_path
            else:
                raise HTTPException(status_code=400, detail="必须提供 local_path 或 content_text / content_base64")
        else:
            if not os.path.exists(local_src):
                raise HTTPException(status_code=400, detail=f"宿主机本地路径不存在: {local_src}")

        res = transfer_remote_file(
            direction="upload",
            host=srv.host,
            port=srv.port,
            username=srv.username,
            local_path=local_src,
            remote_path=payload.remote_path.strip(),
            password_cipher=srv.password_cipher,
            private_key_cipher=srv.private_key_cipher,
            recursive=payload.recursive,
            timeout=payload.timeout,
        )

        display_src = payload.local_path or payload.filename or "[inline-content]"
        log_entry = ServerAccessLog(
            server_id=srv.server_id,
            project_name=srv.project_name,
            host=srv.host,
            action_type="upload_file",
            operator=payload.operator or "Agent",
            command_or_path=f"UPLOAD {display_src} -> {payload.remote_path}",
            exit_code=res["exit_code"],
            status="SUCCESS" if res["success"] else "FAILED",
            output_summary=(res["output"] or "文件上传完成")[:2000],
            duration_sec=res["duration_sec"],
        )
        db.add(log_entry)
        db.commit()

        return {
            "success": res["success"],
            "server_id": srv.server_id,
            "host": srv.host,
            "direction": "upload",
            "local_path": display_src,
            "remote_path": payload.remote_path,
            "exit_code": res["exit_code"],
            "output": res["output"],
            "duration_sec": res["duration_sec"],
        }
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass


# ----------------------------------------------------------------------
# 11. Agent 免密托管下载文件 (Zero-Exposure SCP File Download)
# ----------------------------------------------------------------------
@router.post("/{server_id}/download")
def download_from_server(server_id: str, payload: ServerDownloadRequest, db: Session = Depends(get_db)):
    srv = _resolve_server(db, server_id)
    if srv.status != "active":
        raise HTTPException(status_code=403, detail=f"服务器 {srv.server_id} 当前处于禁用状态 ({srv.status})")

    temp_dest_path = None
    try:
        local_dst = (payload.local_path or "").strip()
        if not local_dst:
            fd, temp_dest_path = tempfile.mkstemp(prefix="ac_download_")
            os.close(fd)
            local_dst = temp_dest_path
        else:
            parent_dir = os.path.dirname(os.path.abspath(local_dst))
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

        res = transfer_remote_file(
            direction="download",
            host=srv.host,
            port=srv.port,
            username=srv.username,
            local_path=local_dst,
            remote_path=payload.remote_path.strip(),
            password_cipher=srv.password_cipher,
            private_key_cipher=srv.private_key_cipher,
            recursive=payload.recursive,
            timeout=payload.timeout,
        )

        content_preview = None
        content_base64 = None
        file_size = None
        if res["success"] and os.path.isfile(local_dst):
            file_size = os.path.getsize(local_dst)
            if payload.return_content or temp_dest_path:
                with open(local_dst, "rb") as f:
                    raw_bytes = f.read(5 * 1024 * 1024)  # 限制最多读取 5MB
                content_base64 = base64.b64encode(raw_bytes).decode("utf-8")
                try:
                    content_preview = raw_bytes.decode("utf-8")[:10000]
                except UnicodeDecodeError:
                    content_preview = f"[Binary file, {file_size} bytes]"

        log_entry = ServerAccessLog(
            server_id=srv.server_id,
            project_name=srv.project_name,
            host=srv.host,
            action_type="download_file",
            operator=payload.operator or "Agent",
            command_or_path=f"DOWNLOAD {payload.remote_path} -> {payload.local_path or '[memory-stream]'}",
            exit_code=res["exit_code"],
            status="SUCCESS" if res["success"] else "FAILED",
            output_summary=(res["output"] or f"文件下载完成 ({file_size or 0} bytes)")[:2000],
            duration_sec=res["duration_sec"],
        )
        db.add(log_entry)
        db.commit()

        result_payload = {
            "success": res["success"],
            "server_id": srv.server_id,
            "host": srv.host,
            "direction": "download",
            "remote_path": payload.remote_path,
            "local_path": payload.local_path or None,
            "file_size": file_size,
            "exit_code": res["exit_code"],
            "output": res["output"],
            "duration_sec": res["duration_sec"],
        }
        if content_preview is not None:
            result_payload["content_preview"] = content_preview
        if content_base64 is not None and (payload.return_content or not payload.local_path):
            result_payload["content_base64"] = content_base64
        return result_payload
    finally:
        if temp_dest_path and os.path.exists(temp_dest_path):
            try:
                os.remove(temp_dest_path)
            except OSError:
                pass
