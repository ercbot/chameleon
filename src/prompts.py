def fetch_prompt(prompt_name):
    """Fetches a static prompt."""
    return prompts[prompt_name]


def format_prompt(prompt_name, **kwargs):
    """Fetches a template prompt and populates it."""
    return fetch_prompt(prompt_name).format(**kwargs)


_game_rules = """\
You are playing a social deduction game where every player pretends the be the same animal. 
During the round each player gets a turn to describe themselves using an "I"-statement as if they were the animal. 
All but one of players know what animal they are pretending to be, collectively these players are called the Herd.
The remaining player, known as the Chameleon, does not know what animal the others are pretending to be.
The Chameleon must blend in by providing details about the animal using context from other players. 
The Herd must be careful not to give away too much information with their responses so that Chameleon deduce the animal. 

After all players have spoken, two thing will happen:
1. The Chameleon will guess what animal the other players are pretending to be
2. The Herd will vote on who they think the Chameleon is.
 
The game is played in rounds, and the first player to reach 7 points wins. Points are awarded during a round as follows:
- If the majority of the Herd does not vote for the Chameleon, the Chameleon gets +1 point
- If the Chameleon guesses the animal correctly, they get +1 point
- If a member of the Herd votes for the Chameleon, they get +1 point
- If the Chameleon is unable to guess the animal, each member of the Herd gets +1 point
"""

_assign_herd = """\
You are a **{herd_animal}**, keep this secret at all costs and figure which player is not really a {herd_animal}
"""

_assign_chameleon = """\
You are the **Chameleon**, remain undetected and guess what animal the others are pretending to be
"""

_player_describe_animal = """It's your turn to describe yourself. Remember:
- Start your response with "I"
- Keep your response as short as possible 
- Do not repeat responses from other players.

Your Response:"""

_chameleon_guess_animal = """\
What animal do you think the other players are pretending to be?
Player Responses:
{player_responses}
Your Guess:
"""

_vote_prompt = """\
It's your turn to vote. Choose from the other players who you think the Chameleon is.
Player Responses:
{player_responses}
Your Vote:
"""

prompts = {
    "game_rules": _game_rules,
    "assign_herd": _assign_herd,
    "assign_chameleon": _assign_chameleon,
    "player_describe_animal": _player_describe_animal,
    "chameleon_guess_animal": _chameleon_guess_animal,
    "response": "Your response:",
    "vote": _vote_prompt
}
