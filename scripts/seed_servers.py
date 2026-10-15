import os
import sys
from datetime import datetime, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.session import Base, sync_engine, SessionLocal
from app.models.server_credential import ServerCredential, ServerAccessLog
from app.core.vault import encrypt_secret


def seed_server_credentials():
    # Ensure tables exist
    Base.metadata.create_all(bind=sync_engine, tables=[ServerCredential.__table__, ServerAccessLog.__table__])

    db = SessionLocal()
    try:
        existing_count = db.query(ServerCredential).count()
        if existing_count > 0:
            print(f"server_credentials already has {existing_count} records. Skipping destructive clear.")
            return

        now = datetime.utcnow()
        servers = [
            ServerCredential(
                server_id="SRV-TPM-LOCAL-01",
                name="本机管控与联调宿主节点 (Localhost)",
                project_name="agent-control",
                environment="dev",
                host="127.0.0.1",
                port=22,
                username="root",
                auth_type="password",
                password_cipher=encrypt_secret("Dev@Local2026#Vault"),
                default_workdir="/Users/youfanyu/Desktop/workspace/tpm",
                tags=["control-plane", "mysql-13306", "local-host"],
                description="Agent Control 控制面与本地多仓库联调宿主机，支持免密连通性探测与脚本执行。",
                status="active",
                last_check_status="online",
                last_check_message="端口连通正常 (0.8 ms) · SSH-2.0-OpenSSH",
                last_check_at=now - timedelta(minutes=5),
                created_by="SystemArch",
            ),
            ServerCredential(
                server_id="SRV-TPM-APP-PROD-01",
                name="TPM 业务后端主节点 (Spring Boot)",
                project_name="tpm-backend-app",
                environment="prod",
                host="192.168.10.101",
                port=22,
                username="deploy",
                auth_type="password",
                password_cipher=encrypt_secret("TpmProd@App#2026!"),
                default_workdir="/opt/tpm/tpm-backend-app",
                tags=["spring-boot", "jdk17", "tongweb-8080"],
                description="运行 tpm-backend-app 核心采购与预算业务服务，Agent 可通过 SRV-TPM-APP-PROD-01 免密上传 Jar 包并重启服务。",
                status="active",
                last_check_status="online",
                last_check_message="SSH 认证通过 (0.12s): Connected_OK Linux 5.15.0",
                last_check_at=now - timedelta(minutes=18),
                created_by="DevOpsLead",
            ),
            ServerCredential(
                server_id="SRV-TPM-WEB-PROD-01",
                name="TPM 前端静态资源与网关节点 (Nginx)",
                project_name="tpm-frontend-web",
                environment="prod",
                host="192.168.10.102",
                port=22,
                username="nginx_adm",
                auth_type="password",
                password_cipher=encrypt_secret("TpmWeb@Nginx#2026!"),
                default_workdir="/usr/share/nginx/html/tpm",
                tags=["vue3", "nginx", "reverse-proxy"],
                description="承载 tpm-frontend-web 前端打包产物 dist 目录与反向代理配置，支持 Agent 免密同步静态文件。",
                status="active",
                last_check_status="online",
                last_check_message="端口连通正常 (1.4 ms) · SSH-2.0-OpenSSH_8.9",
                last_check_at=now - timedelta(minutes=25),
                created_by="FrontendLead",
            ),
            ServerCredential(
                server_id="SRV-TPM-FILE-PROD-01",
                name="TPM 文件存储与附件服务节点",
                project_name="tpm-backend-file",
                environment="prod",
                host="192.168.10.103",
                port=22,
                username="file_svc",
                auth_type="password",
                password_cipher=encrypt_secret("TpmFile@Minio#2026!"),
                default_workdir="/data/tpm-file-service",
                tags=["file-service", "minio", "storage"],
                description="负责招投标附件、合同归档文件与证明材料存储服务。",
                status="active",
                last_check_status="online",
                last_check_message="端口连通正常 (1.9 ms) · SSH-2.0-OpenSSH_8.9",
                last_check_at=now - timedelta(minutes=40),
                created_by="StorageAdmin",
            ),
            ServerCredential(
                server_id="SRV-PROOFREAD-STAGE-01",
                name="智能校对服务预发测试节点",
                project_name="tpm-proofread-service",
                environment="staging",
                host="192.168.20.55",
                port=22022,
                username="ubuntu",
                auth_type="password",
                password_cipher=encrypt_secret("Proofread@Stage#2026!"),
                default_workdir="/opt/tpm-proofread-service",
                tags=["proofread", "nlp", "docker"],
                description="预发布环境公文与合同智能校对微服务节点（非标 SSH 端口 22022）。",
                status="active",
                last_check_status="online",
                last_check_message="SSH 认证通过 (0.21s): Connected_OK Linux 6.1.0",
                last_check_at=now - timedelta(hours=1),
                created_by="AI-Engineer",
            ),
        ]

        for s in servers:
            db.add(s)
        db.flush()

        logs = [
            ServerAccessLog(
                server_id="SRV-TPM-APP-PROD-01",
                project_name="tpm-backend-app",
                host="192.168.10.101",
                action_type="exec_cmd",
                operator="MCP-Agent",
                command_or_path="[/opt/tpm/tpm-backend-app] $ ps -ef | grep tpm-backend-app",
                exit_code=0,
                status="SUCCESS",
                output_summary="deploy 14820 1 2 10:00 ? 00:04:12 java -jar tpm-backend-app.jar --spring.profiles.active=prod",
                duration_sec=0.18,
                created_at=now - timedelta(minutes=30),
            ),
            ServerAccessLog(
                server_id="SRV-TPM-WEB-PROD-01",
                project_name="tpm-frontend-web",
                host="192.168.10.102",
                action_type="upload_file",
                operator="MCP-Agent",
                command_or_path="UPLOAD /workspace/tpm-frontend-web/dist.tar.gz -> /usr/share/nginx/html/tpm/dist.tar.gz",
                exit_code=0,
                status="SUCCESS",
                output_summary="文件上传完成 (4.2 MB, 耗时 0.64s，凭据已通过 Vault PTY 免密注入)",
                duration_sec=0.64,
                created_at=now - timedelta(minutes=22),
            ),
            ServerAccessLog(
                server_id="SRV-PROOFREAD-STAGE-01",
                project_name="tpm-proofread-service",
                host="192.168.20.55",
                action_type="download_file",
                operator="SDK-Client",
                command_or_path="DOWNLOAD /opt/tpm-proofread-service/proofread.log -> ./logs/stage_proofread.log",
                exit_code=0,
                status="SUCCESS",
                output_summary="文件下载完成 (147280 bytes，输出流已完成敏感词脱敏校验)",
                duration_sec=0.31,
                created_at=now - timedelta(minutes=12),
            ),
        ]
        for l in logs:
            db.add(l)

        db.commit()
        print(f"Successfully seeded {len(servers)} server credentials and {len(logs)} audit logs.")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_server_credentials()
