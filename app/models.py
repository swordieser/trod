import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class FundTagEnum(enum.Enum):
    ANIMALS = "Животные"
    CULTURE = "Культура"
    NATURE = "Природа"
    CHILDREN = "Дети"
    ADULTS = "Взрослые"
    ELDERS = "Пожилые"


class Tags(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)


class FundTags(Base):
    __tablename__ = "fund_tags"

    fund_id = Column(ForeignKey("funds.id"), primary_key=True)
    tag_id = Column(ForeignKey("tags.id"), primary_key=True)


class Fund(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    total_collected = Column(Integer, default=0)
    phone = Column(String, nullable=True)
    url = Column(String, nullable=True)

    projects = relationship("Project", back_populates="fund")
    tags = relationship(
        "FundTags",
        lazy="subquery",
        backref="funds",
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    goal_amount = Column(Integer)
    collected_amount = Column(Integer, default=0)
    city = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    main_text = Column(String, nullable=True)

    fund_id = Column(Integer, ForeignKey("funds.id"))
    fund = relationship("Fund", back_populates="projects")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False
    )

    donations = relationship("Donation", back_populates="user")


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    fund_id = Column(Integer, ForeignKey("funds.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    user = relationship("User", back_populates="donations")
    fund = relationship("Fund")
    project = relationship("Project")
