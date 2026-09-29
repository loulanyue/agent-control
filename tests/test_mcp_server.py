import pytest
import json
from unittest.mock import MagicMock, patch
from mcp_server import handle_call_tool, TOOLS

def test_mcp_server_tools_list():
    assert len(TOOLS) == 10
    names = [t["name"] for t in TOOLS]
    assert "control_list_agents" in names
    assert "control_list_tasks" in names
    assert "control_dispatch_task" in names
    assert "control_get_task_status" in names
    assert "control_list_graphs" in names
    assert "control_get_system_metrics" in names
    assert "mysql_read_query" in names
    assert "mysql_list_tables" in names
    assert "mysql_describe_table" in names
    assert "mysql_execute_statement" in names

def test_mcp_handle_list_agents_mock():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Agent Alpha", "status": "online"}
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("mcp_server.get_connection", return_value=mock_conn):
        res = handle_call_tool({"name": "control_list_agents", "arguments": {}})
        assert "content" in res
        text = res["content"][0]["text"]
        data = json.loads(text)
        assert data["total"] == 1
        assert data["agents"][0]["name"] == "Agent Alpha"

def test_mcp_handle_get_metrics_mock():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        {"c": 5}, # total_agents
        {"c": 3}, # online_agents
        {"c": 20}, # total_tasks
        {"c": 2}, # pending_tasks
        {"c": 18}, # completed_tasks
        {"c": 4}, # total_graphs
        {"c": 10}, # total_runs
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("mcp_server.get_connection", return_value=mock_conn):
        res = handle_call_tool({"name": "control_get_system_metrics", "arguments": {}})
        assert "content" in res
        data = json.loads(res["content"][0]["text"])
        assert data["status"] == "operational"
        assert data["agents"]["total"] == 5
        assert data["tasks"]["completed"] == 18

def test_mcp_handle_unknown_tool():
    mock_conn = MagicMock()
    with patch("mcp_server.get_connection", return_value=mock_conn):
        res = handle_call_tool({"name": "unknown_tool", "arguments": {}})
        assert res.get("isError") is True
