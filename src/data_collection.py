import os
import pathlib
from typing import NewType

import pydantic

import player
import message

from pydantic import BaseModel

COLLECT_DATA = os.environ.get("COLLECT_DATA", "true").upper() == "TRUE"

Model = NewType("Model", BaseModel)


data_dir = pathlib.Path(__file__).parent.parent / "data"


def save(log_object: Model):
    if COLLECT_DATA:
        log_file = get_log_file(log_object)

        with open(log_file, "a+") as f:
            f.write(log_object.model_dump_json() + "\n")


def get_log_file(log_object: Model) -> str:
    from game import Game

    if isinstance(log_object, message.AgentMessage):
        log_file = "messages.jsonl"
    elif isinstance(log_object, player.Player):
        log_file = "players.jsonl"
    elif isinstance(log_object, Game):
        log_file = "games.jsonl"
    else:
        raise ValueError(f"Unknown log object type: {type(log_object)}")

    return os.path.join(data_dir, log_file)
