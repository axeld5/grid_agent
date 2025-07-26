from typing import Type, Any
from pydantic import BaseModel, ValidationError

from dotenv import load_dotenv

from smolagents import CodeAgent, WebSearchTool, LiteLLMModel, tool

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

schema_str = Scorer.model_json_schema()


if __name__ == "__main__":
    load_dotenv()

    model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-20250514")
    agent = CodeAgent(
        tools=[WebSearchTool(), return_scores], 
        model=model,
        stream_outputs=True
    )

    # Specify your French location here
    french_location = "Fresnay-sur-Sarthe"  # Change this to your specific location in France

    query = f"""I want to build a data center in {french_location}, France.
    I need to assign a weight to value of grid, water and elevation.
    Make a small model. Make sure the sum is 1.
    Match this json schema: {schema_str}
    """

    result = agent.run(query)
    final_answer = Scorer.model_validate(result).model_dump()
    print(final_answer)