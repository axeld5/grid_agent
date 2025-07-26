from pydantic import BaseModel, ValidationError

from dotenv import load_dotenv

from smolagents import CodeAgent, WebSearchTool, LiteLLMModel, tool

class Information(BaseModel):
    legislation: list[str]
    construction_opposition: list[str]
    environmental_challenges: list[str]

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
        return Information.model_validate(payload).model_dump()
    except ValidationError as e:
        return {"error": f"Schema validation failed: {e}"}

if __name__ == "__main__":
    load_dotenv()

    model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-20250514")
    agent = CodeAgent(tools=[WebSearchTool()], model=model, stream_outputs=True)

    # Specify your French location here
    french_location = "Fresnay-sur-Sarthe"  # Change this to your specific location in France

    query = f"""I am a foreigner who whants to install a data center in France.
    I heard some things about France.
    Location can be tough due to people being "not in my backyard".
    Installation can be tough due to regulatory issues.
    My team has mapped {french_location} as the place for installation of that data center.
    Fill this data in the following json schema: {Information.model_json_schema()}
    When it comes to the data, it needs to be sourced. Do not state a "potential risk", state a risk that has occurred for similar projects.
    """

    result = agent.run(query)
    final_answer = Information.model_validate(result).model_dump()
    print(final_answer)