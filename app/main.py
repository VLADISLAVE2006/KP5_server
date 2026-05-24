import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.rooms import room_manager
from app.routers import admin, tasks, users

app = FastAPI(title="Task Manager API")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "env": os.getenv("APP_ENV", "local")}


@app.get("/rooms/{room_id}/users", tags=["rooms"])
def get_room_users(room_id: str) -> dict:
    return {"room_id": room_id, "users": room_manager.get_users(room_id)}


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str, username: str | None = None) -> None:
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    username = username.strip()
    await room_manager.connect(room_id, username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                text: str = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json({"type": "error", "detail": "Message is too long"})
                else:
                    await room_manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text,
                    })
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username)
