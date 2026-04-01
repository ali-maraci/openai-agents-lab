import json
import pytest
from app.evals.datasets import load_dataset, validate_dataset, DatasetError


@pytest.fixture
def sample_dataset(tmp_path):
    """Create a valid benchmark dataset file."""
    dataset = {
        "name": "test_routing",
        "description": "Test dataset",
        "graders": ["agent_match"],
        "cases": [
            {
                "id": "t_001",
                "input": "What is 2 + 2?",
                "expected_agent": "Math_Conversion_Agent",
                "expected_output": None,
                "tags": ["math"],
            },
            {
                "id": "t_002",
                "input": "When did WW2 end?",
                "expected_agent": "History Agent",
                "expected_output": None,
                "tags": ["history"],
            },
        ],
    }
    path = tmp_path / "test_routing.json"
    path.write_text(json.dumps(dataset))
    return str(tmp_path), "test_routing"


def test_load_dataset(sample_dataset):
    benchmarks_dir, name = sample_dataset
    dataset = load_dataset(name, benchmarks_dir=benchmarks_dir)
    assert dataset["name"] == "test_routing"
    assert len(dataset["cases"]) == 2
    assert dataset["graders"] == ["agent_match"]


def test_load_dataset_not_found():
    with pytest.raises(DatasetError, match="not found"):
        load_dataset("nonexistent", benchmarks_dir="/tmp/empty")


def test_validate_dataset_missing_cases():
    with pytest.raises(DatasetError, match="cases"):
        validate_dataset({"name": "bad", "graders": ["exact_match"]})


def test_validate_dataset_missing_graders():
    with pytest.raises(DatasetError, match="graders"):
        validate_dataset({"name": "bad", "cases": [{"id": "1", "input": "hi"}]})


def test_validate_dataset_empty_cases():
    with pytest.raises(DatasetError, match="cases"):
        validate_dataset({"name": "bad", "graders": ["exact_match"], "cases": []})


def test_validate_dataset_case_missing_id():
    with pytest.raises(DatasetError, match="id"):
        validate_dataset({
            "name": "bad",
            "graders": ["exact_match"],
            "cases": [{"input": "hello"}],
        })


def test_validate_dataset_case_missing_input():
    with pytest.raises(DatasetError, match="input"):
        validate_dataset({
            "name": "bad",
            "graders": ["exact_match"],
            "cases": [{"id": "1"}],
        })
