from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
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
    return likely_animals_chain.run(animal_description=description)

tools = [
    Tool(
        name='get_likely_animals',
        func=get_likely_animals,
        description='used to get a list of potential animals corresponding to a description of an animal'
    )
]