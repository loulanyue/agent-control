#!/usr/bin/env python3
"""
Agent Control MCP Server (Stdio JSON-RPC 2.0 / Model Context Protocol)
Exposes tools for Agent Control Plane orchestration, DAG inspection, task dispatching,
server credential vault execution (SSH/SCP without exposing passwords), and database inspection.

Tools:
  - control_list_agents: List all registered AI agents with status, capabilities, and last heartbeat.
  - control_list_tasks: Query task queue by status, priority, and keyword.
  - control_dispatch_task: Dispatch/create a new autonomous task into the control plane queue.
  - control_get_task_status: Get detailed task execution status, attempts, and artifacts.
  - control_list_graphs: List DAG workflows and orchestration pipelines.
  - control_get_system_metrics: Retrieve cluster metrics (agents, active tasks, DAG runs, DB status).
  - control_list_servers: List managed project servers (server_id, project, host, port, username, workdir; password masked).
  - control_exec_server_command: Execute a remote shell command on a server by server_id without exposing credentials.
  - control_upload_server_file: Upload a local file/directory to a remote server by server_id without exposing credentials.
  - control_download_server_file: Download a remote file/directory from a server by server_id without exposing credentials.
  - mysql_read_query: Execute SELECT/SHOW/DESCRIBE queries against the agent_control database (vault ciphertexts masked).
  - mysql_list_tables: List all tables available in the agent_control database.
  - mysql_describe_table: Inspect schema definitions of any table.
  - mysql_execute_statement: Execute INSERT/UPDATE/DELETE DML statements.
"""

import sys
import os
import glob
import json
import time
import decimal
import datetime
import traceback

# Ensure local venv site-packages and project root are on sys.path
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for _sp in glob.glob(os.path.join(_BASE_DIR, "venv", "lib", "python*", "site-packages")):
    if _sp not in sys.path and os.path.isdir(_sp):
        sys.path.insert(0, _sp)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

import pymysql
from app.core.vault import execute_remote_command, transfer_remote_file

# Database connection config
DB_HOST = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", "13306"))
DB_USER = os.getenv("MYSQL_USER") or os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DATABASE") or os.getenv("DB_NAME", "agent_control")

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    raise TypeError(f"Type {type(obj)} not serializable")

def generate_public_id(prefix: str) -> str:
    timestamp_ms = int(time.time() * 1000)
    rand_hex = os.urandom(3).hex().upper()
    return f"{prefix}_{timestamp_ms}_{rand_hex}"

def _lookup_server_row(cursor, server_id_or_host: str):
    ref = (server_id_or_host or "").strip()
    cursor.execute(
        "SELECT * FROM server_credentials WHERE server_id = %s OR host = %s LIMIT 1",
        (ref, ref)
    )
    row = cursor.fetchone()
    if not row and ref.isdigit():
        cursor.execute("SELECT * FROM server_credentials WHERE id = %s LIMIT 1", (int(ref),))
        row = cursor.fetchone()
    return row

