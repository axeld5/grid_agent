def generate_scoring_prompt(user_query: str, schema_str: str) -> str:
    """Generate the prompt for scoring grid, water, and elevation weights.
    
    Args:
        user_query: The user query
        schema_str: JSON schema string for validation
        
    Returns:
        str: The formatted prompt
    """
    return f"""Given the following user query: <user_query>
{user_query}
</user_query>
I need to assign a weight to specific values.
Make a small model. Make sure the sum is 1.
Match this json schema: {schema_str}
Return only JSON that matches the schema. If you compute intermediate things, do not include them—just the final JSON.
Use the `return_scores` tool to validate the final object."""


def generate_information_prompt(user_query: str, schema_str: str) -> str:
    """Generate the prompt for gathering datacenter installation information.
    
    Args:
        french_location: The French location for the data center
        schema_str: JSON schema string for validation
        
    Returns:
        str: The formatted prompt
    """
    return f"""I am a foreigner who wants to install data centersin France.
I heard some things about France.
Location can be tough due to people being "not in my backyard".
Installation can be tough due to regulatory issues.
My team has sent me this message with respect to their mapping of french locations: <user_query>
{user_query}
</user_query>
Fill this data in the following json schema: {schema_str}
When it comes to the data, it needs to be sourced. Do not state a "potential risk", state a risk that has occurred for similar projects.
Make the risks as specific as possible with respect to the locations. Be as specific as possible.
Use the `return_information` tool to validate the final object.""" 