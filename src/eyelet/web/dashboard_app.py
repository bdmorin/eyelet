"""FastAPI web application for eyelet dashboard."""

from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from eyelet.services.metrics_service import MetricsService


def create_dashboard_app() -> FastAPI:
    """Create and configure the FastAPI dashboard application."""
    
    app = FastAPI(
        title="Eyelet Database Dashboard",
        description="Monitor eyelet databases across the system",
        version="0.1.0"
    )
    
    # Get paths relative to this file
    web_dir = Path(__file__).parent
    templates_dir = web_dir / "templates" 
    static_dir = web_dir / "static"
    
    # Setup templates and static files
    templates = Jinja2Templates(directory=str(templates_dir))
    
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Initialize services
    metrics_service = MetricsService()
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home(request: Request):
        """Main dashboard page."""
        system_metrics = metrics_service.get_system_metrics()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "system_metrics": system_metrics,
            "title": "Eyelet Dashboard"
        })
    
    @app.get("/api/metrics")
    async def get_metrics():
        """API endpoint for system metrics."""
        system_metrics = metrics_service.get_system_metrics()
        
        # Convert to dict for JSON serialization
        return {
            "total_databases": system_metrics.total_databases,
            "total_records": system_metrics.total_records,
            "active_databases": system_metrics.active_databases,
            "total_errors": system_metrics.total_errors,
            "unique_sessions": system_metrics.unique_sessions,
            "last_updated": system_metrics.last_updated.isoformat(),
            "databases": [
                {
                    "path": str(db.path),
                    "exists": db.exists,
                    "record_count": db.record_count,
                    "last_activity": db.last_activity.isoformat() if db.last_activity else None,
                    "activity_level": db.activity_level.value,
                    "schema_version": db.schema_version.value,
                    "recent_errors": db.recent_errors,
                    "size_bytes": db.size_bytes,
                    "error_rate": db.error_rate,
                    "hook_types": db.hook_types,
                    "tools": db.tools
                }
                for db in system_metrics.databases
            ]
        }
    
    @app.get("/api/hooks")
    async def get_recent_hooks(limit: int = 20):
        """API endpoint for recent hooks."""
        system_metrics = metrics_service.get_system_metrics()
        all_hooks = []
        
        # Collect hooks from all active databases
        for db_metrics in system_metrics.databases:
            if db_metrics.exists and db_metrics.record_count > 0:
                db_hooks = metrics_service.get_recent_hooks(db_metrics.path, limit)
                all_hooks.extend(db_hooks)
        
        # Sort by timestamp and limit
        all_hooks.sort(key=lambda h: h.timestamp, reverse=True)
        recent_hooks = all_hooks[:limit]
        
        # Convert to dict for JSON serialization
        return {
            "hooks": [
                {
                    "id": hook.id,
                    "timestamp": hook.timestamp.isoformat(),
                    "hook_type": hook.hook_type,
                    "tool_name": hook.tool_name,
                    "session_id": hook.session_id,
                    "status": hook.status,
                    "duration_ms": hook.duration_ms,
                    "error_message": hook.error_message,
                    "database_path": str(hook.database_path)
                }
                for hook in recent_hooks
            ]
        }
    
    @app.get("/api/search")
    async def search_hooks(q: str, limit: int = 50):
        """API endpoint for searching hooks."""
        results = metrics_service.search_hooks(q, limit)
        
        return {
            "query": q,
            "results": [
                {
                    "id": hook.id,
                    "timestamp": hook.timestamp.isoformat(),
                    "hook_type": hook.hook_type,
                    "tool_name": hook.tool_name,
                    "session_id": hook.session_id,
                    "status": hook.status,
                    "duration_ms": hook.duration_ms,
                    "error_message": hook.error_message,
                    "database_path": str(hook.database_path)
                }
                for hook in results
            ]
        }
    
    return app