from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func, UniqueConstraint
from app.db.base import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending/accepted/rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),)
