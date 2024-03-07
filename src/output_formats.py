import random
from typing import Annotated, NewType, List, Optional, Type, Literal
import json

from pydantic import BaseModel, field_validator, Field, model_validator

FORMAT_INSTRUCTIONS = """Please reformat your previous response as a JSON instance that conforms to the JSON structure below.
Here is the output format:
{schema}
"""


class OutputFormatModel(BaseModel):
    @classmethod
    def get_format_instructions(cls) -> str:
        """Returns a string with instructions on how to format the output."""
        json_format = {}
        for field in cls.model_fields:
            if not cls.model_fields[field].exclude:
                json_format[field] = cls.model_fields[field].description

        # In the future, we could instead use get_annotations() to get the field descriptions
        return FORMAT_INSTRUCTIONS.format(schema=json.dumps(json_format))


class AnimalDescriptionFormat(OutputFormatModel):
    # Define fields of our class here
    description: str = Field(description="A brief description of the animal")
    """A brief description of the animal"""

    # @field_validator('description')
    # @classmethod
    # def check_starting_character(cls, v) -> str:
    #     if not v[0].upper() == 'I':
    #         raise ValueError("Description must begin with 'I'")
    #     return v


class ChameleonGuessFormat(OutputFormatModel):
    animal: str = Field(description="Name of the animal you think the Herd is in its singular form, e.g. 'animal' not 'animals'")

    @field_validator('animal')
    @classmethod
    def is_one_word(cls, v) -> str:
        if len(v.split()) > 1:
            raise ValueError("Animal's name must be one word")
        return v


class HerdVoteFormat(OutputFormatModel):
    player_names: List[str] = Field([], exclude=True)
    """The names of the players in the game"""
    vote: str = Field(description="The name of the player you are voting for")
    """The name of the player you are voting for"""

    @model_validator(mode="after")
    def check_player_exists(self) -> "HerdVoteFormat":
        if self.vote.lower() not in [player.lower() for player in self.player_names]:
            raise ValueError(f"Player {self.vote} does not exist, please vote for one of {self.player_names}")
        return self