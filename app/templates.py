from fastapi.templating import Jinja2Templates
from app.models import UserRole

templates = Jinja2Templates(directory="templates")

templates.env.globals["is_admin"] = lambda user: user and user.role == UserRole.ADMIN
templates.env.globals["current_user"] = lambda request: request.state.user
