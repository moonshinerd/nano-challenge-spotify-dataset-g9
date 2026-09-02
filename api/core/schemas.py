"""Schemas Pydantic dos payloads de request. As respostas continuam como
dict simples nos routers (sem response_model) de propósito: os valores vêm
de cálculos com numpy/pgvector (ex.: np.float64) e forçar um response_model
estrito arriscaria mudar a serialização atual sem necessidade."""
from typing import List

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    track_id: str
    top_n: int = 5


class PlaylistRecommendationRequest(BaseModel):
    track_ids: List[str]
    top_n: int = 10


class AnalyzeRequest(BaseModel):
    query: str
    top_n: int = 5
