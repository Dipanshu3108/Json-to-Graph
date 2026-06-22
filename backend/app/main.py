import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import generate_code, repair, validate

logger = logging.getLogger(__name__)

app = FastAPI(title="JSON Viz Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(validate.router)
app.include_router(repair.router)
app.include_router(generate_code.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("http.request method=%s path=%s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "http.response method=%s path=%s status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("http.unhandled_exception method=%s path=%s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": str(exc)},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
