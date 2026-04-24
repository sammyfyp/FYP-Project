from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserEntryRequest, UserEntryResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/entry", response_model=UserEntryResponse, status_code=status.HTTP_200_OK)
def create_or_get_user_entry(payload: UserEntryRequest, db: Session = Depends(get_db)) -> UserEntryResponse:
    incoming_name = payload.name.strip()
    incoming_number = payload.emergency_number

    try:
        existing = (
            db.query(User)
            .filter(func.lower(func.trim(User.name)) == incoming_name.lower())
            .filter(
                func.coalesce(func.regexp_replace(func.coalesce(User.emergency_number, ""), r"\\s+", "", "g"), "")
                == (incoming_number or "")
            )
            .order_by(User.created_at.asc())
            .first()
        )
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unreachable. Check backend DATABASE_URL and network/DNS access.",
        ) from exc

    if existing:
        return UserEntryResponse(inserted=False, user=existing)

    user = User(name=incoming_name, emergency_number=incoming_number)
    db.add(user)

    try:
        db.commit()
    except OperationalError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unreachable. Check backend DATABASE_URL and network/DNS access.",
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        existing_after_race = (
            db.query(User)
            .filter(func.lower(func.trim(User.name)) == incoming_name.lower())
            .filter(
                func.coalesce(func.regexp_replace(func.coalesce(User.emergency_number, ""), r"\\s+", "", "g"), "")
                == (incoming_number or "")
            )
            .order_by(User.created_at.asc())
            .first()
        )
        if existing_after_race:
            return UserEntryResponse(inserted=False, user=existing_after_race)
        raise HTTPException(status_code=500, detail="Unable to create user entry.") from exc

    db.refresh(user)
    return UserEntryResponse(inserted=True, user=user)
