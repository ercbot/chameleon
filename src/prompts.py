"""
Prompts used for the game
"""


def fetch_prompt(prompt_name):
    return prompts[prompt_name]


game_rules = '''\
GAME RULES: You are playing a social deduction game where every player pretends the be the same animal. 
During the round players go around the room and make an "I"-statement as if they were the animal. 
All players know what animal they are pretending to be, except one who is known as the Chameleon. The Chameleon and must blend in by providing details about the animal using context from other players. 
The other players must be careful not to give away too much information with their responses so that Chameleon cannot guess the animal. After all players have spoken, they vote on who they think the Chameleon is. 
WIN CONDITION:
- If the other players vote for the Chameleon, they win the game. 
- If they vote for the wrong player then the Chameleon wins the game. 

'''

herd_animal = """\
You are a {animal}. In 10 words or less give a description of yourself starting with "I". The description should not give away too much information about the {animal} as you do not want the Chameleon to be able to guess what animal you are. Do not repeat responses from other players.
Previously Mentioned Descriptions: 
{player_responses}
Your Response:
"""

chameleon_animal = """\
You are the Chameleon. Initially, you don't know what animal the other players are, your goal is to deduce . Using the context that they have provided, In 10 words or less give a description of yourself starting with "I". If no one else has said anything try to say something generic that could be true of any animals. 
Previously Mentioned Descriptions:
{player_responses}
Your Response:
"""


vote_prompt = """\
The players have spoken, now it is time to vote. Choose from the players below who you think the Chameleon is.
{players}
"""

herd_vote = """\
Who do you think the Chameleon is?
"""

chameleon_prompt = """\
You are the Chameleon, vote for someone else to remove suspicion from yourself.
"""


prompts = {
    "herd_animal": game_rules + herd_animal,
    "chameleon_animal": game_rules + chameleon_animal,
    "vote_prompt": vote_prompt
}

