from typing import Dict, Any

from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

tool_llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

# Tools
# Get Animals From Description
LIKELY_ANIMALS_PROMPT = """Given the following description of an animal, discuss what possible animals it could be referring to and reasons why. 
Animal Description:
{animal_description}
Possible Animals:
"""

likely_animals_prompt = PromptTemplate(
    input_variables=['animal_description'],
    template=LIKELY_ANIMALS_PROMPT
)

likely_animals_chain = LLMChain(llm=tool_llm, prompt=likely_animals_prompt)

def get_likely_animals(description: str) -> str:
    """Provides animals from a description"""
    return likely_animals_chain.invoke(input={'animal_description': description})['text']


# Animal Match Tool
ANIMAL_MATCH_PROMPT = """\
Consider whether the following animal matches with the description provided. Provide your logic for reaching the conclusion. 
ANIMAL:
{animal}
Description:
{description}
Your Thoughts:
"""

animal_match_template = PromptTemplate(
    input_variables=['animal', 'description'],
    template=ANIMAL_MATCH_PROMPT
)

animal_match_tool = LLMChain(llm=tool_llm, prompt=likely_animals_prompt)


def does_animal_match_description(animal: str, description: str) -> dict[str, Any]:
    """Given an animal and a description, consider whether the animal matches that description"""
    return animal_match_tool.invoke(input={"animal": animal, "description": description})['text']


animal_tools = [
    Tool(
        name='get_likely_animals',
        func=get_likely_animals,
        description='used to get a list of potential animals corresponding to a description of an animal'
    )
]

VOTE_EXTRACTION_PROMPT = """Extract the name of the player being voted for, from the following statement:
{statement}"""

vote_extraction_template = PromptTemplate(
    input_variables=['statement'],
    template=VOTE_EXTRACTION_PROMPT
)

vote_extraction_chain = LLMChain(llm=tool_llm, prompt=vote_extraction_template)

def extract_vote(statement: str) -> str:
    """Extract the name of the player being voted for from the statement"""
    return vote_extraction_chain.invoke(input={"statement":statement})['text']