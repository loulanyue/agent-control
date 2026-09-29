#!/usr/bin/env python3
"""
Agent Control MCP Server (Stdio JSON-RPC 2.0 / Model Context Protocol)
Exposes tools for Agent Control Plane orchestration, DAG inspection, task dispatching,
and database inspection.

Tools:
  - control_list_agents: List all registered AI agents with status, capabilities, and last heartbeat.
  - control_list_tasks: Query task queue by status, priority, and keyword.
  - control_dispatch_task: Dispatch/create a new autonomous task into the control plane queue.
  - control_get_task_status: Get detailed task execution status, attempts, and artifacts.
  - control_list_graphs: List DAG workflows and orchestration pipelines.
  - control_get_system_metrics: Retrieve cluster metrics (agents, active tasks, DAG runs, DB status).
  - mysql_read_query: Execute SELECT/SHOW/DESCRIBE queries against the agent_control database.
  - mysql_list_tables: List all 40 tables available in the agent_control database.
  - mysql_describe_table: Inspect schema definitions of any table.
  - mysql_execute_statement: Execute INSERT/UPDATE/DELETE DML statements.
"""

import sys
import os
import json
import time
import decimal
import datetime
import traceback
import pymysql

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
        "description": "List all 40 tables available in the agent_control MySQL database.",
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
                        "version": "1.1.0"
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
