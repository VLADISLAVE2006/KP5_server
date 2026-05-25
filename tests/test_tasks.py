from fastapi.testclient import TestClient


USER_HEADERS = {"X-User-Id": "10"}
OTHER_USER_HEADERS = {"X-User-Id": "99"}

TASK_PAYLOAD = {
    "title": "Подготовить тесты",
    "description": "Написать интеграционные тесты",
    "status": "todo",
    "priority": 4,
}


def test_create_task_success(client: TestClient):
    resp = client.post("/tasks", json=TASK_PAYLOAD, headers=USER_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == TASK_PAYLOAD["title"]
    assert data["owner_id"] == 10


def test_create_task_title_too_short(client: TestClient):
    resp = client.post("/tasks", json={**TASK_PAYLOAD, "title": "ab"}, headers=USER_HEADERS)
    assert resp.status_code == 422


def test_create_task_no_auth(client: TestClient):
    resp = client.post("/tasks", json=TASK_PAYLOAD)
    assert resp.status_code == 401


def test_user_sees_only_own_tasks(client: TestClient):
    client.post("/tasks", json=TASK_PAYLOAD, headers=USER_HEADERS)
    client.post("/tasks", json={**TASK_PAYLOAD, "title": "Чужая задача"}, headers=OTHER_USER_HEADERS)

    resp = client.get("/tasks", headers=USER_HEADERS)
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["owner_id"] == 10


def test_filter_by_status(client: TestClient):
    client.post("/tasks", json={**TASK_PAYLOAD, "status": "todo"}, headers=USER_HEADERS)
    client.post("/tasks", json={**TASK_PAYLOAD, "title": "Done task", "status": "done"}, headers=USER_HEADERS)

    resp = client.get("/tasks?status=done", headers=USER_HEADERS)
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["status"] == "done" for t in tasks)
    assert len(tasks) == 1


def test_filter_by_min_priority(client: TestClient):
    client.post("/tasks", json={**TASK_PAYLOAD, "priority": 1}, headers=USER_HEADERS)
    client.post("/tasks", json={**TASK_PAYLOAD, "title": "High prio", "priority": 5}, headers=USER_HEADERS)

    resp = client.get("/tasks?min_priority=4", headers=USER_HEADERS)
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["priority"] >= 4 for t in tasks)


def test_update_task_status(client: TestClient):
    create_resp = client.post("/tasks", json=TASK_PAYLOAD, headers=USER_HEADERS)
    task_id = create_resp.json()["id"]

    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers=USER_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_get_other_user_task_returns_404(client: TestClient):
    create_resp = client.post("/tasks", json=TASK_PAYLOAD, headers=OTHER_USER_HEADERS)
    task_id = create_resp.json()["id"]

    resp = client.get(f"/tasks/{task_id}", headers=USER_HEADERS)
    assert resp.status_code == 404


def test_get_nonexistent_task_returns_404(client: TestClient):
    resp = client.get("/tasks/9999", headers=USER_HEADERS)
    assert resp.status_code == 404


def test_delete_task_success(client: TestClient):
    create_resp = client.post("/tasks", json=TASK_PAYLOAD, headers=USER_HEADERS)
    task_id = create_resp.json()["id"]

    resp = client.delete(f"/tasks/{task_id}", headers=USER_HEADERS)
    assert resp.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}", headers=USER_HEADERS)
    assert get_resp.status_code == 404
