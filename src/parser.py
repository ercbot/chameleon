from typing import Type
import asyncio
import json

from kani.engines.openai import OpenAIEngine
from pydantic import BaseModel, ValidationError

from agents import LogMessagesKani

FORMAT_INSTRUCTIONS = """The output should be reformatted as a JSON instance that conforms to the JSON schema below.
Here is the output schema:
```
{schema}
```
"""

parser_prompt = """\
The user gave the following output to the prompt:
Prompt: 
{prompt}
Output:
{message}

{format_instructions}
"""


class ParserKani(LogMessagesKani):
    def __init__(self, engine, *args, **kwargs):
        super().__init__(engine, *args, **kwargs)

    async def parse(self, prompt: str, message: str, format_model: Type[BaseModel], max_retries: int = 3, **kwargs):
        format_instructions = self.get_format_instructions(format_model)

        parser_instructions = parser_prompt.format(
            prompt=prompt,
            message=message,
            format_instructions=format_instructions
        )

        response = await self.chat_round_str(parser_instructions, **kwargs)

        try:
            output = format_model.model_validate_json(response)
        except ValidationError as e:
            print(f"Output did not conform to the expected format: {e}")
            raise e

        # Clear the Chat History after successful parse
        self.chat_history = []

        return output

    @staticmethod
    def get_format_instructions(format_model: Type[BaseModel]):
        schema = format_model.model_json_schema()

        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]

        schema_str = json.dumps(reduced_schema, indent=4)

        return FORMAT_INSTRUCTIONS.format(schema=schema_str)

    @classmethod
    def default(cls):
        """Default ParserKani with OpenAIEngine."""
        engine = OpenAIEngine(model="gpt-3.5-turbo")
        return cls(engine)



# Testing
# parser = ParserKani(engine=OpenAIEngine(model="gpt-3.5-turbo"))
#
# sample_prompt = """\
# Below are the responses from all players. Now it is time to vote. Choose from the players below who you think the Chameleon is.
# - Mallory: I am tall and have a long neck.
# - Jack: I am a herbivore and have a long neck.
# - Jill: I am a herbivore and have a long neck.
# - Bob: I am tall and have a long neck.
# - Courtney: I am tall and have a long neck.
# """
#
# sample_message = """\
# I think the Chameleon is Mallory.
# """
#
# test_output = asyncio.run(parser.parse(prompt=sample_prompt, message=sample_message, format_model=VoteModel))
#
# print(test_output)
#
# print(VoteModel.model_validate_json(test_output))