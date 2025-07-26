from pydantic import ValidationError
from smolagents import tool
from agent_utils.schemas import Scorer, Information


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


@tool
def return_information(payload: dict) -> dict:
    """Validate and return the information object.

    Args:
        payload: dict input from the agent

    Returns:
        dict: The validated and returned object

    Raises:
        ValidationError: If the payload does not match the schema
    """
    try:
        return Information.model_validate(payload).model_dump()
    except ValidationError as e:
        return {"error": f"Schema validation failed: {e}"} 