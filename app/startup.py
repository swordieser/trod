from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from app.models import User, UserRole


def create_admin_if_not_exists(db: Session):
    admin_username = "admin"
    admin_password = "admin"

    admin = (
        db.query(User)
        .filter(User.role == UserRole.ADMIN)
        .first()
    )

    if admin:
        return  # админ уже есть

    admin = User(
        username=admin_username,
        password_hash=bcrypt.hash(admin_password),
        role=UserRole.ADMIN,
    )

    db.add(admin)
    db.commit()
