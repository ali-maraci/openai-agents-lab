import logging

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.config import settings
from app.evals.datasets import list_datasets, load_dataset
from app.evals.runner import run_eval
from app.evals.store import create_eval_run, get_eval_run, get_eval_case_results, list_eval_runs
from app.schemas import EvalRunRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/evals/run")
async def start_eval_run(request: EvalRunRequest, background_tasks: BackgroundTasks):
    """Start an eval run against a benchmark dataset. Runs in background."""
    available = list_datasets()
    if request.dataset not in available:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{request.dataset}' not found. Available: {available}",
        )
    dataset = load_dataset(request.dataset)
    eval_id = create_eval_run(settings.db_path, dataset_name=request.dataset, total_cases=len(dataset["cases"]))
    background_tasks.add_task(run_eval, dataset_name=request.dataset, db_path=settings.db_path, eval_id=eval_id)
    return {"eval_run_id": eval_id, "status": "running"}


@router.get("/evals/summary")
def get_eval_summary(dataset: str | None = None, limit: int = 20):
    """List eval runs with aggregate metrics. Optionally filter by dataset."""
    runs = list_eval_runs(settings.db_path, limit=limit)
    if dataset:
        runs = [r for r in runs if r["dataset_name"] == dataset]
    return {"eval_runs": runs, "count": len(runs)}


@router.get("/evals/datasets")
def get_available_datasets():
    """List available benchmark datasets."""
    return {"datasets": list_datasets()}


@router.get("/evals/{eval_id}")
def get_eval_detail(eval_id: str):
    """Get eval run details with case results."""
    eval_run = get_eval_run(settings.db_path, eval_id)
    if not eval_run:
        raise HTTPException(status_code=404, detail="Eval run not found")
    eval_run["case_results"] = get_eval_case_results(settings.db_path, eval_id)
    return eval_run
