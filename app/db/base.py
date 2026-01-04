# app/db/base.py
from app.db.base_class import Base  # noqa

#  Import des models uniquement pour qu'Alembic les "voie"
from app.models.user import User  # noqa
from app.models.course import Course  # noqa
from app.models.enrollment import Enrollment  # noqa
