from typing import Optional

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

# smolagents imports
from smolagents import CodeAgent, WebSearchTool, LiteLLMModel, tool


# ---- Domain models ----
class Scorer(BaseModel):
    score_grid: float
    score_water: float
    score_elevation: float


@tool
def return_scores(payload: dict) -> dict:
    """Validate and return the final object.

    Args:
        payload: dict input from the agent

    Returns:
        dict: The validated and returned object

    Raises:
        ValidationError: If the payload does not match the schema
    """
    try:
        return Scorer.model_validate(payload).model_dump()
    except ValidationError as e:
        return {"error": f"Schema validation failed: {e}"}


# ---- FastAPI setup ----
load_dotenv()  # Load keys like ANTHROPIC_API_KEY (used by LiteLLM) and any web-search keys required by WebSearchTool

app = FastAPI(title="Datacenter Weighting API", version="1.0.0")

# Make schema available to the agent
schema_str = Scorer.model_json_schema()

# Configuration via env, with sensible defaults
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "anthropic/claude-sonnet-4-20250514")
STREAM_OUTPUTS = os.getenv("STREAM_OUTPUTS", "false").lower() == "true"


# ---- Request/Response models ----
class ScoreRequest(BaseModel):
    french_location: str
    # Optional: override the model on a per-request basis
    model_id: Optional[str] = None


class ScoreResponse(Scorer):
    """The validated weights are the response body."""


# ---- Endpoint ----
@app.post("/score", response_model=ScoreResponse, summary="Get grid/water/elevation weights for a French location")
def score(req: ScoreRequest):
    """
    Returns a set of three weights (grid, water, elevation) for the requested
    French location. The three scores always sum to 1.0 and conform to the Scorer schema.
    """
    # Create the model + agent per request for thread-safety
    model = LiteLLMModel(model_id=DEFAULT_MODEL_ID)

    agent = CodeAgent(
        tools=[WebSearchTool(), return_scores],
        model=model,
        stream_outputs=STREAM_OUTPUTS,
    )

    query = f"""I want to build a data center in {req.french_location}, France.
I need to assign a weight to value of grid, water and elevation.
Make a small model. Make sure the sum is 1.
Match this json schema: {schema_str}
Return only JSON that matches the schema. If you compute intermediate things, do not include them—just the final JSON.
Use the `return_scores` tool to validate the final object."""
    try:
        result = agent.run(query)

        # Ensure strict schema compliance regardless of what the agent returns
        validated = Scorer.model_validate(result)
        return validated.model_dump()
    except ValidationError as ve:
        # Agent returned data but it didn't match the schema
        raise HTTPException(status_code=400, detail=f"Validation error: {ve}") from ve
    except Exception as e:
        # Any other runtime/LLM/tool/web-search errors
        raise HTTPException(status_code=500, detail=f"Internal error: {e}") from e


# ---- Local dev runner ----
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",  # you can also run "app:app"
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )