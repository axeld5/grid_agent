def generate_scoring_prompt(french_location: str, schema_str: str) -> str:
    """Generate the prompt for scoring grid, water, and elevation weights.
    
    Args:
        french_location: The French location for the data center
        schema_str: JSON schema string for validation
        
    Returns:
        str: The formatted prompt
    """
    return f"""I want to build a data center in {french_location}, France.
I need to assign a weight to value of grid, water and elevation.
Make a small model. Make sure the sum is 1.
Match this json schema: {schema_str}
Return only JSON that matches the schema. If you compute intermediate things, do not include them—just the final JSON.
Use the `return_scores` tool to validate the final object."""


def generate_information_prompt(french_location: str, schema_str: str) -> str:
    """Generate the prompt for gathering datacenter installation information.
    
    Args:
        french_location: The French location for the data center
        schema_str: JSON schema string for validation
        
    Returns:
        str: The formatted prompt
    """
    return f"""I am a foreigner who wants to install a data center in France.
I heard some things about France.
Location can be tough due to people being "not in my backyard".
Installation can be tough due to regulatory issues.
My team has mapped {french_location} as the place for installation of that data center.
Fill this data in the following json schema: {schema_str}
When it comes to the data, it needs to be sourced. Do not state a "potential risk", state a risk that has occurred for similar projects.
Use the `return_information` tool to validate the final object.""" 