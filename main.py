import os
import sys
import glob

# 自动环境兼容：若使用外部全局 Python/uvicorn 启动，自动引入项目内 venv 的依赖包与工作路径
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for _sp in glob.glob(os.path.join(_BASE_DIR, "venv", "lib", "python*", "site-packages")):
    if _sp not in sys.path and os.path.isdir(_sp):
        sys.path.insert(0, _sp)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Agent Control Plane - Comprehensive Task & Workflow Scheduling Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.requests import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    response = JSONResponse(
        status_code=500,
        content={"status": "ERROR", "message": str(exc)}
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

app.include_router(api_router)

DASHBOARD_HTML_PATH = os.path.join(os.path.dirname(__file__), "app", "templates", "dashboard.html")

@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/dashboard/talent")

@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
@app.get("/dashboard/{menu_path:path}", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard(menu_path: str = ""):
    if os.path.exists(DASHBOARD_HTML_PATH):
        with open(DASHBOARD_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard template not found</h1>", status_code=404)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "env": settings.APP_ENV,
        "dashboard_url": "/dashboard",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
