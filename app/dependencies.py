from fastapi import Depends, Header, HTTPException

from app.schemas import CurrentUser
from app.storage import TaskStorage, storage


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> CurrentUser:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id header")
    return CurrentUser(id=user_id, role=x_user_role or "user")


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_storage() -> TaskStorage:
    return storage
