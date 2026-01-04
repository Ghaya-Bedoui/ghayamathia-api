from sqlalchemy.orm import declarative_base

Base = declarative_base()

#  IMPORTANT: importer les models pour Alembic
from app.models.user import User  # noqa
from app.models.course import Course  # noqa
from app.models.enrollment import Enrollment  # noqa
