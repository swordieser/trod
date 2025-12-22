from fastapi import Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import User, UserRole


def get_current_user(
        request: Request,
        db: Session=Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).get(user_id)


def require_user(user=Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return user


# def require_user(user=Depends(get_current_user)):
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED
#         )
#     return user


def require_admin(user=Depends(require_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )
    return user


def flash(request, message: str):
    request.session["flash"] = message


def get_flash(request):
    return request.session.pop("flash", None)
