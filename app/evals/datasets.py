import json
from pathlib import Path

BENCHMARKS_DIR = "benchmarks"


class DatasetError(Exception):
    pass


def load_dataset(name: str, benchmarks_dir: str = BENCHMARKS_DIR) -> dict:
    """Load a benchmark dataset by name from the benchmarks directory."""
    path = Path(benchmarks_dir) / f"{name}.json"
    if not path.exists():
        raise DatasetError(f"Dataset '{name}' not found at {path}")
    with open(path) as f:
        dataset = json.load(f)
    validate_dataset(dataset)
    return dataset


def validate_dataset(dataset: dict) -> None:
    """Validate a benchmark dataset has required fields."""
    if "graders" not in dataset or not dataset["graders"]:
        raise DatasetError("Dataset must have a non-empty 'graders' list")
    if "cases" not in dataset or not dataset["cases"]:
        raise DatasetError("Dataset must have a non-empty 'cases' list")
    for i, case in enumerate(dataset["cases"]):
        if "id" not in case:
            raise DatasetError(f"Case {i} missing required field 'id'")
        if "input" not in case:
            raise DatasetError(f"Case {i} (id={case.get('id', '?')}) missing required field 'input'")


def list_datasets(benchmarks_dir: str = BENCHMARKS_DIR) -> list[str]:
    """List available benchmark dataset names."""
    path = Path(benchmarks_dir)
    if not path.exists():
        return []
    return [f.stem for f in sorted(path.glob("*.json"))]
