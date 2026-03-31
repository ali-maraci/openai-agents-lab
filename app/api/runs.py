import logging

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.database import get_run, list_runs
from app.tracing.store import get_spans_for_run

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/runs")
def get_runs(limit: int = 50, offset: int = 0):
    """List all runs, most recent first."""
    runs = list_runs(settings.db_path, limit=limit, offset=offset)
    return {"runs": runs, "count": len(runs)}


@router.get("/runs/{run_id}")
def get_run_detail(run_id: str):
    """Get a single run with its trace spans."""
    run = get_run(settings.db_path, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run["spans"] = get_spans_for_run(settings.db_path, run_id)
    return run
