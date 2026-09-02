"""POST /recommend e /recommend_playlist."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.schemas import PlaylistRecommendationRequest, RecommendationRequest
from services.recommend_service import ensure_track_in_db, find_similar, recommend_for_playlist

router = APIRouter()


@router.post("/recommend")
def recommend_unified(req: RecommendationRequest, db: Session = Depends(get_db)):
    track = ensure_track_in_db(db, req.track_id)
    return find_similar(db, track, req.top_n)


@router.post("/recommend_playlist")
def recommend_playlist(req: PlaylistRecommendationRequest, db: Session = Depends(get_db)):
    return recommend_for_playlist(db, req.track_ids, req.top_n)
