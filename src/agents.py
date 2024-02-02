from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

from langchain.prompts import PromptTemplate
from reasoning_tools import animal_tools, extract_vote

# LLM Configuration for each role
llm_parameters = {
        "chameleon": {
            'model': 'gpt-4-turbo-preview',
            'temperature': 1
        },
        "herd": {
            'model': 'gpt-3.5-turbo',
            'temperature': 1
        },
        "judge": {
            'model': 'gpt-3.5-turbo',
            'temperature': 1
        }
}

prompt = hub.pull("hwchase17/openai-functions-agent")


class PlayerAgent(AgentExecutor):

    def __init__(self, role):
        llm = ChatOpenAI(**llm_parameters[role])

        agent = create_openai_functions_agent(llm, animal_tools, prompt)

        super().__init__(agent=agent, tools=animal_tools, verbose=True, return_intermediate_steps=True)
