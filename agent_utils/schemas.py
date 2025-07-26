from typing import Optional, Dict, Any
from pydantic import BaseModel


# ---- Domain models ----
class Scorer(BaseModel):
    score_grid: float
    score_temperature: float
    score_network: float


class Information(BaseModel):
    legislation: list[str]
    construction_opposition: list[str]
    environmental_challenges: list[str]


# ---- Request/Response models ----
class ScoreRequest(BaseModel):
    message: str


class ScoreResponse(BaseModel):
    """Response containing weights and ranked data."""
    score_grid: float
    score_temperature: float
    score_network: float
    ranked_data: list[Dict[str, Any]]


class InformationRequest(BaseModel):
    message: str
    additional_context: Optional[str] = None
    highlighted: Optional[dict[str, float]] = None


class HexagonData(BaseModel):
    score: float  # 0-1 for color mapping
    
    connection_points: Optional[float] = None
    latency_ms: Optional[float] = None
    avg_temperature: Optional[float] = None
    
    connection_normalized_score: Optional[float] = None
    latency_normalized_score: Optional[float] = None
    temperature_normalized_score: Optional[float] = None


class InformationResponse(BaseModel):
    """The validated information is the response body.""" 
    response: str
    hexagonData: Optional[Dict[str, HexagonData]] = None
    highlighted: Optional[dict[str, float]] = None  # H3 IDs to emphasize


# ---- Data table response models ----
class DataResponse(BaseModel):
    """Generic response for data table queries."""
    data: list[Dict[str, Any]]
    total_count: Optional[str] = None


class GridDataResponse(DataResponse):
    """Response for grid data table."""
    pass


class TemperatureDataResponse(DataResponse):
    """Response for temperature data table."""
    pass


class NetworkDataResponse(DataResponse):
    """Response for network data table."""
    pass


class FullDataResponse(BaseModel):
    """Response for combined data from all tables."""
    grid_data: list[Dict[str, Any]]
    network_data: list[Dict[str, Any]]
    temperature_data: list[Dict[str, Any]]