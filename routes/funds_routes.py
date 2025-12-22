from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Donation, Fund, FundTagEnum
from app import crud
from app.auth import require_admin
from app.templates import templates

router = APIRouter(prefix="/funds")


@router.get("/", response_class=HTMLResponse)
def get_funds(request: Request, db: Session = Depends(get_db), tag: str | None = None):
    funds = crud.get_funds(db, tag)
    return templates.TemplateResponse(
        "funds.html",
        {"request": request, "funds": funds, "tags": FundTagEnum}
    )


@router.get("/{fund_id}/donors", response_class=HTMLResponse)
def fund_donors(
        fund_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    donations = (
        db.query(Donation)
        .filter(Donation.fund_id == fund_id)
        .order_by(Donation.created_at.desc())
        .all()
    )

    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    return templates.TemplateResponse(
        "fund_donors.html",
        {"request": request, "donations": donations, "fund": fund}
    )
