from typing import Optional, Dict, Any
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


class CurrentView(BaseModel):
    lat: float
    lng: float
    zoom: float


class Context(BaseModel):
    currentView: CurrentView


class InformationRequest(BaseModel):
    message: str
    context: Optional[Context] = None


class HexagonData(BaseModel):
    score: float  # 0-1 for color mapping
    internetSpeed: Optional[float] = None
    gridDistance: Optional[float] = None
    nbGridConnections: Optional[float] = None
    avgTemp: Optional[float] = None
    
    internetSpeedNorm: Optional[float] = None
    gridDistanceNorm: Optional[float] = None
    nbGridConnectionsNorm: Optional[float] = None
    avgTempNorm: Optional[float] = None
    
    opposition: Optional[str] = None  # "low" | "medium" | "high"


class InformationResponse(BaseModel):
    """The validated information is the response body.""" 
    response: str
    hexagonData: Optional[Dict[str, HexagonData]] = None
    highlighted: Optional[list[str]] = None  # H3 IDs to emphasize