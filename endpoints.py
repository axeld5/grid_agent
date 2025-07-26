import os
import requests
from fastapi import HTTPException
from pydantic import ValidationError
from smolagents import CodeAgent, WebSearchTool, LiteLLMModel
from dotenv import load_dotenv

from agent_utils.schemas import (
    Scorer, Information,
    ScoreRequest, InformationRequest, InformationResponse,
    GridDataResponse, TemperatureDataResponse, NetworkDataResponse
)
from agent_utils.prompts import generate_scoring_prompt, generate_information_prompt
from agent_utils.tools import return_scores, return_information

# Load environment variables
load_dotenv()

# Configuration via env, with sensible defaults
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "anthropic/claude-sonnet-4-20250514")
STREAM_OUTPUTS = os.getenv("STREAM_OUTPUTS", "false").lower() == "true"

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")


def supabase_get(table, select="*"):
    """
    Generic function to get data from Supabase tables.
    
    Args:
        table: Name of the table to query
        select: Fields to select (default: "*")
    
    Returns:
        tuple: (data, total_count)
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
        )
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = [("select", select)]

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Accept": "application/json",
        "Prefer": "count=exact"  # returns Content-Range header with total
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        total = resp.headers.get("Content-Range")  # e.g. "0-9/123"
        return resp.json(), total
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from Supabase: {e}") from e


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
    
    # Generate the prompt using the dedicated function
    schema_str = Scorer.model_json_schema()
    query = generate_scoring_prompt(req.message, schema_str)
    
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
    model = LiteLLMModel(model_id=DEFAULT_MODEL_ID)

    agent = CodeAgent(
        tools=[WebSearchTool(), return_information],
        model=model,
        stream_outputs=STREAM_OUTPUTS,
    )
    
    # Generate the prompt using the dedicated function
    info_schema_str = Information.model_json_schema()
    query = generate_information_prompt(req.message, info_schema_str)
    
    try:
        result = agent.run(query)
        validated = Information.model_validate(result)
        data = validated.model_dump()
        
        # Format the response as requested
        formatted_response = "Here are the informations you need to be wary of.\n\n"
        
        for schema_key, schema_value in data.items():
            formatted_response += f"## {schema_key.capitalize()}\n\n"
            if isinstance(schema_value, list):
                for item in schema_value:
                    formatted_response += f"- {item}\n"
            else:
                formatted_response += f"{schema_value}\n"
            formatted_response += "\n"
        return InformationResponse(response=formatted_response.strip())
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {ve}") from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}") from e


# ---- Data endpoints ----
def get_grid_data():
    """
    Returns all grid data from the grid_data table.
    """
    try:
        data, total_count = supabase_get("grid_data")
        return GridDataResponse(data=data, total_count=total_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching grid data: {e}") from e


def get_temperature_data():
    """
    Returns all temperature data from the temperature_data table.
    """
    try:
        data, total_count = supabase_get("temperature_data")
        return TemperatureDataResponse(data=data, total_count=total_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching temperature data: {e}") from e


def get_network_data():
    """
    Returns all network data from the network_data table.
    """
    try:
        data, total_count = supabase_get("network_data")
        return NetworkDataResponse(data=data, total_count=total_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching network data: {e}") from e 