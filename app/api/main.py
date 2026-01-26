"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pathlib import Path

from app.core.scheduler import lifespan_scheduler
from app.api.routers import (
    products, 
    categories, 
    units, 
    purchase_types, 
    stores, 
    labels, 
    tracked_items,
    extraction,
    logs,
    scheduler,
    email,
    ui
)

app = FastAPI(
    title="Price Spy",
    description="Visual price tracking with AI",
    version="0.3.0",
    lifespan=lifespan_scheduler
)

# Include API routers
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(units.router)
app.include_router(purchase_types.router)
app.include_router(stores.router)
app.include_router(labels.router)
app.include_router(tracked_items.router)
app.include_router(extraction.router)
app.include_router(logs.router)
app.include_router(scheduler.router)
app.include_router(email.router)

# Include UI router (at the end as it contains catch-all style routes like "/")
app.include_router(ui.router)

# Mount screenshots directory if it exists
screenshots_dir = Path("screenshots")
if screenshots_dir.exists():
    app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors by returning a 422 JSON response."""
    from app.core.error_logger import log_error_to_db
    log_error_to_db(
        error_type="validation_error",
        message=f"Validation error: {str(exc)}",
        url=str(request.url)
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global catch-all for unhandled exceptions."""
    from app.core.error_logger import log_error_to_db
    log_error_to_db(
        error_type="unhandled_exception",
        message=str(exc),
        url=str(request.url)
    )
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred."}
    )


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.3.0"}
