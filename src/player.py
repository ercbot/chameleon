import os
import asyncio

import openai
from agents import LogMessagesKani
from kani.engines.openai import OpenAIEngine


# Using TGI Inference Endpoints from Hugging Face
# api_type = "tgi"
api_type = "openai"

if api_type == "tgi":
    model_name = "tgi"
    client = openai.Client(
        base_url=os.environ['HF_ENDPOINT_URL'] + "/v1/",
        api_key=os.environ['HF_API_TOKEN']
    )
else:
    model_name = "gpt-3.5-turbo"
    client = openai.Client()

openai_engine = OpenAIEngine(model="gpt-3.5-turbo")


class Player:
    def __init__(self, name: str, controller_type: str, role: str, log_filepath: str = None):
        self.name = name
        self.controller = controller_type
        if controller_type == "ai":
            self.kani = LogMessagesKani(openai_engine, log_filepath=log_filepath)

        self.role = role
        self.messages = []

    async def respond_to(self, prompt: str) -> str:
        """Makes the player respond to a prompt. Returns the response."""
        # Generate a response from the controller
        output = await self.__generate(prompt)

        return output

    async def __generate(self, prompt: str) -> str:
        if self.controller == "human":
            print(prompt)
            return input()

        elif self.controller == "ai":
            output = await self.kani.chat_round_str(prompt)

            return output



