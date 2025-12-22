from fastapi import APIRouter
from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.auth import require_user
from app.templates import templates

router = APIRouter(prefix="/projects")


@router.get("/", response_class=HTMLResponse)
def get_projects(
        request: Request,
        fund_id: int | None = None,
        db: Session = Depends(get_db)
):
    projects = crud.get_projects(db, fund_id)
    funds = crud.get_funds(db)
    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "projects": projects,
            "funds": funds,
            "selected_fund": fund_id,
        }
    )


@router.get("/{project_id}", response_class=HTMLResponse)
def project_detail(
        request: Request,
        project_id: int,
        db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "project": project}
    )


@router.post("/donate/{project_id}")
def donate(
        project_id: int,
        amount: int = Form(...),
        user=Depends(require_user),
        db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    crud.create_donation(db, user, project, amount)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)
