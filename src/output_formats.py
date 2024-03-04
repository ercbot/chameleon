import random
from typing import Annotated, NewType, List, Optional, Type, Literal
import json

from pydantic import BaseModel, field_validator, Field

FORMAT_INSTRUCTIONS = """Please reformat your previous response as a JSON instance that conforms to the JSON structure below.
Here is the output format:
{schema}
"""
FEW_SHOT_INSTRUCTIONS = """Here are a few examples of correctly formatted responses: \n
{examples}
"""

OutputFormatModel = NewType("OutputFormatModel", BaseModel)


class OutputFormat:
    """The base class for all output formats."""

    format_instructions: str = FORMAT_INSTRUCTIONS
    """Instructions for formatting the output, it is combined with the JSON schema of the output format."""
    few_shot_instructions: str = FEW_SHOT_INSTRUCTIONS
    """Instructions for the few shot examples, it is combined with the few shot examples."""
    few_shot_examples: Optional[List[dict]] = None
    """A list of examples to be shown to the agent to help them understand the desired format of the output."""

    def __init__(self, output_format_model: Type[OutputFormatModel], player_names: List[str] = None):
        self.output_format_model = output_format_model
        self.output_format_model.player_names = player_names

    def get_format_instructions(self) -> str:
        json_format = self.output_format_model().model_dump_json()

        return self.format_instructions.format(schema=json_format)

    def get_few_shot(self, max_examples=3):
        if len(self.few_shot_examples) <= max_examples:
            examples = self.few_shot_examples
        else:
            examples = random.sample(self.few_shot_examples, max_examples)

        few_shot = "\n\n".join([f"Example Response:\n{json.dumps(example)}" for example in examples])

        return self.few_shot_instructions.format(examples=few_shot)


class AnimalDescriptionFormat(BaseModel):
    # Define fields of our class here
    description: str = Field("A brief description of the animal")
    """A brief description of the animal"""

    @field_validator('description')
    @classmethod
    def check_starting_character(cls, v) -> str:
        if not v[0].upper() == 'I':
            raise ValueError("Description must begin with 'I'")
        return v


class ChameleonGuessFormat(BaseModel):
    animal: str = Field("The name of the animal you think the chameleon is")

    @field_validator('animal')
    @classmethod
    def is_one_word(cls, v) -> str:
        if len(v.split()) > 1:
            raise ValueError("Animal's name must be one word")
        return v


class HerdVoteFormat(BaseModel):
    player_names: List[str] = Field([], exclude=True)
    """The names of the players in the game"""
    vote: str = Field("The name of the player you are voting for")
    """The name of the player you are voting for"""

    @field_validator('vote')
    @classmethod
    def check_player_exists(cls, v) -> str:
        if v.lower() not in [player.lower() for player in cls.player_names]:
            raise ValueError(f"Player {v} does not exist")
        return v
