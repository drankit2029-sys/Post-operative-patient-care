from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.services.scheduler import scheduler

api_router = APIRouter(prefix="/v1")

@api_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    journal_mode = db.execute(text("PRAGMA journal_mode;")).scalar()
    return {
        "status": "healthy",
        "database": {
            "connected": True,
            "journal_mode": journal_mode
        },
        "scheduler_running": scheduler.running
    }
