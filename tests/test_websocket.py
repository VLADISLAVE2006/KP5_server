import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rooms import room_manager


@pytest.fixture(autouse=True)
def clear_rooms():
    room_manager._rooms.clear()
    yield
    room_manager._rooms.clear()


def test_connect_with_valid_username(client: TestClient):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "join"
        assert msg["username"] == "alice"


def test_send_and_receive_message(client: TestClient):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join event
        ws.send_json({"type": "message", "text": "Всем привет"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["text"] == "Всем привет"
        assert msg["username"] == "alice"
        assert msg["room_id"] == "python"


def test_two_clients_receive_same_message(client: TestClient):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()  # alice join
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            alice.receive_json()  # bob join event for alice
            bob.receive_json()   # bob join event for bob

            alice.send_json({"type": "message", "text": "Hello"})
            msg_alice = alice.receive_json()
            msg_bob = bob.receive_json()

            assert msg_alice["text"] == "Hello"
            assert msg_bob["text"] == "Hello"


def test_different_rooms_isolation(client: TestClient):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()  # join
        with client.websocket_connect("/ws/rooms/java?username=bob") as bob:
            bob.receive_json()  # join

            alice.send_json({"type": "message", "text": "Python only"})
            msg = alice.receive_json()
            assert msg["text"] == "Python only"
            # bob should not receive the message — check room users
            assert "bob" not in room_manager.get_users("python")


def test_message_too_long_returns_error(client: TestClient):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        ws.send_json({"type": "message", "text": "x" * 301})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "too long" in msg["detail"].lower()


def test_disconnect_removes_user(client: TestClient):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join

    resp = client.get("/rooms/python/users")
    assert resp.status_code == 200
    assert "alice" not in resp.json()["users"]
