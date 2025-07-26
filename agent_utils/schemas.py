from typing import Optional
from pydantic import BaseModel


# ---- Domain models ----
class Scorer(BaseModel):
    score_grid: float
    score_water: float
    score_elevation: float


class Information(BaseModel):
    legislation: list[str]
    construction_opposition: list[str]
    environmental_challenges: list[str]


# ---- Request/Response models ----
class ScoreRequest(BaseModel):
    french_location: str
    # Optional: override the model on a per-request basis
    model_id: Optional[str] = None


class ScoreResponse(Scorer):
    """The validated weights are the response body."""


class InformationRequest(BaseModel):
    french_location: str
    # Optional: override the model on a per-request basis
    model_id: Optional[str] = None


class InformationResponse(Information):
    """The validated information is the response body.""" 