import json
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.config import settings
from app.experiments.runner import create_experiment, get_experiment, run_experiment
from app.schemas import ExperimentRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/experiments/compare")
async def start_experiment(request: ExperimentRequest, background_tasks: BackgroundTasks):
    exp_id = create_experiment(
        settings.db_path,
        dataset_name=request.dataset,
        baseline_version_id=request.baseline_version_id,
        candidate_version_id=request.candidate_version_id,
    )
    background_tasks.add_task(
        run_experiment,
        db_path=settings.db_path,
        dataset_name=request.dataset,
        baseline_version_id=request.baseline_version_id,
        candidate_version_id=request.candidate_version_id,
        exp_id=exp_id,
    )
    return {"experiment_id": exp_id, "status": "running"}


@router.get("/experiments/{exp_id}")
def get_experiment_detail(exp_id: str):
    exp = get_experiment(settings.db_path, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if exp.get("result"):
        exp["result"] = json.loads(exp["result"])
    return exp
