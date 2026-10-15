from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Integer, Float
from db.session import Base


class ServerCredential(Base):
    """
    项目服务器登录凭据与资产表：
    密码与私钥仅存储加密密文 (password_cipher / private_key_cipher)，
    向前端及 Agent 暴露唯一句柄 server_id，实现免密托管命令执行与文件传输。
    """
    __tablename__ = "server_credentials"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    server_id = Column(String(64), unique=True, nullable=False, index=True)  # 如 SRV-TPM-PROD-01
    name = Column(String(128), nullable=False)                               # 服务器名称，如 生产环境应用主机
    project_name = Column(String(128), nullable=False, default="tpm-backend-app", index=True)
    environment = Column(String(32), nullable=False, default="prod", index=True)  # prod, staging, test, dev
    host = Column(String(128), nullable=False, index=True)                   # IP 或域名
    port = Column(Integer, nullable=False, default=22)                       # SSH 端口
    username = Column(String(64), nullable=False, default="root")            # 登录账号
    auth_type = Column(String(32), nullable=False, default="password")       # password / ssh_key
    password_cipher = Column(Text, nullable=True)                            # Fernet/AES 加密后的密码密文
    private_key_cipher = Column(Text, nullable=True)                         # Fernet/AES 加密后的 SSH 私钥密文
    default_workdir = Column(String(256), nullable=True, default="/opt/app") # 默认工作路径
    tags = Column(JSON, nullable=True)                                       # 用途标签列表，如 ["docker", "nginx", "java"]
    description = Column(Text, nullable=True)                                # 服务器用途说明与 Agent 操作指引
    status = Column(String(32), nullable=False, default="active", index=True)# active / disabled
    last_check_status = Column(String(32), nullable=False, default="unknown")# online / unreachable / unknown
    last_check_message = Column(String(512), nullable=True)
    last_check_at = Column(DateTime, nullable=True)
    created_by = Column(String(64), nullable=False, default="Admin")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ServerAccessLog(Base):
    """
    服务器访问与 Agent 托管操作审计日志表：
    记录所有连通性测试、远程命令执行 (exec)、文件上传 (upload) 与下载 (download) 行为，输出均脱敏。
    """
    __tablename__ = "server_access_logs"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    server_id = Column(String(64), nullable=False, index=True)
    project_name = Column(String(128), nullable=False, default="tpm-backend-app", index=True)
    host = Column(String(128), nullable=False)
    action_type = Column(String(32), nullable=False, index=True)  # test_conn / exec_cmd / upload_file / download_file / credential_update
    operator = Column(String(64), nullable=False, default="Agent") # MCP-Agent / SDK / Dashboard-Admin
    command_or_path = Column(Text, nullable=True)                 # 执行的命令或上传下载路径摘要
    exit_code = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="SUCCESS", index=True)  # SUCCESS / FAILED
    output_summary = Column(Text, nullable=True)                  # 脱敏后的执行输出摘要
    duration_sec = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
