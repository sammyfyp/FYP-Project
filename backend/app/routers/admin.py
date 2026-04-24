from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import AdminStatsResponse, AdminUsersResponse
from ..security import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=AdminUsersResponse)
def get_users(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> AdminUsersResponse:
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unreachable. Check backend DATABASE_URL and network/DNS access.",
        ) from exc
    return AdminUsersResponse(users=users)


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> AdminStatsResponse:
    try:
        total_users = db.query(func.count(User.id)).scalar() or 0
        users_with_emergency_number = (
            db.query(func.count(User.id))
            .filter(User.emergency_number.is_not(None))
            .filter(func.length(func.trim(User.emergency_number)) > 0)
            .scalar()
            or 0
        )
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unreachable. Check backend DATABASE_URL and network/DNS access.",
        ) from exc
    users_without_emergency_number = total_users - users_with_emergency_number

    return AdminStatsResponse(
        total_users=total_users,
        users_with_emergency_number=users_with_emergency_number,
        users_without_emergency_number=users_without_emergency_number,
    )
