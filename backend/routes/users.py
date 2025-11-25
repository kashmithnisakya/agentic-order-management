from fastapi import APIRouter, HTTPException
from models import User


def init_user_routes(users_data):
    """Initialize user routes with dependencies"""

    router = APIRouter(prefix="/api/users", tags=["Users"])

    @router.get("/{user_id}", response_model=User)
    def get_user(user_id: str):
        """Get user information"""
        user = next(
            (u for u in users_data if u["user_id"] == user_id),
            None
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    return router
