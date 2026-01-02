from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
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
def root():
    return {
        "name": "Ghayamathia API",
        "docs": "/docs",
        "health": "/health",
    }
