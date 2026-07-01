from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud, auth

router = APIRouter(prefix="/api/stats", tags=["stats"])

def get_current_user(session_id: str = Query(...)):
    user_id = auth.get_user_id_from_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user_id

@router.get("/overview", response_model=schemas.StatsOverview)
def get_stats_overview(
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    stats = crud.get_stats_overview(db, user_id)
    return stats