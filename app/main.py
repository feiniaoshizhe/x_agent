"""FastAPI application main entry point"""

import os

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config.settings import settings
from app.core.logger import logger_manager
from app.middleware.lifespan import lifespan
from app.routers import v1_router

# Create LoggerManager instance
logger_manager.setup()

# Create Logger instance
logger = logger_manager.get_logger(__name__)


# Create FastAPI instance
app = FastAPI(
    lifespan=lifespan,
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    description=settings.app.APP_DESCRIPTION,
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """HTTP exception handler"""
    logger.error(f"HTTPException: {exc}")
    error_detail = exc.detail
    
    if isinstance(error_detail, dict):
        error_message = error_detail.get("error", str(error_detail))
    else:
        error_message = str(error_detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "error": error_message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": 500, "error": "Internal server error"},
    )


# CORS middleware
allow_origins = [x.strip() for x in settings.cors.CORS_ALLOWED_ORIGINS.split(',') if x.strip()]
allow_methods = [x.strip() for x in settings.cors.CORS_ALLOW_METHODS.split(',') if x.strip()]
allow_headers = [x.strip() for x in settings.cors.CORS_ALLOW_HEADERS.split(',') if x.strip()]
allow_credentials = settings.cors.CORS_ALLOW_CREDENTIALS
expose_headers = [x.strip() for x in settings.cors.CORS_EXPOSE_HEADERS.split(',') if x.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    allow_credentials=allow_credentials,
    expose_headers=expose_headers,
)


# Static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Include routers
app.include_router(v1_router, prefix="/api")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# OpenAPI documentation
def custom_openapi():
    """Custom OpenAPI documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app.APP_NAME,
        version=settings.app.APP_VERSION,
        description=settings.app.APP_DESCRIPTION,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Start application
if __name__ == "__main__":
    if settings.app.ENV == "development":
        logger.info("🚩 Starting the application in development mode...")
        uvicorn.run(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
        )
