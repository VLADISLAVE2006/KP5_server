from fastapi.testclient import TestClient

USER_HEADERS = {"X-User-Id": "10", "X-User-Role": "user"}
ADMIN_HEADERS = {"X-User-Id": "1", "X-User-Role": "admin"}
OTHER_USER_HEADERS = {"X-User-Id": "99", "X-User-Role": "user"}

TASK_PAYLOAD = {"title": "Test task", "status": "todo", "priority": 3}


def test_users_me(client: TestClient):
    resp = client.get("/users/me", headers=USER_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 10
    assert data["role"] == "user"


def test_users_me_no_header_returns_401(client: TestClient):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_regular_user_cannot_access_admin_stats(client: TestClient):
    resp = client.get("/admin/stats", headers=USER_HEADERS)
    assert resp.status_code == 403


def test_admin_gets_stats(client: TestClient):
    client.post("/tasks", json=TASK_PAYLOAD, headers=USER_HEADERS)
    client.post("/tasks", json={**TASK_PAYLOAD, "status": "done"}, headers=USER_HEADERS)

    resp = client.get("/admin/stats", headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 2
    assert "todo" in data["by_status"]
    assert "done" in data["by_status"]


def test_regular_user_cannot_delete_others_task(client: TestClient):
    create_resp = client.post("/tasks", json=TASK_PAYLOAD, headers=OTHER_USER_HEADERS)
    task_id = create_resp.json()["id"]

    resp = client.delete(f"/tasks/{task_id}", headers=USER_HEADERS)
    assert resp.status_code == 404


def test_admin_can_delete_any_task(client: TestClient):
    create_resp = client.post("/tasks", json=TASK_PAYLOAD, headers=USER_HEADERS)
    task_id = create_resp.json()["id"]

    resp = client.delete(f"/admin/tasks/{task_id}", headers=ADMIN_HEADERS)
    assert resp.status_code == 204


def test_health_endpoint(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "env" in data
