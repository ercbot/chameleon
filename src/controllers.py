import os

from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage


def player_input(prompt):
    # even though they are human, we still need to return an AIMessage, since the HumanMessages are from the GameMaster
    response = AIMessage(content=input())
    return response

MAX_TOKENS = 20

def controller_from_name(name: str):
    if name == "tgi":
        return ChatOpenAI(
            api_base=os.environ['HF_ENDPOINT_URL'] + "/v1/",
            api_key=os.environ['HF_API_TOKEN']
        )
    elif name == "openai":
        return ChatOpenAI(model="gpt-3.5-turbo", max_tokens=MAX_TOKENS)
    elif name == "ollama":
        return ChatOpenAI(model="mistral", openai_api_key="ollama", openai_api_base="http://localhost:11434/v1", max_tokens=MAX_TOKENS)
    elif name == "human":
        return RunnableLambda(player_input)
    else:
        raise ValueError(f"Unknown controller name: {name}")