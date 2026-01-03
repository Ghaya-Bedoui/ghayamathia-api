from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.deps import get_db
from app.models.course import Course
from app.api.routes import auth, courses

app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(auth.router)
app.include_router(courses.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    courses = (
        db.query(Course)
        .filter(Course.published == True)
        .order_by(Course.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "courses": courses},
    )
