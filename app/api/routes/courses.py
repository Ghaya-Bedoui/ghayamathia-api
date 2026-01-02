from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.course import Course
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseOut,
)

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)


@router.get("", response_model=list[CourseOut])
def list_courses(
    published_only: bool = True,
    db: Session = Depends(get_db),
):
    query = db.query(Course)

    if published_only:
        query = query.filter(Course.published == True)  # noqa: E712

    return query.order_by(Course.id.desc()).all()


@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    return course


@router.post(
    "",
    response_model=CourseOut,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
):
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.patch(
    "/{course_id}",
    response_model=CourseOut,
    dependencies=[Depends(require_admin)],
)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


@router.delete(
    "/{course_id}",
    status_code=204,
    dependencies=[Depends(require_admin)],
)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    db.delete(course)
    db.commit()
    return None
