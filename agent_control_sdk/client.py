"""
High-level Agent Control Client.
"""

from typing import Dict, Any, Optional, List, Union
import json
import urllib.parse
import requests

from .models import (
    Agent,
    Task,
    GraphDefinition,
    GraphRun,
    SystemMetrics,
    TaskPriority,
    TaskStatus,
)
from .exceptions import (
    AgentControlError,
    APIError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    ConnectionError,
)

class _AgentsEndpoint:
    def __init__(self, client: "AgentControlClient"):
        self._c = client

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if keyword:
            params["keyword"] = keyword
        res = self._c._get("/api/v1/agents", params=params)
        items = [Agent.from_dict(item) for item in res.get("items", [])]
        return {
            "total": res.get("total", 0),
            "page": res.get("page", page),
            "page_size": res.get("page_size", page_size),
            "items": items,
        }

    def register(
        self,
        name: str,
        agent_type: str = "general",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        payload = {
            "name": name,
            "agent_type": agent_type,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
        }
        res = self._c._post("/api/v1/agents", data=payload)
        return Agent.from_dict(res)

    def heartbeat(self, agent_id: int, status: str = "online", metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": status, "metrics": metrics or {}}
        return self._c._post(f"/api/v1/agents/{agent_id}/heartbeat", data=payload)


class _TasksEndpoint:
    def __init__(self, client: "AgentControlClient"):
        self._c = client

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if keyword:
            params["keyword"] = keyword
        res = self._c._get("/api/v1/tasks", params=params)
        items = [Task.from_dict(item) for item in res.get("items", [])]
        return {
            "total": res.get("total", 0),
            "page": res.get("page", page),
            "page_size": res.get("page_size", page_size),
            "items": items,
        }

    def get(self, task_id: int) -> Task:
        res = self._c._get(f"/api/v1/tasks/{task_id}")
        return Task.from_dict(res)

    def dispatch(
        self,
        title: str,
        objective: Optional[str] = None,
        priority: Union[TaskPriority, str] = TaskPriority.NORMAL,
        source_type: str = "sdk",
        external_id: Optional[str] = None,
    ) -> Task:
        payload = {
            "title": title,
            "objective": objective or "",
            "priority": str(priority.value if isinstance(priority, TaskPriority) else priority),
            "source_type": source_type,
        }
        if external_id:
            payload["external_id"] = external_id
        res = self._c._post("/api/v1/tasks", data=payload)
        return Task.from_dict(res)

    def claim(self, task_id: int, agent_id: int, lease_seconds: int = 300) -> Dict[str, Any]:
        payload = {"agent_id": agent_id, "lease_seconds": lease_seconds}
        return self._c._post(f"/api/v1/tasks/{task_id}/claim", data=payload)

    def heartbeat(self, task_id: int, attempt_id: int, lease_seconds: int = 300) -> Dict[str, Any]:
        payload = {"attempt_id": attempt_id, "lease_seconds": lease_seconds}
        return self._c._post(f"/api/v1/tasks/{task_id}/heartbeat", data=payload)

    def complete(self, task_id: int, attempt_id: int, result_summary: Optional[str] = None) -> Dict[str, Any]:
        payload = {"attempt_id": attempt_id, "result_summary": result_summary or "Completed via SDK"}
        return self._c._post(f"/api/v1/tasks/{task_id}/complete", data=payload)

    def fail(self, task_id: int, attempt_id: int, error_message: str) -> Dict[str, Any]:
        payload = {"attempt_id": attempt_id, "error_message": error_message}
        return self._c._post(f"/api/v1/tasks/{task_id}/fail", data=payload)


class _GraphsEndpoint:
    def __init__(self, client: "AgentControlClient"):
        self._c = client

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if keyword:
            params["keyword"] = keyword
        res = self._c._get("/api/v1/graphs", params=params)
        items = [GraphDefinition.from_dict(item) for item in res.get("items", [])]
        return {
            "total": res.get("total", 0),
            "page": res.get("page", page),
            "page_size": res.get("page_size", page_size),
            "items": items,
        }

    def list_runs(
        self,
        page: int = 1,
        page_size: int = 20,
        graph_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if graph_id is not None:
            params["graph_id"] = graph_id
        if status:
            params["status"] = status
        res = self._c._get("/api/v1/graphs/runs", params=params)
        items = [GraphRun.from_dict(item) for item in res.get("items", [])]
        return {
            "total": res.get("total", 0),
            "page": res.get("page", page),
            "page_size": res.get("page_size", page_size),
            "items": items,
        }


class _SystemEndpoint:
    def __init__(self, client: "AgentControlClient"):
        self._c = client

    def health(self) -> Dict[str, Any]:
        return self._c._get("/health")

    def metrics(self) -> SystemMetrics:
        res = self._c._get("/api/v1/dashboard/stats")
        return SystemMetrics.from_dict(res)


class AgentControlClient:
    """
    Main entry point for Agent Control Python SDK.

    Usage:
        client = AgentControlClient(base_url="http://localhost:8000")
        agents = client.agents.list()
        task = client.tasks.dispatch(title="Collect Competitor Intelligence")
        metrics = client.system.metrics()
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = session or requests.Session()

        self.agents = _AgentsEndpoint(self)
        self.tasks = _TasksEndpoint(self)
        self.graphs = _GraphsEndpoint(self)
        self.system = _SystemEndpoint(self)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "agent-control-sdk/1.0.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = self._headers()
        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Could not connect to {url}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise AgentControlError(f"Request error: {e}") from e

        if resp.status_code == 404:
            raise NotFoundError(resp.text, status_code=404)
        if resp.status_code in (401, 403):
            raise AuthenticationError(resp.text, status_code=resp.status_code)
        if resp.status_code == 422:
            raise ValidationError(resp.text, status_code=422)
        if resp.status_code >= 400:
            raise APIError(resp.text, status_code=resp.status_code)

        if not resp.content:
            return None

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("POST", path, data=data)

    def _put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("PUT", path, data=data)

    def _delete(self, path: str) -> Any:
        return self._request("DELETE", path)