TOOLS = [
    {
        "name": "control_list_agents",
        "description": "List registered AI agents in the control plane with status, capabilities, and last heartbeat timestamp.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Optional filter by agent status (e.g., 'online', 'offline', 'busy')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of agents to return (default 20)",
                    "default": 20
                }
            }
        }
    },
    {
        "name": "control_list_tasks",
        "description": "Query the agent control task queue by status, priority, or search keyword.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by task status ('pending', 'claimed', 'running', 'completed', 'failed')"
                },
                "priority": {
                    "type": "string",
                    "description": "Filter by priority ('critical', 'high', 'normal', 'low')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tasks to return (default 20)",
                    "default": 20
                }
            }
        }
    },
    {
        "name": "control_dispatch_task",
        "description": "Dispatch a new task to the Agent Control Plane queue for autonomous agent execution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title or short description of the task"
                },
                "objective": {
                    "type": "string",
                    "description": "Detailed goal or execution objective of the task"
                },
                "priority": {
                    "type": "string",
                    "description": "Priority level ('critical', 'high', 'normal', 'low'). Default: 'normal'",
                    "default": "normal"
                },
                "source_type": {
                    "type": "string",
                    "description": "Source identifier (e.g., 'mcp', 'user', 'dag')",
                    "default": "mcp"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "control_get_task_status",
        "description": "Retrieve comprehensive status, execution logs, attempts, and artifacts of a specific task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "Internal ID or public ID of the task"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "control_list_graphs",
        "description": "List DAG workflow definitions and active pipelines configured in the Agent Control Plane.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of graphs to return (default 20)",
                    "default": 20
                }
            }
        }
    },
    {
        "name": "control_get_system_metrics",
        "description": "Retrieve real-time metrics of the Agent Control Plane (total agents, active jobs, workflow runs, database health).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "control_list_servers",
        "description": "List managed project servers in the Server Vault (returns server_id, name, project_name, environment, host, port, username, default_workdir, description; passwords are never exposed).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Optional filter by project name (e.g., 'tpm-backend-app', 'tpm-frontend-web')"
                },
                "environment": {
                    "type": "string",
                    "description": "Optional filter by environment ('prod', 'staging', 'test', 'dev')"
                },
                "keyword": {
                    "type": "string",
                    "description": "Optional keyword matching server_id, name, host, or description"
                }
            }
        }
    },
    {
        "name": "control_exec_server_command",
        "description": "Execute a shell command on a remote server using its server_id (or host IP) via the encrypted Server Vault without exposing the password.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "string",
                    "description": "The server_id (e.g., 'SRV-TPM-APP-PROD-01') or IP address of the target server"
                },
                "command": {
                    "type": "string",
                    "description": "The shell command to execute on the remote server"
                },
                "workdir": {
                    "type": "string",
                    "description": "Optional working directory on the remote server (defaults to server's default_workdir)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default 60)",
                    "default": 60
                }
            },
            "required": ["server_id", "command"]
        }
    },
    {
        "name": "control_upload_server_file",
        "description": "Upload a local file or directory to a remote server by server_id via SCP using the encrypted Server Vault without exposing the password.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "string",
                    "description": "The server_id (e.g., 'SRV-TPM-APP-PROD-01') or IP address of the target server"
                },
                "local_path": {
                    "type": "string",
                    "description": "Absolute or relative local file/directory path on the host machine"
                },
                "remote_path": {
                    "type": "string",
                    "description": "Target path on the remote server (e.g., '/opt/tpm/app.jar')"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Set to true when uploading a directory recursively",
                    "default": False
                },
                "timeout": {
                    "type": "integer",
                    "description": "Transfer timeout in seconds (default 120)",
                    "default": 120
                }
            },
            "required": ["server_id", "local_path", "remote_path"]
        }
    },
    {
        "name": "control_download_server_file",
        "description": "Download a file or directory from a remote server to a local path by server_id via SCP using the encrypted Server Vault without exposing the password.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "string",
                    "description": "The server_id (e.g., 'SRV-TPM-APP-PROD-01') or IP address of the target server"
                },
                "remote_path": {
                    "type": "string",
                    "description": "Source file/directory path on the remote server"
                },
                "local_path": {
                    "type": "string",
                    "description": "Destination path on the local host machine"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Set to true when downloading a directory recursively",
                    "default": False
                },
                "timeout": {
                    "type": "integer",
                    "description": "Transfer timeout in seconds (default 120)",
                    "default": 120
                }
            },
            "required": ["server_id", "remote_path", "local_path"]
        }
    },
    {
        "name": "mysql_read_query",
        "description": "Execute a SELECT / SHOW / DESC query against the agent_control MySQL database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL SELECT statement to execute"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "mysql_list_tables",
        "description": "List all tables available in the agent_control MySQL database.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "mysql_describe_table",
        "description": "Show column names, data types, keys, and definitions for a table in agent_control.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "The name of the table to describe"
                }
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "mysql_execute_statement",
        "description": "Execute an INSERT, UPDATE, or DELETE SQL statement on the agent_control database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "statement": {
                    "type": "string",
                    "description": "The SQL DML statement to execute"
                }
            },
            "required": ["statement"]
        }
    }
]

