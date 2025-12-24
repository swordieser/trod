from sqlalchemy.orm import Session
from app.models import Fund, Project, Donation, FundTags, Tags


def get_funds(db: Session, tag: str | None = None):
    query = db.query(Fund)

    if tag:
        query = (
            query
            .join(FundTags, onclause=(Fund.id == FundTags.fund_id))
            .join(Tags, onclause=(FundTags.tag_id == Tags.id))
            .filter(Tags.tag == tag)
        )

    return query.all()


def get_tags(db: Session):
    query = db.query(Tags)
    return query.all()


def get_projects(db: Session, fund_id: int | None = None):
    query = db.query(Project)
    if fund_id:
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
    project.fund.total_collected += amount

    db.commit()
