#!/usr/bin/env python3
"""
Agent Control MySQL MCP Server (Stdio JSON-RPC 2.0)
Exposes tools to inspect and query the local agent_control MySQL database.
Tools:
  - mysql_read_query: Execute SELECT queries on agent_control.
  - mysql_list_tables: List all tables in agent_control database.
  - mysql_describe_table: View schema/column definitions of a specified table.
  - mysql_execute_statement: Execute INSERT/UPDATE/DELETE statements.
"""

import sys
import os
import json
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

TOOLS = [
    {
        "name": "mysql_read_query",
        "description": "Execute a SELECT query against the local agent_control MySQL database.",
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
        "description": "Show column names, types, keys and comments for a given table in agent_control.",
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
            if name == "mysql_read_query":
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

            elif name == "mysql_list_tables":
                cursor.execute("SHOW TABLES")
                tables = [list(r.values())[0] for r in cursor.fetchall()]
                result_text = json.dumps({"tables": tables, "total": len(tables)}, ensure_ascii=False, indent=2)
                return {
                    "content": [{"type": "text", "text": result_text}]
                }

            elif name == "mysql_describe_table":
                table_name = arguments.get("table_name", "").strip()
                # sanitize table name
                clean_name = "".join(c for c in table_name if c.isalnum() or c == "_")
                cursor.execute(f"DESCRIBE `{clean_name}`")
                columns = cursor.fetchall()
                result_text = json.dumps(columns, default=json_serial, ensure_ascii=False, indent=2)
                return {
                    "content": [{"type": "text", "text": result_text}]
                }

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
                        "name": "mysql-agent-control",
                        "version": "1.0.0"
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
