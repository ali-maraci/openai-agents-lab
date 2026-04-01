import logging
from fastapi import APIRouter
from app.config import settings
from app.monitoring.metrics import get_run_stats, get_agent_distribution, get_status_distribution, get_latency_percentiles, get_runs_over_time
from app.monitoring.failure_tags import get_failure_summary
from app.monitoring.alerts import get_active_alerts, resolve_alert

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard/metrics")
def get_dashboard_metrics(days: int = 7):
    return {
        "run_stats": get_run_stats(settings.db_path),
        "agent_distribution": get_agent_distribution(settings.db_path),
        "status_distribution": get_status_distribution(settings.db_path),
        "latency_percentiles": get_latency_percentiles(settings.db_path),
        "runs_over_time": get_runs_over_time(settings.db_path, days=days),
    }


@router.get("/dashboard/failures")
def get_dashboard_failures():
    return {"failure_summary": get_failure_summary(settings.db_path)}


@router.get("/dashboard/alerts")
def get_dashboard_alerts():
    return {"alerts": get_active_alerts(settings.db_path)}


@router.post("/dashboard/alerts/{alert_id}/resolve")
def resolve_dashboard_alert(alert_id: str):
    resolve_alert(settings.db_path, alert_id)
    return {"status": "resolved"}
