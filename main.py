from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from app.database import get_db, SessionLocal
import logging
from app.auth import require_user
from app.startup import create_admin_if_not_exists
from app.templates import templates
from routes import *
from app.models import User

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Charity Aggregator")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(funds_router)
app.include_router(projects_router)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_admin_if_not_exists(db)
    finally:
        db.close()


@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    request.state.user = None
    db = SessionLocal()

    user_id = request.session.get("user_id")
    if user_id:
        try:
            request.state.user = db.query(User).get(user_id)
        finally:
            db.close()

    response = await call_next(request)
    return response


# self.add_middleware(BaseHTTPMiddleware, dispatch=func) ?
@app.middleware("http")
async def add_session_to_request(request: Request, call_next):
    response = await call_next(request)
    session = request.cookies.get('session')
    if session:
        response.set_cookie(key='session', value=request.cookies.get('session'), httponly=True)
    return response


app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_KEY"
)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "home.html", 
        {"request": request}
    )

#@app.get("/", response_class=HTMLResponse)
#def home(request: Request, db: Session = Depends(get_db)):
#    return templates.TemplateResponse(
#        "base.html",
#        {"request": request}
#    )


@app.get("/my-donations", response_class=HTMLResponse)
def my_donations(
        request: Request,
        user=Depends(require_user),
        db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "donations.html",
        {
            "request": request,
            "donations": user.donations
        }
    )
