import os
from fastapi import HTTPException
from pydantic import ValidationError
from smolagents import CodeAgent, WebSearchTool, LiteLLMModel

from agent_utils.schemas import (
    Scorer, Information,
    ScoreRequest, InformationRequest
)
from agent_utils.prompts import generate_scoring_prompt, generate_information_prompt
from agent_utils.tools import return_scores, return_information

# Configuration via env, with sensible defaults
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "anthropic/claude-sonnet-4-20250514")
STREAM_OUTPUTS = os.getenv("STREAM_OUTPUTS", "false").lower() == "true"


def score(req: ScoreRequest):
    """
    Returns a set of three weights (grid, water, elevation) for the requested
    French location. The three scores always sum to 1.0 and conform to the Scorer schema.
    """
    # Create the model + agent per request for thread-safety
    model = LiteLLMModel(model_id=req.model_id or DEFAULT_MODEL_ID)

    agent = CodeAgent(
        tools=[WebSearchTool(), return_scores],
        model=model,
        stream_outputs=STREAM_OUTPUTS,
    )
    
    # Generate the prompt using the dedicated function
    schema_str = Scorer.model_json_schema()
    query = generate_scoring_prompt(req.french_location, schema_str)
    
    try:
        result = agent.run(query)
        validated = Scorer.model_validate(result)
        return validated.model_dump()
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {ve}") from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}") from e


def information(req: InformationRequest):
    """
    Returns information about legislation, construction opposition, and environmental challenges
    for installing a data center in the specified French location.
    """
    # Create the model + agent per request for thread-safety
    model = LiteLLMModel(model_id=req.model_id or DEFAULT_MODEL_ID)

    agent = CodeAgent(
        tools=[WebSearchTool(), return_information],
        model=model,
        stream_outputs=STREAM_OUTPUTS,
    )
    
    # Generate the prompt using the dedicated function
    info_schema_str = Information.model_json_schema()
    query = generate_information_prompt(req.french_location, info_schema_str)
    
    try:
        result = agent.run(query)
        validated = Information.model_validate(result)
        return validated.model_dump()
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {ve}") from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}") from e 