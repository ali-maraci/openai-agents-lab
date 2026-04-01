from app.database import init_db, create_run, complete_run
from app.monitoring.metrics import get_run_stats, get_agent_distribution, get_status_distribution


def _seed_runs(db_path, count=10):
    init_db(db_path)
    agents = ["Math_Conversion_Agent", "History Agent", "General Agent"]
    statuses = ["completed", "completed", "completed", "failed", "guardrail_blocked"]
    for i in range(count):
        run_id = create_run(db_path, session_id=f"s{i}", input_text=f"msg{i}")
        complete_run(db_path, run_id, output=f"resp{i}", status=statuses[i % len(statuses)], final_agent=agents[i % len(agents)])


def test_get_run_stats(tmp_db_path):
    _seed_runs(tmp_db_path)
    stats = get_run_stats(tmp_db_path)
    assert stats["total_runs"] == 10
    assert stats["completed"] == 6
    assert stats["failed"] == 2
    assert stats["guardrail_blocked"] == 2


def test_get_agent_distribution(tmp_db_path):
    _seed_runs(tmp_db_path)
    dist = get_agent_distribution(tmp_db_path)
    agents = {d["agent"]: d["count"] for d in dist}
    assert "Math_Conversion_Agent" in agents
    assert "History Agent" in agents


def test_get_status_distribution(tmp_db_path):
    _seed_runs(tmp_db_path)
    dist = get_status_distribution(tmp_db_path)
    statuses = {d["status"]: d["count"] for d in dist}
    assert statuses["completed"] == 6
    assert statuses["failed"] == 2
