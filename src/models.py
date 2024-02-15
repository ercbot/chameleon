from typing import Annotated

from pydantic import BaseModel, field_validator

MAX_DESCRIPTION_LEN = 10


class AnimalDescriptionModel(BaseModel):
    # Define fields of our class here
    description: str

    # @field_validator('description')
    # @classmethod
    # def check_starting_character(cls, v) -> str:
    #     if not v[0].upper() == 'I':
    #         raise ValueError("Description must begin with 'I'")
    #     return v
    #
    # @field_validator('description')
    # @classmethod
    # def wordcount(cls, v) -> str:
    #     count = len(v.split())
    #     if count > MAX_DESCRIPTION_LEN:
    #         raise ValueError(f"Animal Description must be {MAX_DESCRIPTION_LEN} words or less")
    #     return v


class ChameleonDecisionModel(BaseModel):
    will_guess: bool


class AnimalGuessModel(BaseModel):
    animal_name: str


class ChameleonGuessDecisionModel(BaseModel):
    decision: Annotated[str, "Must be one of: ['guess', 'pass']"]

    @field_validator('decision')
    @classmethod
    def check_decision(cls, v) -> str:
        if v.lower() not in ['guess', 'pass']:
            raise ValueError("Decision must be one of: ['guess', 'pass']")
        return v


class ChameleonGuessAnimalModel(BaseModel):
    animal: str


class VoteModel(BaseModel):
    vote: str

    # @field_validator('vote')
    # @classmethod
    # def check_player_exists(cls, v) -> str:
    #     if v.lower() not in [player.lower() for player in players]:
    #         raise ValueError(f"Player {v} does not exist")
    #     return v

