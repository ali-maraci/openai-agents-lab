import json
from app.database import init_db
from app.versioning.registry import create_version, get_version, list_versions, snapshot_current


def test_create_and_get_version(tmp_db_path):
    init_db(tmp_db_path)
    config = {
        "triage": {"name": "Triage Agent", "instructions": "Route to specialists", "handoffs": ["Math_Conversion_Agent", "History Agent", "General Agent"]},
        "specialists": {
            "Math_Conversion_Agent": {"instructions": "You are a math specialist.", "tools": ["calculate", "convert_temperature", "convert_distance", "convert_weight"]},
            "History Agent": {"instructions": "You are a history expert."},
            "General Agent": {"instructions": "You are a general assistant."},
        },
    }
    version_id = create_version(tmp_db_path, name="v1.0", description="Initial version", agent_config=config)
    version = get_version(tmp_db_path, version_id)
    assert version is not None
    assert version["name"] == "v1.0"
    assert version["description"] == "Initial version"
    loaded_config = json.loads(version["agent_config"])
    assert loaded_config["triage"]["name"] == "Triage Agent"


def test_list_versions(tmp_db_path):
    init_db(tmp_db_path)
    create_version(tmp_db_path, name="v1.0", agent_config={"triage": {}})
    create_version(tmp_db_path, name="v1.1", agent_config={"triage": {}})
    versions = list_versions(tmp_db_path)
    assert len(versions) == 2
    assert versions[0]["name"] == "v1.1"


def test_snapshot_current_agents(tmp_db_path):
    init_db(tmp_db_path)
    version_id = snapshot_current(tmp_db_path, name="v1.0", description="Snapshot test")
    version = get_version(tmp_db_path, version_id)
    config = json.loads(version["agent_config"])
    assert "triage" in config
    assert config["triage"]["name"] == "Triage Agent"
    assert "Math_Conversion_Agent" in config["specialists"]
