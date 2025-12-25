from sqlalchemy.orm import Session
from app.models import Fund, Project, Donation, FundTags, Tags
from sqlalchemy import func

def get_funds(db: Session, tag: str | None = None):
    from sqlalchemy.orm import joinedload
    
    query = db.query(Fund).options(
        joinedload(Fund.tags),
        joinedload(Fund.projects)
    )

    if tag:
        query = (
            query
            .join(FundTags, onclause=(Fund.id == FundTags.fund_id))
            .join(Tags, onclause=(FundTags.tag_id == Tags.id))
            .filter(Tags.tag == tag)
        )

    funds = query.all()
    
    # Только считаем активные проекты, не трогаем total_collected
    for fund in funds:
        fund.active_projects_count = len(fund.projects)
    
    return funds


def get_tags(db: Session):
    query = db.query(Tags)
    return query.all()


def get_projects(db: Session, fund_id: int | None = None):
    query = db.query(Project)

    if fund_id is not None:
        query = query.filter(Project.fund_id == fund_id)
    
    return query.all()


def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def create_donation(db, user, project, amount):
    donation = Donation(
        user_id=user.id,
        fund_id=project.fund_id,
        project_id=project.id,
        amount=amount
    )
    db.add(donation)

    project.collected_amount += amount

    fund = project.fund
    fund.total_collected = (
        db.query(func.coalesce(func.sum(Donation.amount), 0))
        .filter(Donation.fund_id == fund.id)
        .scalar() or 0
    )

    db.commit()