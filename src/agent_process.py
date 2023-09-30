


"""Beginning of the round:
1. Assigned each player role
2. determine the order in which the players will speak"""


"""Describing Stage
THOUGHT STEP
Provide:
- Brief description of the game
- IF Herd:
    - The Animal the player is pretending to be
- ELSE IF Chameleon
    - Prompt that the player is the chameleon and doesn't know the answer but must pretend to know. 
- What each player before the current player has answered
Output:
- A Chain of Thought Style response thinking about what to respond

ACTION STEP
Provide: 
- All of the previous + the THOUGHT output
Output:
- A statement about the animal e.g. Respond("I am hairy")
"""

"""Voting Stage:
THOUGHT STEP
Provide:
- Brief description of the game
- IF Herd:
    - The Animal the player is pretending to be
- ELSE IF Chameleon
    - Prompt that the player is the chameleon they ought not to vote for themselves 
- What each player answered during the round
- A prompt instruction the agent to choose
Output:
- A Chain of Thought style response thinking about who would be best to vote for

ACTION STEP
Provide: 
- All of the previous + the THOUGHT output
- Instruction to vote for the player of their choice
Output:
- Another player's name as a choice of who to vote for e.g. Vote("Lisa")
"""


from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain

import random

herd_llm = ChatOpenAI(temperature=0.7)
chameleon_llm = ChatOpenAI(temperature=0.4)
decision_llm = ChatOpenAI(temperature=0)

# Game Setup
NUM_PLAYERS = 5
ANIMALS = ["Shark", "Tiger", "Owl", "Gorilla"]

selected_animal = random.choice(ANIMALS)
selected_chameleon = random.randint(0, NUM_PLAYERS - 1)

print(f'Animal: {selected_animal}')
print(f'Chameleon: Player {selected_chameleon}')

GAME_RULES = '''\
GAME RULES: You are playing a social deduction game where every player pretends the be the same animal. The players go around the room and make an "I"-statement as if they were the animal. All players know what animal they are pretending to be, except one who is known as the Chameleon. The Chameleon and must blend in by providing details about the animal using context from other players. The other players must be careful not to give away too much information with their responses so that Chameleon cannot guess the animal. After all players have spoken, they vote on who they think the Chameleon is. If the other players vote for the Chameleon, they win the game. If they vote for the wrong player then the Chameleon wins the game. 

'''

HERD_PROMPT = """You are a {animal}. In 10 words or less give a description of yourself starting with "I". Do not repeat responses from other players.
Previously Mentioned Descriptions: 
{player_responses}
Your Response:
"""

CHAMELEON_PROMPT = """You are the Chameleon. You don't know what animal the other players are. Using the context that they have provided, In 10 words or less give a description of yourself starting with "I". If no one else has said anything try to say something generic that could be true of any animals. 
Previously Mentioned Descriptions:
{player_responses}
Your Response:
"""

herd_prompt_template = PromptTemplate(
    input_variables=["animal", "player_responses"],
    template=GAME_RULES + HERD_PROMPT
)
chameleon_prompt_template = PromptTemplate(
    input_variables=["player_responses"],
    template=GAME_RULES + CHAMELEON_PROMPT
)

# Game chains
herd_chain = LLMChain(llm=herd_llm, prompt=herd_prompt_template)
chameleon_chain = LLMChain(llm=chameleon_llm, prompt=chameleon_prompt_template)
# chain = new_sequential_chain()

player_responses = []
for i in range(0, NUM_PLAYERS):
    if i == selected_chameleon:
        player_responses.append(chameleon_chain.run(player_responses=player_responses))
    else:
        player_responses.append(herd_chain.run(animal=selected_animal, player_responses=player_responses))
    print(f"Player {i}: {player_responses[i]}")
    player_responses[i] = f"Player {i}: {player_responses[i]}"


formatted_player_response = '\n-'.join(player_responses)

VOTING_PROMPT = f"""You are playing a game called Chameleon. In this game, there are {NUM_PLAYERS} players. {NUM_PLAYERS-1} of them are all the same animal. 1 player is a different animal who is pretending to be the same animal as everyone else. You are the judge of this game. Each player has said a sentence describing themselves. Use these descriptions to decide which player is most likely not describing the same animal as everyone else. 
Player responses: 
-{formatted_player_response}

Please vote for the player you think is most likely to be the Chameleon.
"""

print(VOTING_PROMPT)

# election = [0*NUM_PLAYERS]

# Tools
def vote(player: str) -> str:
    """Votes for a player."""
    print(f"A player has voted for {player}")

#https://python.langchain.com/docs/modules/agents/agent_types/react
    # try:
    #     election[player] += 1
    #     return f"You successfully voted for {player}"
    # except KeyError:
    #     return f"{player} is not a valid option on this ballot, please try again"


tools = [
    Tool(
        name='Vote',
        func=vote,
        description='used to cast a vote for who you think is the Chameleon'
    )
]

# voting_agent_executor = initialize_agent(tools, decision_llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
# voting_agent_executor.invoke({"input": VOTING_PROMPT})


# # This is an LLMChain to write a synopsis given a title of a play and the era it is set in.
# llm = OpenAI(temperature=.7)
# synopsis_template = """You are a playwright. Given the title of play and the era it is set in, it is your job to write a synopsis for that title.
#
# Title: {title}
# Era: {era}
# Playwright: This is a synopsis for the above play:"""
# synopsis_prompt_template = PromptTemplate(input_variables=["title", "era"], template=synopsis_template)
# synopsis_chain = LLMChain(llm=llm, prompt=synopsis_prompt_template, output_key="synopsis")
#
# # This is an LLMChain to write a review of a play given a synopsis.
# llm = OpenAI(temperature=.7)
# template = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.
#
# Play Synopsis:
# {synopsis}
# Review from a New York Times play critic of the above play:"""
# prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
# review_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="review")
#
# # This is the overall chain where we run these two chains in sequence.
# from langchain.chains import SequentialChain
# overall_chain = SequentialChain(
#     chains=[synopsis_chain, review_chain],
#     input_variables=["era", "title"],
#     # Here we return multiple variables
#     output_variables=["synopsis", "review"],
#     verbose=True)


#BABYAGI
import os
from collections import deque
from typing import Dict, List, Optional, Any

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
# from langchain.llms import BaseLLM
# from langchain.schema.vectorstore import VectorStore
# from pydantic import BaseModel, Field
# from langchain.chains.base import Chain
from langchain_experimental.autonomous_agents import BabyAGI

from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
# Define your embedding model
embeddings_model = OpenAIEmbeddings()
# Initialize the vectorstore as empty
import faiss

embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
llm = ChatOpenAI(model='gpt-4', temperature=0)

# Logging of LLMChains
verbose = False
# If None, will keep going on forever
max_iterations = 10
baby_agi = BabyAGI.from_llm(
    llm=llm, vectorstore=vectorstore, verbose=verbose, max_iterations=max_iterations
)

baby_agi({"objective": VOTING_PROMPT})