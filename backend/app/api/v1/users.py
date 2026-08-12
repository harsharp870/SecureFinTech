from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserPublic, UserList

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserList, dependencies=[Depends(require_admin)])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Admin-only: list all registered users."""
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    return UserList(users=users, total=total)


@router.get("/me", response_model=UserPublic)
def get_profile(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user
