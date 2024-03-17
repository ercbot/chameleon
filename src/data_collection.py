import os
import pathlib
from typing import NewType

import pydantic

import player
import message

from pymongo import MongoClient
from pydantic import BaseModel


DATA_COLLECTION_MODE = os.environ.get("DATA_COLLECTION_MODE", "JSONL")

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
DB_NAME = os.environ.get("MONGODB_NAME")

Model = NewType("Model", BaseModel)


def save(log_object: Model):
    collection = get_collection(log_object)

    if DATA_COLLECTION_MODE.upper() == "JSONL":
        data_dir = pathlib.Path(__file__).parent.parent / "data"
        log_file = os.path.join(data_dir, f"{collection}.jsonl")

        with open(log_file, "a+") as f:
            f.write(log_object.model_dump_json() + "\n")

    if DATA_COLLECTION_MODE.upper() == "MONGODB":
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client[DB_NAME]
        db[collection].insert_one(log_object.model_dump())


def get_collection(log_object: Model) -> str:
    from game import Game

    if isinstance(log_object, message.AgentMessage):
        collection = "messages"
    elif isinstance(log_object, player.Player):
        collection = "players"
    elif isinstance(log_object, Game):
        collection = "games"
    else:
        raise ValueError(f"Unknown log object type: {type(log_object)}")

    return collection
