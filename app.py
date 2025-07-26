import os
from fastapi import FastAPI
from dotenv import load_dotenv

from agent_utils.schemas import (
    ScoreResponse, InformationResponse,
    GridDataResponse, TemperatureDataResponse, NetworkDataResponse
)
from endpoints import (
    score, information,
    get_grid_data, get_temperature_data, get_network_data
)


# ---- FastAPI setup ----
load_dotenv()  # Load keys like ANTHROPIC_API_KEY (used by LiteLLM) and any web-search keys required by WebSearchTool

app = FastAPI(title="Datacenter Weighting API", version="1.0.0")


# ---- Route registration ----
app.post("/score", response_model=ScoreResponse, summary="Get grid/water/elevation weights for a French location")(score)
app.post("/information", response_model=InformationResponse, summary="Get datacenter installation information for a French location")(information)

# Data endpoints
app.get("/data/grid", response_model=GridDataResponse, summary="Get all grid data")(get_grid_data)
app.get("/data/temperature", response_model=TemperatureDataResponse, summary="Get all temperature data")(get_temperature_data)
app.get("/data/network", response_model=NetworkDataResponse, summary="Get all network data")(get_network_data)


# ---- Local dev runner ----
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )