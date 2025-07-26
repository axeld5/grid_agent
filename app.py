import os
from fastapi import FastAPI
from dotenv import load_dotenv

from agent_utils.schemas import ScoreResponse, InformationResponse
from endpoints import score, information


# ---- FastAPI setup ----
load_dotenv()  # Load keys like ANTHROPIC_API_KEY (used by LiteLLM) and any web-search keys required by WebSearchTool

app = FastAPI(title="Datacenter Weighting API", version="1.0.0")


# ---- Route registration ----
app.post("/score", response_model=ScoreResponse, summary="Get grid/water/elevation weights for a French location")(score)
app.post("/information", response_model=InformationResponse, summary="Get datacenter installation information for a French location")(information)


# ---- Local dev runner ----
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )