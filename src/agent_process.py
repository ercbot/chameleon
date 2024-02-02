


"""Beginning of the round:
1. Assigned each player role
2. determine the order in which the players will speak"""
import os

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

import random
import json
import re
import uuid

from langchain.prompts import PromptTemplate
from agents import PlayerAgent, llm_parameters
from reasoning_tools import extract_vote

chameleon_agent = PlayerAgent(role="chameleon")
herd_agent = PlayerAgent(role="herd")
judge_agent = PlayerAgent(role="judge")

# Game Setup
NUM_PLAYERS = 5
ANIMALS = ["Shark", "Tiger", "Owl", "Gorilla"]

selected_animal = random.choice(ANIMALS)
selected_chameleon = random.randint(0, NUM_PLAYERS - 1)

print(f'Animal: {selected_animal}')
print(f'Chameleon: Player {selected_chameleon+1}')

GAME_RULES = '''\
GAME RULES: You are playing a social deduction game where every player pretends the be the same animal. 
During the round players go around the room and make an "I"-statement as if they were the animal. 
All players know what animal they are pretending to be, except one who is known as the Chameleon. The Chameleon and must blend in by providing details about the animal using context from other players. 
The other players must be careful not to give away too much information with their responses so that Chameleon cannot guess the animal. After all players have spoken, they vote on who they think the Chameleon is. 
WIN CONDITION:
- If the other players vote for the Chameleon, they win the game. 
- If they vote for the wrong player then the Chameleon wins the game. 

'''

HERD_PROMPT = """\
You are a {animal}. In 10 words or less give a description of yourself starting with "I". The description should not give away too much information about the {animal} as you do not want the Chameleon to be able to guess what animal you are. Do not repeat responses from other players.
Previously Mentioned Descriptions: 
{player_responses}
Your Response:
"""

CHAMELEON_PROMPT = """\
You are the Chameleon. Initially, you don't know what animal the other players are, your goal is to deduce . Using the context that they have provided, In 10 words or less give a description of yourself starting with "I". If no one else has said anything try to say something generic that could be true of any animals. 
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


# Game Round, all the players go around and describe the animal
player_responses = []
formatted_player_responses = ''
for i in range(0, NUM_PLAYERS):
    if i == selected_chameleon:
        role = "chameleon"
        prompt = chameleon_prompt_template.format_prompt(player_responses=formatted_player_responses)
        response = chameleon_agent.invoke({"input": prompt})
    else:
        role = "herd"
        prompt = herd_prompt_template.format_prompt(animal=selected_animal, player_responses=formatted_player_responses)
        response = herd_agent.invoke({"input": prompt})

    # record thought process - TODO: make this into seperate func
    intermediate_steps = []
    if response['intermediate_steps']:
        for step in response['intermediate_steps']:
            intermediate_steps.append(
                {
                    "agent_action": {
                        "tool": step[0].tool,
                        "tool_input": step[0].tool_input,
                        "log": step[0].log
                    },
                    "output": step[1]
            }
            )


    # Record the LLM Call
    player_response = {
        "name": f"Player {i+1}",
        "role": role,
        "prompt": prompt.to_string(),
        "intermediate_steps": intermediate_steps,
        "final_answer": response['output']
    }

    print(intermediate_steps)

    player_responses.append(player_response)
    # Nicely Formatted String of Responses
    formatted_player_responses += f"- Player {i + 1}: {response['output']}\n"


JUDGE_PROMPT = f"""You are playing a game called Chameleon. In this game, there are {NUM_PLAYERS} players. {NUM_PLAYERS - 1} of them are all the same animal. 1 player is a different animal who is pretending to be the same animal as everyone else. You are the judge of this game. Each player has said a sentence describing themselves. Use these descriptions to decide which player is most likely not describing the same animal as everyone else. 
Player responses: 
{formatted_player_responses}

Please vote for the player you think is most likely to be the Chameleon.
"""

print(JUDGE_PROMPT)

# election = [0*NUM_PLAYERS]

judge_response = judge_agent.invoke({"input": JUDGE_PROMPT})




# Determine Winner - doesn't work because sometimes the judges final answer will mention multiple players...
player_vote = extract_vote(judge_response['output'])

print(player_vote)

herd_win = re.match(f"Player {selected_chameleon+1}".lower(), player_vote.lower())
if herd_win:
    winner = "Herd"
else:
    winner = "Chameleon"

print(f"The {winner} has won!")

# Save the experiment
game_ruleset = 'vote'
experiment_id = f"{game_ruleset}-{uuid.uuid4().hex}"
experiment = {
    "experiment_id": experiment_id,
    "game_ruleset": game_ruleset,
    "chameleon_llm_parameters": llm_parameters['chameleon'],
    "herd_llm_parameters": llm_parameters['herd'],
    "judge_llm_parameters": llm_parameters['judge'],
    "player_responses": player_responses
}

experiment_path = os.path.join(os.pardir, 'experiments', f"{experiment_id}.json")
with open(experiment_path, "w") as output_file:
    output_file.write(json.dumps(experiment, indent=4))

