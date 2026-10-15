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

import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.router import api_router
from app.core.config import settings

logger = logging.getLogger("agent_control.security")

app = FastAPI(
    title=settings.APP_NAME,
    description="Agent Control Plane - Comprehensive Task & Workflow Scheduling Engine (Secured)",
    version="1.0.0"
)

# CORS 安全加固：严禁在通配符 * 下开启 allow_credentials=True
cors_origins = settings.CORS_ORIGINS
has_wildcard = "*" in cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if not has_wildcard else ["*"],
    allow_credentials=not has_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def security_startup_check():
    try:
        from scripts.seed_servers import seed_server_credentials
        seed_server_credentials()
    except Exception as e:
        logger.warning(f"Auto table creation / seed skipped or failed: {e}")

    if settings.REQUIRE_AUTH:
        if settings.API_KEY:
            logger.info("🔐 [SECURITY] API 身份认证已启用 (Master API Key 已配置)")
        else:
            logger.warning(
                f"⚠️  [SECURITY] 未配置 API_KEY，已自动生成引导密钥 (Bootstrap Key):\n"
                f"    {settings.effective_api_key}\n"
                f"    请在 .env 中设置 API_KEY 以固化密钥。"
            )
    else:
        logger.warning("🚨 [SECURITY] REQUIRE_AUTH=false，当前 API 处于未认证开放模式！")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    headers = dict(getattr(exc, "headers", {}) or {})
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "ERROR", "message": exc.detail},
        headers=headers
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return await http_exception_handler(request, exc)
    logger.exception(f"Unhandled server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "ERROR", "message": str(exc)}
    )

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
        "auth_enabled": settings.REQUIRE_AUTH,
        "dashboard_url": "/dashboard",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
