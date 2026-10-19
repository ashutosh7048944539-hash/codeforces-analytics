from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.database import engine
from app.routers.analytics import router as analytics_router
from app.routers.recommendations import (
    router as recommendations_router,
)


templates = Jinja2Templates(
    directory="templates"
)


app = FastAPI(
    title="Codeforces Analytics & Practice Recommender",
    version="0.1.0",
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


app.include_router(analytics_router)
app.include_router(recommendations_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }