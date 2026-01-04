from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.deps import get_db, get_current_user, require_admin
from app.api.routes import auth, courses, enrollments
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User
from app.content.projects import PROJECTS
from app.core.security import verify_password, create_access_token, hash_password
from app.web.utils import set_auth_cookie, clear_auth_cookie

app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",  # ✅ OpenAPI sous /api
)

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ API sous /api
app.include_router(auth.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(enrollments.router, prefix="/api")

# -------------------------
# HEALTH
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# SITE PUBLIC
# -------------------------
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    published_courses = (
        db.query(Course)
        .filter(Course.published == True)
        .order_by(Course.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "page_title": "Ghayamathia — Ghaya Bedoui",
            "courses": published_courses,
            "projects": PROJECTS,
            "published_count": len(published_courses),
        },
    )

@app.get("/courses")
def courses_page(request: Request, db: Session = Depends(get_db)):
    courses_list = (
        db.query(Course)
        .filter(Course.published == True)
        .order_by(Course.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        "courses_list.html",
        {"request": request, "courses": courses_list},
    )

@app.get("/courses/{course_id}")
def course_detail_page(course_id: int, request: Request, db: Session = Depends(get_db)):
    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.published == True)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # utilisateur connecté ? (on ne force pas login ici)
    user = None
    try:
        user = get_current_user(request, db)  # type: ignore
    except Exception:
        user = None

    already_enrolled = False
    if user:
        already_enrolled = (
            db.query(Enrollment)
            .filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id)
            .first()
            is not None
        )

    return templates.TemplateResponse(
        "course_detail.html",
        {
            "request": request,
            "course": course,
            "user": user,
            "already_enrolled": already_enrolled,
        },
    )

# -------------------------
# AUTH WEB (PAGES)
# -------------------------
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth_login.html", {"request": request})

@app.post("/login")
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth_login.html",
            {"request": request, "error": "Email ou mot de passe incorrect."},
            status_code=401,
        )

    token = create_access_token(subject=user.email, role=user.role)
    response = RedirectResponse(url="/me", status_code=303)
    set_auth_cookie(response, token)
    return response

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("auth_register.html", {"request": request})

@app.post("/register")
def register_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        return templates.TemplateResponse(
            "auth_register.html",
            {"request": request, "error": "Cet email est déjà utilisé."},
            status_code=409,
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email, role=user.role)
    response = RedirectResponse(url="/me", status_code=303)
    set_auth_cookie(response, token)
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    clear_auth_cookie(response)
    return response

# -------------------------
# ESPACE ELEVE
# -------------------------
@app.get("/me")
def me_dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    my_enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id)
        .order_by(Enrollment.id.desc())
        .all()
    )
    # récupérer les cours liés
    course_ids = [e.course_id for e in my_enrollments]
    courses_map = {}
    if course_ids:
        cs = db.query(Course).filter(Course.id.in_(course_ids)).all()
        courses_map = {c.id: c for c in cs}

    return templates.TemplateResponse(
        "me_dashboard.html",
        {
            "request": request,
            "user": user,
            "enrollments": my_enrollments,
            "courses_map": courses_map,
        },
    )

@app.post("/courses/{course_id}/enroll")
def enroll_from_site(
    course_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id, Course.published == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user.id, Enrollment.course_id == course_id
    ).first()
    if existing:
        return RedirectResponse(url=f"/courses/{course_id}", status_code=303)

    enr = Enrollment(user_id=user.id, course_id=course_id, status="pending")
    db.add(enr)
    db.commit()

    return RedirectResponse(url="/me", status_code=303)

# -------------------------
# ADMIN BACK-OFFICE
# -------------------------
@app.get("/admin")
def admin_dashboard(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    pending_count = db.query(Enrollment).filter(Enrollment.status == "pending").count()
    courses_count = db.query(Course).count()
    users_count = db.query(User).count()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "admin": admin,
            "pending_count": pending_count,
            "courses_count": courses_count,
            "users_count": users_count,
        },
    )

@app.get("/admin/courses")
def admin_courses(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    all_courses = db.query(Course).order_by(Course.id.desc()).all()
    return templates.TemplateResponse(
        "admin_courses.html",
        {"request": request, "admin": admin, "courses": all_courses},
    )

@app.get("/admin/courses/new")
def admin_course_new(request: Request, admin: User = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin_course_form.html",
        {"request": request, "admin": admin, "mode": "create", "course": None},
    )

@app.post("/admin/courses/new")
def admin_course_create(
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(""),
    level: str = Form(""),
    duration_minutes: int = Form(...),
    price_eur: int = Form(...),
    published: str = Form("false"),
):
    c = Course(
        title=title,
        description=description,
        level=level,
        duration_minutes=duration_minutes,
        price_eur=price_eur,
        published=(published == "true"),
    )
    db.add(c)
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)

@app.get("/admin/courses/{course_id}/edit")
def admin_course_edit(course_id: int, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return templates.TemplateResponse(
        "admin_course_form.html",
        {"request": request, "admin": admin, "mode": "edit", "course": course},
    )

@app.post("/admin/courses/{course_id}/edit")
def admin_course_update(
    course_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(""),
    level: str = Form(""),
    duration_minutes: int = Form(...),
    price_eur: int = Form(...),
    published: str = Form("false"),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.title = title
    course.description = description
    course.level = level
    course.duration_minutes = duration_minutes
    course.price_eur = price_eur
    course.published = (published == "true")
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)

@app.post("/admin/courses/{course_id}/delete")
def admin_course_delete(course_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)

@app.get("/admin/enrollments")
def admin_enrollments(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    ens = db.query(Enrollment).order_by(Enrollment.id.desc()).all()

    user_ids = list({e.user_id for e in ens})
    course_ids = list({e.course_id for e in ens})

    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    courses_ = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []

    users_map = {u.id: u for u in users}
    courses_map = {c.id: c for c in courses_}

    return templates.TemplateResponse(
        "admin_enrollments.html",
        {
            "request": request,
            "admin": admin,
            "enrollments": ens,
            "users_map": users_map,
            "courses_map": courses_map,
        },
    )

@app.post("/admin/enrollments/{enrollment_id}/set")
def admin_set_enrollment(
    enrollment_id: int,
    status_value: str = Form(...),  # accepted/rejected/pending
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    e = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    if status_value not in ("pending", "accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")
    e.status = status_value
    db.commit()
    return RedirectResponse(url="/admin/enrollments", status_code=303)
