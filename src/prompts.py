from models import *
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate


def fetch_prompt(prompt_name):
    """Fetches a static prompt."""
    return prompts[prompt_name]
def format_prompt(prompt_name, **kwargs):
    """Fetches a template prompt and populates it."""
    return fetch_prompt(prompt_name).format(**kwargs)


class Task:
    def __init__(self, prompt: str, response_format: Type[BaseModel], few_shot_examples: List[dict] = None):
        self.prompt = prompt
        self.response_format = response_format
        self.few_shot_examples = few_shot_examples

    def full_prompt(self, **kwargs):
        prompt = self.prompt.format(**kwargs)

        format_instructions = self.get_format_instructions()
        if self.few_shot_examples:
            few_shot = self.get_few_shot()

    def get_format_instructions(self):
        schema = self.get_input_schema()
        format_instructions = FORMAT_INSTRUCTIONS.format(schema=schema)

        return format_instructions

    def get_input_schema(self):
        schema = self.response_format.model_json_schema()

        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]

        schema_str = json.dumps(reduced_schema, indent=4)

        return schema_str

    def get_few_shot(self, max_examples=3):
        if len(self.few_shot_examples) <= max_examples:
            examples = self.few_shot_examples
        else:
            examples = random.sample(self.few_shot_examples, max_examples)

        few_shot = "\n\n".join([self.format_example(ex) for ex in examples])

        return few_shot

    def format_example(self, example):
        ex_prompt = self.prompt.format(**example['inputs'])
        ex_response = example['response']

        return f"Prompt: {ex_prompt}\nResponse: {ex_response}"



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

_chameleon_guess_decision = """\
You now have the opportunity to guess what animal the other players are pretending to be.
If you guess correctly you will WIN, if you guess incorrectly you will LOSE.
If you believe you know what animal the other players are pretending to be make choose to GUESS, otherwise choose to PASS.
Your response should be one of ("GUESS", "PASS")
Your Response: 
"""

_chameleon_guess_animal = """\
What animal do you think the other players are pretending to be?
"""

_vote_prompt = """\
Now it is time to vote. Choose from the players above who you think the Chameleon is.
"""

prompts = {
    "game_rules": _game_rules,
    "assign_herd": _assign_herd,
    "assign_chameleon": _assign_chameleon,
    "player_describe_animal": _player_describe_animal,
    "chameleon_guess_decision": _all_responses + _chameleon_guess_decision,
    "chameleon_guess_animal": _chameleon_guess_animal,
    "response": "Your response:",
    "vote": _all_responses + _vote_prompt
}
