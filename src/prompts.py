def fetch_prompt(prompt_name):
    """Fetches a static prompt."""
    return prompts[prompt_name]


def format_prompt(prompt_name, **kwargs):
    """Fetches a template prompt and populates it."""
    return fetch_prompt(prompt_name).format(**kwargs)


_game_rules = '''\
You are playing a social deduction game where every player pretends the be the same animal. 
During the round players go around the room and make an "I"-statement as if they were the animal. 
All players know what animal they are pretending to be, except one who is known as the Chameleon. 
The Chameleon and must blend in by providing details about the animal using context from other players. 
The other players must be careful not to give away too much information with their responses so that Chameleon cannot guess the animal. 
After all players have spoken, they vote on who they think the Chameleon is. \
'''

_assign_herd = """\
You are a **{herd_animal}**, keep this secret at all costs and figure which player is not really a {herd_animal}
"""

_assign_chameleon = """\
"You are the **Chameleon**, remain undetected and guess what animal the others are pretending to be"
"""

_player_describe_animal = """It's your turn to describe yourself. Remember:
- Start your response with "I"
- Keep your response as short as possible 
- Do not repeat responses from other players.

Your Response:"""

_all_responses = """\
Below are the responses from all the other players. 
{player_responses}
"""

_chameleon_guess_animal = """\
What animal do you think the other players are pretending to be?
Guess the name of the animal not it's plural form e.g. guess "animal" not "animals"
"""

_vote_prompt = """\
Now it is time to vote. Choose from the players above who you think the Chameleon is.
"""

prompts = {
    "game_rules": _game_rules,
    "assign_herd": _assign_herd,
    "assign_chameleon": _assign_chameleon,
    "player_describe_animal": _player_describe_animal,
    "chameleon_guess_animal": _chameleon_guess_animal,
    "response": "Your response:",
    "vote": _all_responses + _vote_prompt
}
