from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User
from app.api.deps import get_current_user, require_admin
from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut, EnrollmentUpdate

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@router.post("", response_model=EnrollmentOut)
def create_enrollment(payload: EnrollmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == payload.course_id, Course.published == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.course_id == payload.course_id).first()
    if existing:
        return existing

    e = Enrollment(user_id=user.id, course_id=payload.course_id, status="pending")
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

@router.get("/me", response_model=list[EnrollmentOut])
def my_enrollments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Enrollment).filter(Enrollment.user_id == user.id).order_by(Enrollment.id.desc()).all()

@router.get("/admin", response_model=list[EnrollmentOut])
def admin_list(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Enrollment).order_by(Enrollment.id.desc()).all()

@router.patch("/admin/{enrollment_id}", response_model=EnrollmentOut)
def admin_update(enrollment_id: int, payload: EnrollmentUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    e = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    if payload.status not in ("pending", "accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")
    e.status = payload.status
    db.commit()
    db.refresh(e)
    return e
