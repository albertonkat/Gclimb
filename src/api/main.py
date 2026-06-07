"""
Gclimb Patient Data Extraction API

FastAPI application that accepts PDFs and faxes, extracts structured
patient data using Claude, validates it, and pushes to Nymble EMR and EzClaim.

Run locally:
    uvicorn src.api.main:app --reload --port 8000

Production:
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes.extraction import router as extraction_router
from .routes.ingest import router as ingest_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Gclimb Extraction API starting up")
    if not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("ANTHROPIC_API_KEY not set — extraction will fail")
    yield
    logger.info("Gclimb Extraction API shutting down")


app = FastAPI(
    title="Gclimb Patient Data Extraction API",
    description=(
        "HIPAA-aware patient data extraction from PDFs and faxes using Claude. "
        "Integrates with Nymble EMR and EzClaim billing."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(extraction_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "gclimb-extraction"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error — see server logs"},
    )
