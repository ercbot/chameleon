import os
import json
import asyncio

import openai
from agents import LogMessagesKani
from kani import ChatMessage
from kani.engines.openai import OpenAIEngine

from game_utils import log

# api_type = "tgi"
# api_type = "openai"
api_type = "ollama"

match api_type:
    case "tgi":
        # Using TGI Inference Endpoints from Hugging Face
        default_engine = OpenAIEngine(  # type: ignore
            api_base=os.environ['HF_ENDPOINT_URL'] + "/v1/",
            api_key=os.environ['HF_API_TOKEN']
        )
    case "openai":
        # Using OpenAI GPT-3.5 Turbo
        default_engine = OpenAIEngine(model="gpt-3.5-turbo")  # type: ignore
    case "ollama":
        # Using Ollama
        default_engine = OpenAIEngine(
            api_base="http://localhost:11434/v1",
            api_key="ollama",
            model="mistral"
        )


class Player:
    def __init__(self, name: str, controller_type: str, role: str, id: str = None, log_filepath: str = None):
        self.name = name
        self.id = id
        self.controller = controller_type
        if controller_type == "ai":
            self.kani = LogMessagesKani(default_engine, log_filepath=log_filepath)

        self.role = role
        self.messages = []

        self.log_filepath = log_filepath

        if log_filepath:
            player_info = {
                "id": self.id,
                "name": self.name,
                "role": self.role,
                "controller": controller_type,
            }
            log(player_info, log_filepath)

    async def respond_to(self, prompt: str) -> str:
        """Makes the player respond to a prompt. Returns the response."""
        if self.controller == "human":
            # We're pretending the human is an ai for logging purposes... I don't love this but it's fine for now
            log(ChatMessage.user(prompt).model_dump_json(), self.log_filepath)
            print(prompt)
            output = input()
            log(ChatMessage.assistant(output).model_dump_json(), self.log_filepath)

            return output

        elif self.controller == "ai":
            output = await self.kani.chat_round_str(prompt)

            return output




