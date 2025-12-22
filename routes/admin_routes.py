from fastapi import APIRouter, HTTPException
from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import sqlalchemy as sa
from app.database import get_db
from app.models import Fund, Project, FundTags, FundTagEnum
from app import crud
from app.auth import require_admin
from app.templates import templates

router = APIRouter(prefix="/admin")


@router.get("/funds/new", response_class=HTMLResponse)
def fund_create_form(
        request: Request,
        admin=Depends(require_admin)
):
    return templates.TemplateResponse(
        "fund_form.html",
        {"request": request}
    )


@router.post("/funds/new")
def fund_create(
        name: str = Form(...),
        description: str = Form(...),
        phone: str | None = Form(...),
        url: str | None = Form(...),
        tags: list[str] = Form([]),
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
):
    fund = Fund(
        name=name,
        description=description,
        phone=phone,
        url=url
    )
    db.add(fund)
    db.flush()

    for tag in tags:
        db.execute(
            sa.insert(FundTags).values(
                fund_id=fund.id,
                tag=FundTagEnum(tag),
            )
        )

    db.commit()

    return RedirectResponse("/", status_code=303)


@router.get("/projects/new", response_class=HTMLResponse)
def project_create_form(
        request: Request,
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
):
    funds = db.query(Fund).all()

    return templates.TemplateResponse(
        "project_form.html",
        {
            "request": request,
            "funds": funds
        }
    )


@router.post("/projects/new")
def project_create(
        title: str = Form(...),
        description: str = Form(...),
        goal_amount: int = Form(...),
        fund_id: int = Form(...),
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
):
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        # защита от подмены fund_id
        raise HTTPException(status_code=400, detail="Фонд не найден")

    project = Project(
        title=title,
        description=description,
        goal_amount=goal_amount,
        fund_id=fund.id
    )
    db.add(project)
    db.commit()

    return RedirectResponse("/projects", status_code=303)
