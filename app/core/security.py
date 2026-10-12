import hashlib
import time
import os
import secrets
from datetime import datetime
from typing import Optional, Any

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session

from db.session import get_db
from app.core.config import settings
from app.models.agent import ApiClient

# Crockford Base32 characters for ULID
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# FastAPI 鉴权机制：支持标准 Authorization: Bearer <token> 与 X-API-Key: <token>
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

def generate_ulid(prefix: str = "") -> str:
    """Generate a sortable ULID string with an optional entity prefix (e.g. TASK_01...)"""
    timestamp_ms = int(time.time() * 1000)
    # 48 bits of timestamp
    time_chars = []
    t = timestamp_ms
    for _ in range(10):
        time_chars.append(CROCKFORD_BASE32[t % 32])
        t //= 32
    time_part = "".join(reversed(time_chars))

    # 80 bits of randomness
    random_bytes = os.urandom(10)
    rand_int = int.from_bytes(random_bytes, byteorder="big")
    rand_chars = []
    for _ in range(16):
        rand_chars.append(CROCKFORD_BASE32[rand_int % 32])
        rand_int //= 32
    rand_part = "".join(reversed(rand_chars))

    ulid_str = time_part + rand_part
    if prefix:
        return f"{prefix}_{ulid_str}"
    return ulid_str

def hash_token(token: str) -> str:
    """Hash API client token using SHA-256"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_token() -> tuple[str, str]:
    """Generate a secure bearer token and return (raw_token, sha256_hash)"""
    token = "ac_" + secrets.token_urlsafe(32)
    return token, hash_token(token)

def verify_token(raw_token: str, db: Session) -> Optional[Any]:
    """
    验证客户端提供的原始 Token：
    1. 优先校验主控 API 密钥（Master Key，支持时间常数比对防时序攻击）
    2. 校验数据库 api_clients 表中的哈希匹配项并更新 last_used_at
    """
    if not raw_token or not raw_token.strip():
        return None

    raw_token = raw_token.strip()

    # 1. 匹配 Master API Key
    effective_master_key = settings.effective_api_key
    if effective_master_key and secrets.compare_digest(raw_token, effective_master_key):
        return {
            "id": 0,
            "public_id": "CLIENT_MASTER",
            "name": "Master Admin",
            "scopes": ["*"],
            "is_master": True
        }

    # 2. 匹配数据库 ApiClient
    token_h = hash_token(raw_token)
    client = db.query(ApiClient).filter(ApiClient.token_hash == token_h).first()
    if client:
        try:
            client.last_used_at = datetime.utcnow()
            db.commit()
        except Exception:
            db.rollback()
        return client

    return None

def get_current_client(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    x_api_key: Optional[str] = Security(api_key_header_scheme),
    db: Session = Depends(get_db)
) -> Any:
    """
    FastAPI 全局与路由级身份认证依赖项 (CWE-306 核心防御)：
    提取请求凭证并验证，未通过鉴权立即抛出 401 Unauthorized。
    """
    if not settings.REQUIRE_AUTH:
        return {
            "id": 0,
            "public_id": "CLIENT_ANONYMOUS",
            "name": "Anonymous",
            "scopes": ["*"],
            "is_master": True
        }

    raw_token = None
    if credentials and credentials.scheme.lower() == "bearer":
        raw_token = credentials.credentials
    elif x_api_key:
        raw_token = x_api_key

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide 'Authorization: Bearer <token>' or 'X-API-Key' header.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    client = verify_token(raw_token, db)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return client

def require_scopes(*required_scopes: str):
    """权限范围 (Scopes) 校验依赖工厂"""
    def _check_scope(client: Any = Depends(get_current_client)):
        if getattr(client, "is_master", False) or (isinstance(client, dict) and client.get("is_master")):
            return client
        scopes = client.get("scopes", []) if isinstance(client, dict) else (client.scopes or [])
        if "*" in scopes:
            return client
        for req in required_scopes:
            if req not in scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Forbidden: Client lacks required scope '{req}'"
                )
        return client
    return _check_scope

