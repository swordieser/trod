from fastapi import APIRouter
from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import flash, get_flash
from app.models import User, UserRole
from app.templates import templates

router = APIRouter(prefix="/auth")


@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    message = get_flash(request)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": message
        }
    )


@router.post("/login")
def login_post(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        flash(
            request,
            "Неверное имя пользователя или пароль"
        )
        return RedirectResponse("/auth/login", status_code=303)

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = User(
        username=username,
        password_hash=bcrypt.hash(password),
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    return RedirectResponse("/auth/login", status_code=303)
