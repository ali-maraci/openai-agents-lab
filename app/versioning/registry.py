import json
import sqlite3
import uuid
from datetime import datetime, timezone


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _row_to_dict(cursor: sqlite3.Cursor, row: tuple) -> dict:
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def create_version(db_path: str, name: str, agent_config: dict, description: str | None = None) -> str:
    """Create a new agent version snapshot. Returns the version ID."""
    version_id = str(uuid.uuid4())
    conn = _connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO agent_versions (id, name, description, agent_config, created_at) VALUES (?, ?, ?, ?, ?)",
            (version_id, name, description, json.dumps(agent_config), datetime.now(timezone.utc).isoformat()),
        )
    conn.close()
    return version_id


def get_version(db_path: str, version_id: str) -> dict | None:
    conn = _connect(db_path)
    cursor = conn.execute("SELECT * FROM agent_versions WHERE id = ?", (version_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row) if row else None
    conn.close()
    return result


def list_versions(db_path: str, limit: int = 50) -> list[dict]:
    conn = _connect(db_path)
    conn.row_factory = _row_to_dict
    rows = conn.execute(
        "SELECT * FROM agent_versions ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows


def snapshot_current(db_path: str, name: str, description: str | None = None) -> str:
    """Snapshot the current live agent configuration as a new version."""
    from app.agents.definitions import triage_agent, math_agent, history_agent, general_agent

    config = {
        "triage": {
            "name": triage_agent.name,
            "instructions": triage_agent.instructions,
            "handoffs": [h.name for h in triage_agent.handoffs],
        },
        "specialists": {},
    }
    for agent in [math_agent, history_agent, general_agent]:
        agent_conf = {"instructions": agent.instructions}
        if agent.tools:
            agent_conf["tools"] = [t.name for t in agent.tools]
        config["specialists"][agent.name] = agent_conf

    return create_version(db_path, name=name, description=description, agent_config=config)
