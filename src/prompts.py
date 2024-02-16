def fetch_prompt(prompt_name):
    """Fetches a static prompt."""
    return prompts[prompt_name]

def format_prompt(prompt_name, **kwargs):
    """Fetches a template prompt and populates it."""
    return fetch_prompt(prompt_name).format(**kwargs)


_game_rules = '''\
GAME RULES: You are playing a social deduction game where every player pretends the be the same animal. 
During the round players go around the room and make an "I"-statement as if they were the animal. 
All players know what animal they are pretending to be, except one who is known as the Chameleon. The Chameleon and must blend in by providing details about the animal using context from other players. 
The other players must be careful not to give away too much information with their responses so that Chameleon cannot guess the animal. After all players have spoken, they vote on who they think the Chameleon is. 

'''

_herd_animal = """\
You are a {animal}, keep this a secret at all costs. 
In 10 words or less give a description of yourself starting with "I". The description should not give away too much information about the {animal} as you do not want the Chameleon to be able to guess what animal you are. Do not repeat responses from other players.
If the Chameleon can guess what animal you really are you will LOSE.
Previously Mentioned Descriptions: 
{player_responses}
"""

_chameleon_animal = """\
You are the Chameleon, keep this a secret at all costs. 
You don't know what animal the other players are, your goal is to deduce it using the context they provide.
Starting with "I" describe yourself in 10 words or less as if you are the same animal as the other players. 
If no one else has said anything try to say something generic that could be true of any animals. 
If the other players realize you are the Chameleon you will LOSE. 
Previously Mentioned Descriptions:
{player_responses}
"""

_all_responses = """\
Below are the responses from all the other players. 
{player_responses}
"""

_chameleon_guess_decision = """\
You now have the opportunity to guess what animal the other players are pretending to be.
If you guess correctly you will WIN, if you guess incorrectly you will LOSE.
If you believe you know what animal the other players are pretending to be make choose to GUESS, otherwise choose to PASS.
"""

_chameleon_guess_animal = """\
What animal do you think the other players are pretending to be?
"""

_vote_prompt = """\
Now it is time to vote. Choose from the players above who you think the Chameleon is.
"""

prompts = {
    "herd_animal": _game_rules + _herd_animal,
    "chameleon_animal": _game_rules + _chameleon_animal,
    "chameleon_guess_decision": _all_responses + _chameleon_guess_decision,
    "chameleon_guess_animal": _chameleon_guess_animal,
    "vote": _all_responses + _vote_prompt
}