def handle_call_tool(params):
    name = params.get("name")
    arguments = params.get("arguments", {})

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. control_list_agents
            if name == "control_list_agents":
                status = arguments.get("status")
                limit = min(int(arguments.get("limit", 20)), 100)
                sql = "SELECT id, public_id, name, agent_type, status, capabilities, last_seen_at, created_at FROM agents"
                conds = []
                args = []
                if status:
                    conds.append("status = %s")
                    args.append(status)
                if conds:
                    sql += " WHERE " + " AND ".join(conds)
                sql += " ORDER BY id DESC LIMIT %s"
                args.append(limit)
                cursor.execute(sql, args)
                rows = cursor.fetchall()
                return {"content": [{"type": "text", "text": json.dumps({"total": len(rows), "agents": rows}, default=json_serial, ensure_ascii=False, indent=2)}]}

            # 2. control_list_tasks
            elif name == "control_list_tasks":
                status = arguments.get("status")
                priority = arguments.get("priority")
                limit = min(int(arguments.get("limit", 20)), 100)
                sql = "SELECT id, public_id, title, objective, priority, status, source_type, claimed_by, attempt_count, created_at, updated_at FROM tasks WHERE deleted_at IS NULL"
                conds = []
                args = []
                if status:
                    conds.append("status = %s")
                    args.append(status)
                if priority:
                    conds.append("priority = %s")
                    args.append(priority)
                if conds:
                    sql += " AND " + " AND ".join(conds)
                sql += " ORDER BY id DESC LIMIT %s"
                args.append(limit)
                cursor.execute(sql, args)
                rows = cursor.fetchall()
                return {"content": [{"type": "text", "text": json.dumps({"total": len(rows), "tasks": rows}, default=json_serial, ensure_ascii=False, indent=2)}]}

            # 3. control_dispatch_task
            elif name == "control_dispatch_task":
                title = arguments.get("title", "").strip()
                objective = arguments.get("objective", "")
                priority = arguments.get("priority", "normal")
                source_type = arguments.get("source_type", "mcp")
                pub_id = generate_public_id("TASK")
                sql = """
                    INSERT INTO tasks (public_id, title, objective, priority, status, source_type, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, 'pending', %s, NOW(), NOW())
                """
                cursor.execute(sql, (pub_id, title, objective, priority, source_type))
                new_id = cursor.lastrowid
                task_info = {
                    "id": new_id,
                    "public_id": pub_id,
                    "title": title,
                    "objective": objective,
                    "priority": priority,
                    "status": "pending",
                    "source_type": source_type,
                    "message": "Task dispatched successfully to agent-control queue."
                }
                return {"content": [{"type": "text", "text": json.dumps(task_info, default=json_serial, ensure_ascii=False, indent=2)}]}

            # 4. control_get_task_status
            elif name == "control_get_task_status":
                task_id = arguments.get("task_id")
                cursor.execute("SELECT * FROM tasks WHERE id = %s OR public_id = %s", (task_id, str(task_id)))
                task = cursor.fetchone()
                if not task:
                    return {"isError": True, "content": [{"type": "text", "text": f"Task not found: {task_id}"}]}
                cursor.execute("SELECT * FROM task_attempts WHERE task_id = %s ORDER BY id DESC", (task["id"],))
                attempts = cursor.fetchall()
                cursor.execute("SELECT * FROM task_artifacts WHERE task_id = %s ORDER BY id DESC", (task["id"],))
                artifacts = cursor.fetchall()
                data = {
                    "task": task,
                    "attempts": attempts,
                    "artifacts": artifacts
                }
                return {"content": [{"type": "text", "text": json.dumps(data, default=json_serial, ensure_ascii=False, indent=2)}]}

            # 5. control_list_graphs
            elif name == "control_list_graphs":
                limit = min(int(arguments.get("limit", 20)), 100)
                cursor.execute("SELECT id, public_id, name, description, tags, status, created_by, created_at FROM graph_definitions WHERE deleted_at IS NULL ORDER BY id DESC LIMIT %s", (limit,))
                graphs = cursor.fetchall()
                return {"content": [{"type": "text", "text": json.dumps({"total": len(graphs), "graphs": graphs}, default=json_serial, ensure_ascii=False, indent=2)}]}

            # 6. control_get_system_metrics
            elif name == "control_get_system_metrics":
                cursor.execute("SELECT COUNT(*) AS c FROM agents")
                total_agents = cursor.fetchone()["c"]
                cursor.execute("SELECT COUNT(*) AS c FROM agents WHERE status = 'online'")
                online_agents = cursor.fetchone()["c"]
                cursor.execute("SELECT COUNT(*) AS c FROM tasks WHERE deleted_at IS NULL")
                total_tasks = cursor.fetchone()["c"]
                cursor.execute("SELECT COUNT(*) AS c FROM tasks WHERE status = 'pending' AND deleted_at IS NULL")
                pending_tasks = cursor.fetchone()["c"]
                cursor.execute("SELECT COUNT(*) AS c FROM tasks WHERE status = 'completed' AND deleted_at IS NULL")
                completed_tasks = cursor.fetchone()["c"]
                cursor.execute("SELECT COUNT(*) AS c FROM graph_definitions WHERE deleted_at IS NULL")
                total_graphs = cursor.fetchone()["c"]
                cursor.execute("SELECT COUNT(*) AS c FROM graph_runs")
                total_runs = cursor.fetchone()["c"]
                metrics = {
                    "status": "operational",
                    "agents": {"total": total_agents, "online": online_agents},
                    "tasks": {"total": total_tasks, "pending": pending_tasks, "completed": completed_tasks},
                    "workflows": {"total_definitions": total_graphs, "total_runs": total_runs},
                    "database": {"connected": True, "host": DB_HOST, "port": DB_PORT, "name": DB_NAME}
                }
                return {"content": [{"type": "text", "text": json.dumps(metrics, ensure_ascii=False, indent=2)}]}

            # 6.1 control_list_servers
            elif name == "control_list_servers":
                project_name = arguments.get("project_name")
                environment = arguments.get("environment")
                keyword = arguments.get("keyword")
                sql = """
                    SELECT id, server_id, name, project_name, environment, host, port,
                           username, auth_type, default_workdir, tags, description,
                           status, last_check_status, last_check_message, last_check_at
                    FROM server_credentials
                """
                conds = []
                args = []
                if project_name:
                    conds.append("project_name = %s")
                    args.append(project_name)
                if environment:
                    conds.append("environment = %s")
                    args.append(environment)
                if keyword:
                    kw = f"%{keyword}%"
                    conds.append("(server_id LIKE %s OR name LIKE %s OR host LIKE %s OR description LIKE %s)")
                    args.extend([kw, kw, kw, kw])
                if conds:
                    sql += " WHERE " + " AND ".join(conds)
                sql += " ORDER BY id DESC"
                cursor.execute(sql, args)
                rows = cursor.fetchall()
                for r in rows:
                    r["password_masked"] = "********"
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({"total": len(rows), "servers": rows}, default=json_serial, ensure_ascii=False, indent=2)
                    }]
                }

            # 6.2 control_exec_server_command
            elif name == "control_exec_server_command":
                server_ref = arguments.get("server_id", "")
                command = arguments.get("command", "")
                workdir = arguments.get("workdir")
                timeout = int(arguments.get("timeout", 60))

                srv = _lookup_server_row(cursor, server_ref)
                if not srv:
                    return {"isError": True, "content": [{"type": "text", "text": f"Server credential not found: {server_ref}"}]}
                if srv.get("status") != "active":
                    return {"isError": True, "content": [{"type": "text", "text": f"Server {srv['server_id']} is disabled."}]}

                effective_wd = workdir if workdir is not None else srv.get("default_workdir")
                res = execute_remote_command(
                    host=srv["host"],
                    port=int(srv.get("port") or 22),
                    username=srv["username"],
                    command=command,
                    password_cipher=srv.get("password_cipher"),
                    private_key_cipher=srv.get("private_key_cipher"),
                    workdir=effective_wd,
                    timeout=timeout
                )
                cursor.execute(
                    """
                    INSERT INTO server_access_logs
                    (server_id, project_name, host, action_type, operator, command_or_path, exit_code, status, output_summary, duration_sec, created_at)
                    VALUES (%s, %s, %s, 'exec_cmd', 'MCP-Agent', %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        srv["server_id"],
                        srv["project_name"],
                        srv["host"],
                        f"[{effective_wd or '~'}] $ {command}",
                        res["exit_code"],
                        "SUCCESS" if res["success"] else "FAILED",
                        (res["output"] or "")[:2000],
                        res["duration_sec"]
                    )
                )
                return {
                    "isError": not res["success"],
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "server_id": srv["server_id"],
                            "host": srv["host"],
                            "workdir": effective_wd,
                            **res
                        }, ensure_ascii=False, indent=2)
                    }]
                }

            # 6.3 control_upload_server_file
            elif name == "control_upload_server_file":
                server_ref = arguments.get("server_id", "")
                local_path = arguments.get("local_path", "")
                remote_path = arguments.get("remote_path", "")
                recursive = bool(arguments.get("recursive", False))
                timeout = int(arguments.get("timeout", 120))

                srv = _lookup_server_row(cursor, server_ref)
                if not srv:
                    return {"isError": True, "content": [{"type": "text", "text": f"Server credential not found: {server_ref}"}]}
                if not os.path.exists(local_path):
                    return {"isError": True, "content": [{"type": "text", "text": f"Local path does not exist: {local_path}"}]}

                res = transfer_remote_file(
                    direction="upload",
                    host=srv["host"],
                    port=int(srv.get("port") or 22),
                    username=srv["username"],
                    local_path=local_path,
                    remote_path=remote_path,
                    password_cipher=srv.get("password_cipher"),
                    private_key_cipher=srv.get("private_key_cipher"),
                    recursive=recursive,
                    timeout=timeout
                )
                cursor.execute(
                    """
                    INSERT INTO server_access_logs
                    (server_id, project_name, host, action_type, operator, command_or_path, exit_code, status, output_summary, duration_sec, created_at)
                    VALUES (%s, %s, %s, 'upload_file', 'MCP-Agent', %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        srv["server_id"],
                        srv["project_name"],
                        srv["host"],
                        f"UPLOAD {local_path} -> {remote_path}",
                        res["exit_code"],
                        "SUCCESS" if res["success"] else "FAILED",
                        (res["output"] or "Upload completed")[:2000],
                        res["duration_sec"]
                    )
                )
                return {
                    "isError": not res["success"],
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "server_id": srv["server_id"],
                            "host": srv["host"],
                            **res
                        }, ensure_ascii=False, indent=2)
                    }]
                }

            # 6.4 control_download_server_file
            elif name == "control_download_server_file":
                server_ref = arguments.get("server_id", "")
                remote_path = arguments.get("remote_path", "")
                local_path = arguments.get("local_path", "")
                recursive = bool(arguments.get("recursive", False))
                timeout = int(arguments.get("timeout", 120))

                srv = _lookup_server_row(cursor, server_ref)
                if not srv:
                    return {"isError": True, "content": [{"type": "text", "text": f"Server credential not found: {server_ref}"}]}

                parent_dir = os.path.dirname(os.path.abspath(local_path))
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                res = transfer_remote_file(
                    direction="download",
                    host=srv["host"],
                    port=int(srv.get("port") or 22),
                    username=srv["username"],
                    local_path=local_path,
                    remote_path=remote_path,
                    password_cipher=srv.get("password_cipher"),
                    private_key_cipher=srv.get("private_key_cipher"),
                    recursive=recursive,
                    timeout=timeout
                )
                cursor.execute(
                    """
                    INSERT INTO server_access_logs
                    (server_id, project_name, host, action_type, operator, command_or_path, exit_code, status, output_summary, duration_sec, created_at)
                    VALUES (%s, %s, %s, 'download_file', 'MCP-Agent', %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        srv["server_id"],
                        srv["project_name"],
                        srv["host"],
                        f"DOWNLOAD {remote_path} -> {local_path}",
                        res["exit_code"],
                        "SUCCESS" if res["success"] else "FAILED",
                        (res["output"] or "Download completed")[:2000],
                        res["duration_sec"]
                    )
                )
                return {
                    "isError": not res["success"],
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "server_id": srv["server_id"],
                            "host": srv["host"],
                            **res
                        }, ensure_ascii=False, indent=2)
                    }]
                }

            # 7. mysql_read_query
            elif name == "mysql_read_query":
                query = arguments.get("query", "").strip()
                if not query.lower().startswith(("select", "show", "desc", "explain")):
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": "Only read queries (SELECT, SHOW, DESC, EXPLAIN) are allowed in mysql_read_query. Use mysql_execute_statement for DML."}]
                    }
                cursor.execute(query)
                rows = cursor.fetchall()
                # 安全防护：屏蔽凭据表中的密文字段，防止密文进入 Agent 上下文
                for r in rows:
                    if isinstance(r, dict):
                        for secret_col in ("password_cipher", "private_key_cipher", "token_hash"):
                            if secret_col in r and r[secret_col]:
                                r[secret_col] = "[REDACTED_VAULT_SECRET]"
                result_text = json.dumps(rows, default=json_serial, ensure_ascii=False, indent=2)
                return {
                    "content": [{"type": "text", "text": result_text}]
                }

            # 8. mysql_list_tables
            elif name == "mysql_list_tables":
                cursor.execute("SHOW TABLES")
                tables = [list(r.values())[0] for r in cursor.fetchall()]
                result_text = json.dumps({"tables": tables, "total": len(tables)}, ensure_ascii=False, indent=2)
                return {
                    "content": [{"type": "text", "text": result_text}]
                }

            # 9. mysql_describe_table
            elif name == "mysql_describe_table":
                table_name = arguments.get("table_name", "").strip()
                clean_name = "".join(c for c in table_name if c.isalnum() or c == "_")
                cursor.execute(f"DESCRIBE `{clean_name}`")
                columns = cursor.fetchall()
                result_text = json.dumps(columns, default=json_serial, ensure_ascii=False, indent=2)
                return {
                    "content": [{"type": "text", "text": result_text}]
                }

            # 10. mysql_execute_statement
            elif name == "mysql_execute_statement":
                stmt = arguments.get("statement", "").strip()
                cursor.execute(stmt)
                affected = cursor.rowcount
                return {
                    "content": [{"type": "text", "text": f"Query OK, {affected} rows affected."}]
                }

            else:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}]
                }
    finally:
        conn.close()

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "agent-control-mcp",
                        "version": "1.2.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            try:
                res = handle_call_tool(params)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": res
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Execution error: {str(e)}\n{traceback.format_exc()}"}]
                    }
                }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        else:
            if req_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method {method} not found"
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    main()
