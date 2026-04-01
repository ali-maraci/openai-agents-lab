import logging
from fastapi import APIRouter, HTTPException
from app.config import settings
from app.versioning.registry import create_version, get_version, list_versions, snapshot_current
from app.schemas import CreateVersionRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/versions")
def create_agent_version(request: CreateVersionRequest):
    if request.snapshot_current:
        version_id = snapshot_current(settings.db_path, name=request.name, description=request.description)
    else:
        raise HTTPException(status_code=400, detail="Only snapshot_current=true is supported")
    version = get_version(settings.db_path, version_id)
    return version


@router.get("/versions")
def get_versions(limit: int = 50):
    versions = list_versions(settings.db_path, limit=limit)
    return {"versions": versions, "count": len(versions)}


@router.get("/versions/{version_id}")
def get_version_detail(version_id: str):
    version = get_version(settings.db_path, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version
