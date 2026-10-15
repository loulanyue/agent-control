#!/usr/bin/env python3
"""
Agent 免密服务器操作 CLI 工具 (agent_ssh.py)
================================================
供 AI Agent 或开发者通过 `server_id`（或 IP）直接免密执行远程命令、上传文件、下载文件，
密码全程由 Agent Control Vault 加密托管并在后台 PTY 内存态注入，绝不暴露在终端、日志或 Prompt 中。

用法示例:
  1. 列出所有可用服务器:
     python3 agent-control/scripts/agent_ssh.py list
  2. 测试服务器连通性:
     python3 agent-control/scripts/agent_ssh.py test SRV-TPM-APP-PROD-01
  3. 免密执行远程命令:
     python3 agent-control/scripts/agent_ssh.py exec SRV-TPM-APP-PROD-01 "ps -ef | grep java"
  4. 免密上传本地文件/目录到服务器:
     python3 agent-control/scripts/agent_ssh.py upload SRV-TPM-APP-PROD-01 ./target/app.jar /opt/tpm/app.jar
  5. 免密从服务器下载文件/目录到本地:
     python3 agent-control/scripts/agent_ssh.py download SRV-TPM-APP-PROD-01 /opt/tpm/logs/app.log ./app.log
"""

import argparse
import glob
import json
import os
import sys

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _sp in glob.glob(os.path.join(_BASE_DIR, "venv", "lib", "python*", "site-packages")):
    if _sp not in sys.path and os.path.isdir(_sp):
        sys.path.insert(0, _sp)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from agent_control_sdk.client import AgentControlClient
from app.core.config import settings


def get_sdk_client(base_url: str, api_key: str) -> AgentControlClient:
    key = api_key or settings.API_KEY or os.getenv("AGENT_CONTROL_API_KEY") or ""
    return AgentControlClient(base_url=base_url, api_key=key, timeout=120)


def main():
    parser = argparse.ArgumentParser(description="Agent Control 免密服务器命令执行与文件传输工具")
    parser.add_argument("--url", default=os.getenv("AGENT_CONTROL_URL", "http://127.0.0.1:8000"), help="Agent Control API 地址")
    parser.add_argument("--api-key", default=os.getenv("AGENT_CONTROL_API_KEY", ""), help="API Key")

    subparsers = parser.add_subparsers(dest="action", required=True)

    # list
    p_list = subparsers.add_parser("list", help="列出纳管的服务器清单（不含密码）")
    p_list.add_argument("--project", default=None, help="按项目名称筛选")
    p_list.add_argument("--env", default=None, help="按环境筛选 (prod/staging/test/dev)")

    # test
    p_test = subparsers.add_parser("test", help="测试服务器连通性")
    p_test.add_argument("server_id", help="服务器唯一标识 (如 SRV-TPM-APP-PROD-01) 或 IP")
    p_test.add_argument("--auth", action="store_true", help="同时验证 SSH 认证登录")

    # exec
    p_exec = subparsers.add_parser("exec", help="按 server_id 免密执行远程 Shell 命令")
    p_exec.add_argument("server_id", help="服务器唯一标识或 IP")
    p_exec.add_argument("command", help="待执行的远程命令")
    p_exec.add_argument("--workdir", default=None, help="远程工作目录（默认使用服务器配置的 default_workdir）")
    p_exec.add_argument("--timeout", type=int, default=60, help="超时时间(秒)")

    # upload
    p_up = subparsers.add_parser("upload", help="按 server_id 免密上传文件或目录到远程服务器")
    p_up.add_argument("server_id", help="服务器唯一标识或 IP")
    p_up.add_argument("local_path", help="本地源文件路径")
    p_up.add_argument("remote_path", help="远程目标路径")
    p_up.add_argument("-r", "--recursive", action="store_true", help="递归上传目录")
    p_up.add_argument("--timeout", type=int, default=120, help="超时时间(秒)")

    # download
    p_down = subparsers.add_parser("download", help="按 server_id 免密从远程服务器下载文件或目录到本地")
    p_down.add_argument("server_id", help="服务器唯一标识或 IP")
    p_down.add_argument("remote_path", help="远程源文件路径")
    p_down.add_argument("local_path", help="本地保存目标路径")
    p_down.add_argument("-r", "--recursive", action="store_true", help="递归下载目录")
    p_down.add_argument("--timeout", type=int, default=120, help="超时时间(秒)")

    args = parser.parse_args()
    client = get_sdk_client(args.url, args.api_key)

    if args.action == "list":
        res = client.servers.list(project_name=args.project, environment=args.env, page_size=100)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.action == "test":
        res = client.servers.test_connection(args.server_id, verify_ssh_auth=args.auth)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("success") else 1)
    elif args.action == "exec":
        res = client.servers.exec(
            server_id=args.server_id,
            command=args.command,
            workdir=args.workdir,
            timeout=args.timeout,
            operator="CLI-Agent",
        )
        if res.get("output"):
            print(res["output"])
        sys.exit(res.get("exit_code", 0 if res.get("success") else 1))
    elif args.action == "upload":
        res = client.servers.upload(
            server_id=args.server_id,
            local_path=os.path.abspath(args.local_path),
            remote_path=args.remote_path,
            recursive=args.recursive,
            timeout=args.timeout,
            operator="CLI-Agent",
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("success") else 1)
    elif args.action == "download":
        res = client.servers.download(
            server_id=args.server_id,
            remote_path=args.remote_path,
            local_path=os.path.abspath(args.local_path),
            recursive=args.recursive,
            timeout=args.timeout,
            operator="CLI-Agent",
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("success") else 1)


if __name__ == "__main__":
    main()
