from fastapi import APIRouter, Depends
from app.core.security import get_current_client
from app.api.v1 import agents, tasks, graphs, rules, extensions, schedules, dashboard, contracts

api_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(get_current_client)]
)
api_router.include_router(agents.router)
api_router.include_router(tasks.router)
api_router.include_router(graphs.router)
api_router.include_router(rules.router)
api_router.include_router(schedules.router)
api_router.include_router(extensions.router)
api_router.include_router(dashboard.router)
api_router.include_router(contracts.router)

