import pytest
from unittest.mock import MagicMock, patch
from agent_control_sdk import (
    AgentControlClient,
    Agent,
    Task,
    GraphDefinition,
    SystemMetrics,
    TaskPriority,
)
from agent_control_sdk.exceptions import APIError, NotFoundError

def test_sdk_models_serialization():
    agent_data = {
        "id": 1,
        "public_id": "AGT_01HQ",
        "name": "CrawlerAgent-01",
        "agent_type": "crawler",
        "status": "online",
        "capabilities": ["http", "extract"],
    }
    agent = Agent.from_dict(agent_data)
    assert agent.id == 1
    assert agent.name == "CrawlerAgent-01"
    assert "extract" in agent.capabilities

    task_data = {
        "id": 10,
        "public_id": "TSK_01HQ",
        "title": "Crawl Hangzhou notices",
        "priority": "high",
        "status": "pending",
    }
    task = Task.from_dict(task_data)
    assert task.title == "Crawl Hangzhou notices"
    assert task.priority == "high"

    stats_data = {
        "agents": {"total_agents": 5, "online_agents": 3},
        "tasks": {"total_tasks": 42, "completed_tasks": 40},
        "graphs": {"definitions": 8},
    }
    metrics = SystemMetrics.from_dict(stats_data)
    assert metrics.total_agents == 5
    assert metrics.online_agents == 3
    assert metrics.total_tasks == 42
    assert metrics.completed_tasks == 40
    assert metrics.total_graphs == 8

def test_sdk_client_agents_list():
    client = AgentControlClient(base_url="http://mock-server")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"total": 1, "page": 1, "page_size": 20, "items": [{"id": 1, "name": "Agent1"}]}'
    mock_resp.json.return_value = {
        "total": 1,
        "page": 1,
        "page_size": 20,
        "items": [{"id": 1, "name": "Agent1"}]
    }

    with patch.object(client.session, "request", return_value=mock_resp):
        res = client.agents.list()
        assert res["total"] == 1
        assert len(res["items"]) == 1
        assert res["items"][0].name == "Agent1"

def test_sdk_client_dispatch_task():
    client = AgentControlClient(base_url="http://mock-server")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"id": 99, "title": "Test Task", "priority": "high"}'
    mock_resp.json.return_value = {"id": 99, "title": "Test Task", "priority": "high"}

    with patch.object(client.session, "request", return_value=mock_resp):
        task = client.tasks.dispatch(title="Test Task", priority=TaskPriority.HIGH)
        assert task.id == 99
        assert task.title == "Test Task"

def test_sdk_client_not_found():
    client = AgentControlClient(base_url="http://mock-server")
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Not Found"

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(NotFoundError):
            client.tasks.get(9999)
