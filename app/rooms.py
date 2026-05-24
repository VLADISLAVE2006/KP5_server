from collections import defaultdict

from fastapi import WebSocket


class RoomManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, WebSocket]] = defaultdict(dict)

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[room_id][username] = websocket
        await self.broadcast(room_id, {"type": "join", "username": username})

    async def disconnect(self, room_id: str, username: str) -> None:
        self._rooms[room_id].pop(username, None)
        if not self._rooms[room_id]:
            del self._rooms[room_id]
        else:
            await self.broadcast(room_id, {"type": "leave", "username": username})

    async def broadcast(self, room_id: str, payload: dict) -> None:
        for ws in list(self._rooms.get(room_id, {}).values()):
            await ws.send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        return list(self._rooms.get(room_id, {}).keys())


room_manager = RoomManager()
