import os
import requests
from fastapi import HTTPException
from pydantic import ValidationError
from smolagents import CodeAgent, WebSearchTool, LiteLLMModel
from dotenv import load_dotenv

from agent_utils.schemas import (
    Scorer, Information, HexagonData,
    ScoreRequest, ScoreResponse, InformationRequest, InformationResponse,
    GridDataResponse, TemperatureDataResponse, NetworkDataResponse, FullDataResponse
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
    Returns a set of three weights (grid, network, temperature) for the requested
    French location and applies them to data to return ranked results.
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
        # Get the weights from the agent
        result = agent.run(query)
        validated = Scorer.model_validate(result)
        weights = validated.model_dump()
        
        # Fetch data from all three tables
        grid_data, _ = supabase_get("grid_data")
        network_data, _ = supabase_get("network_data") 
        temperature_data, _ = supabase_get("temperature_data")
        
        # Create dictionaries for faster lookup by id (assuming records have an 'id' field)
        grid_dict = {item.get('hexagon_id'): item for item in grid_data if item.get('hexagon_id')}
        network_dict = {item.get('hexagon_id'): item for item in network_data if item.get('hexagon_id')}
        temp_dict = {item.get('hexagon_id'): item for item in temperature_data if item.get('hexagon_id')}
        
        # Get all unique IDs
        all_ids = set(grid_dict.keys()) | set(network_dict.keys()) | set(temp_dict.keys())
        
        # Calculate aggregated scores and create hexagon data
        scored_data = []
        hexagon_data_dict = {}
        
        for record_id in all_ids:
            grid_record = grid_dict.get(record_id, {})
            network_record = network_dict.get(record_id, {})
            temp_record = temp_dict.get(record_id, {})
            
            # Get normalized scores, default to -1 if null/missing
            grid_norm = grid_record.get('connection_normalized_score', -1) if grid_record.get('connection_normalized_score') is not None else -1
            network_norm = network_record.get('latency_normalized_score', -1) if network_record.get('latency_normalized_score') is not None else -1
            temp_norm = temp_record.get('temperature_normalized_score', -1) if temp_record.get('temperature_normalized_score') is not None else -1
            
            # Calculate aggregated score
            aggregated_score = (
                weights['score_grid'] * grid_norm +
                weights['score_network'] * network_norm + 
                weights['score_temperature'] * temp_norm
            )
            
            # Normalize aggregated score to 0-1 range
            # Handle case where all normalized scores are -1 (missing data)
            if grid_norm == -1 and network_norm == -1 and temp_norm == -1:
                normalized_aggregated_score = 0.0
            else:
                # For valid scores, normalize from [-1,1] to [0,1] range
                normalized_aggregated_score = max(0, min(1, (aggregated_score + 1) / 2))
            
            # Create HexagonData for this hexagon
            hexagon_data_dict[record_id] = HexagonData(
                score=normalized_aggregated_score,
                connection_points=grid_record.get('connection_points'),
                latency_ms=network_record.get('latency_ms'),
                avg_temperature=temp_record.get('avg_temperature'),
                connection_normalized_score=grid_record.get('connection_normalized_score'),
                latency_normalized_score=network_record.get('latency_normalized_score'),
                temperature_normalized_score=temp_record.get('temperature_normalized_score')
            )
            
            scored_data.append({
                'hexagon_id': record_id,
                'aggregated_score': aggregated_score
            })
        
        # Rank data by aggregated score (highest first)
        ranked_data = sorted(scored_data, key=lambda x: x['aggregated_score'], reverse=True)
        
        # Get top 5 hexagon IDs for highlighting
        top_hexagons = [item['hexagon_id'] for item in ranked_data[:5]]
        
        # Create response message
        response_message = "These are the top 5 data center locations, based on my computations:\n"
        for i, item in enumerate(ranked_data[:5], 1):
            response_message += f"- hexagon id {item['hexagon_id']}\n"
        response_message += "\nDo you want me to elaborate on them?"
        
        return InformationResponse(
            response=response_message,
            hexagonData=hexagon_data_dict,
            highlighted=top_hexagons
        )
        
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


def get_full_data():
    """
    Returns all data from grid_data, network_data, and temperature_data tables
    in a combined dictionary format.
    """
    try:
        # Get data from all three tables
        grid_data, _ = supabase_get("grid_data")
        network_data, _ = supabase_get("network_data")
        temperature_data, _ = supabase_get("temperature_data")
        
        return FullDataResponse(
            grid_data=grid_data,
            network_data=network_data,
            temperature_data=temperature_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching full data: {e}") from e 
    
