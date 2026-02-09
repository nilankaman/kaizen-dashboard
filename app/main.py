from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.core.logging_middleware import RequestLoggingMiddleware

from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.teams import router as teams_router
from app.routes.ideas import router as ideas_router
from app.routes.tasks import router as tasks_router
from app.routes.dashboard import router as dashboard_router
from app.routes.audit import router as audit_router

app = FastAPI(title="Kaizen (改善) Management Dashboard Backend")

app.add_middleware(RequestLoggingMiddleware)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", None)
    if isinstance(exc.detail, dict) and "error_code" in exc.detail:
        payload = exc.detail
    else:
        payload = {"error_code": "HTTP_ERROR", "message": str(exc.detail)}
    if request_id:
        payload["request_id"] = request_id
    return JSONResponse(status_code=exc.status_code, content=payload)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(ideas_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {"status": "ok", "service": "kaizen-dashboard-backend"}
