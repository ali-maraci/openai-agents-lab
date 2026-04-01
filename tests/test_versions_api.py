def test_create_version_snapshot(client):
    response = client.post("/api/versions", json={"name": "v1.0", "description": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "v1.0"
    assert data["id"] is not None


def test_list_versions(client):
    client.post("/api/versions", json={"name": "v1.0"})
    client.post("/api/versions", json={"name": "v1.1"})
    response = client.get("/api/versions")
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_get_version_not_found(client):
    response = client.get("/api/versions/nonexistent")
    assert response.status_code == 404
