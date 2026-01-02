from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import settings
from app.core.security import hash_password


def ensure_admin(db: Session) -> None:
    """
    Crée ou met à jour le compte admin au démarrage
    selon les valeurs dans .env
    """
    admin = db.query(User).filter(
        User.email == settings.ADMIN_EMAIL
    ).first()

    if admin:
        admin.hashed_password = hash_password(settings.ADMIN_PASSWORD)
        admin.role = "admin"
        admin.is_active = True
        db.commit()
        return

    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )

    db.add(admin)
    db.commit()
