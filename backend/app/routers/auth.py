from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AdminUser
from ..schemas import AdminInfo, AdminLoginRequest, TokenResponse
from ..security import create_access_token

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])


@router.post("/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = str(payload.email).strip().lower()

    try:
        admin = db.query(AdminUser).filter(AdminUser.email == email).first()
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unreachable. Check backend DATABASE_URL and network/DNS access.",
        ) from exc

    if not admin or admin.password_text != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token(str(admin.id))
    return TokenResponse(access_token=token, admin=AdminInfo(id=admin.id, email=admin.email))
