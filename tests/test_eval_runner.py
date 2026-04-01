import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.database import init_db
from app.evals.runner import run_eval, execute_case
from app.evals.store import get_eval_run, get_eval_case_results


@pytest.fixture
def tool_routing_dataset(tmp_path):
    """Create a small tool routing dataset for testing."""
    dataset = {
        "name": "test_routing",
        "description": "Test",
        "graders": ["agent_match"],
        "cases": [
            {"id": "t_001", "input": "What is 2+2?", "expected_agent": "Math_Conversion_Agent"},
            {"id": "t_002", "input": "Hello", "expected_agent": "General Agent"},
        ],
    }
    benchmarks_dir = tmp_path / "benchmarks"
    benchmarks_dir.mkdir()
    (benchmarks_dir / "test_routing.json").write_text(json.dumps(dataset))
    return str(benchmarks_dir)


class TestExecuteCase:
    @pytest.mark.asyncio
    async def test_execute_case_returns_result(self, tmp_db_path):
        init_db(tmp_db_path)
        mock_result = MagicMock()
        mock_result.final_output = "4"
        mock_result.last_agent = MagicMock()
        mock_result.last_agent.name = "Math_Conversion_Agent"

        with patch("app.evals.runner.Runner.run", new_callable=AsyncMock, return_value=mock_result):
            result = await execute_case(
                case={"id": "t_001", "input": "What is 2+2?"},
                db_path=tmp_db_path,
            )
        assert result["output"] == "4"
        assert result["agent"] == "Math_Conversion_Agent"
        assert result["run_id"] is not None
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_execute_case_handles_error(self, tmp_db_path):
        init_db(tmp_db_path)
        with patch("app.evals.runner.Runner.run", new_callable=AsyncMock, side_effect=Exception("API error")):
            result = await execute_case(
                case={"id": "t_001", "input": "What is 2+2?"},
                db_path=tmp_db_path,
            )
        assert result["error"] == "API error"
        assert result["output"] == ""


class TestRunEval:
    @pytest.mark.asyncio
    async def test_run_eval_full(self, tmp_db_path, tool_routing_dataset):
        init_db(tmp_db_path)
        mock_result = MagicMock()
        mock_result.final_output = "4"
        mock_result.last_agent = MagicMock()
        mock_result.last_agent.name = "Math_Conversion_Agent"

        with patch("app.evals.runner.Runner.run", new_callable=AsyncMock, return_value=mock_result):
            eval_id = await run_eval(
                dataset_name="test_routing",
                db_path=tmp_db_path,
                benchmarks_dir=tool_routing_dataset,
            )

        eval_run = get_eval_run(tmp_db_path, eval_id)
        assert eval_run["status"] == "completed"
        assert eval_run["total_cases"] == 2
        # Case t_001 expects Math_Conversion_Agent -> matches mock -> pass
        # Case t_002 expects General Agent -> gets Math_Conversion_Agent -> fail
        assert eval_run["passed"] == 1
        assert eval_run["failed"] == 1

        case_results = get_eval_case_results(tmp_db_path, eval_id)
        assert len(case_results) == 2
