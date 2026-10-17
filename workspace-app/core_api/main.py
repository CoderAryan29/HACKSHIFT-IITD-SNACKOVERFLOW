
from datetime import datetime, timezone

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from core_api.api.market import router as market_router
from core_api.api.prices import router as prices_router
from core_api.db.session import get_db

app = FastAPI(
    title="KisanSetu API",
    description="Backend API for agricultural assistance.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to KisanSetu API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "kisansetu-core-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
    }


app.include_router(prices_router)
app.include_router(market_router)
