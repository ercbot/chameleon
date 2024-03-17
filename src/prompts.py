def fetch_prompt(prompt_name):
    """Fetches a static prompt."""
    return prompts[prompt_name]


def format_prompt(prompt_name, **kwargs):
    """Fetches a template prompt and populates it."""
    return fetch_prompt(prompt_name).format(**kwargs)


# Get game rules from GAME_RULES.md
with open("GAME_RULES.md", "r") as file:
    _game_rules = file.read()

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
