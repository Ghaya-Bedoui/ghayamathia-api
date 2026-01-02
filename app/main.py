from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.core.config import settings
from app.api.routes import auth_router, courses_router
from app.db.session import SessionLocal
from app.db.init_db import ensure_admin

app = FastAPI(
    title=settings.APP_NAME,
)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


app.include_router(auth_router)
app.include_router(courses_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        ensure_admin(db)
    finally:
        db.close()
