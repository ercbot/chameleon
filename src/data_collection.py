import os
from typing import NewType

import pydantic

import message
import player

from pydantic import BaseModel

Model = NewType("Model", BaseModel)


data_dir = os.path.join(os.pardir, "data")


def save(log_object: Model):
    log_file = get_log_file(log_object)

    with open(log_file, "a+") as f:
        f.write(log_object.model_dump_json() + "\n")


def get_log_file(log_object: Model) -> str:
    match type(log_object):
        case message.AgentMessage:
            log_file = "messages.jsonl"
        # ...
        case _:
            raise ValueError(f"Unknown log object type: {type(log_object)}")

    return os.path.join(data_dir, log_file)
