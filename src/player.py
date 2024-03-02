import os
from typing import Type, Literal, List
import logging

from langchain_core.runnables import Runnable, RunnableLambda

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from langchain_core.exceptions import OutputParserException

from pydantic import BaseModel

from game_utils import log
from message import Message, MessageType

Role = Literal["chameleon", "herd"]

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("chameleon")


class Player:

    role: Role | None = None
    """The role of the player in the game. Can be "chameleon" or "herd". This changes every round."""
    rounds_played_as_chameleon: int = 0
    """The number of times the player has been the Chameleon."""
    rounds_played_as_herd: int = 0
    """The number of times the player has been in the Herd."""
    points: int = 0
    """The number of points the player has."""

    def __init__(
            self,
            name: str,
            controller: Type[Runnable | RunnableLambda],
            controller_name: str,
            player_id: str = None,
            log_filepath: str = None
    ):
        self.name = name
        self.id = player_id

        if controller_name == "human":
            self.controller_type = "human"
        else:
            self.controller_type = "ai"

        self.controller = controller
        """The controller for the player."""
        self.log_filepath = log_filepath
        """The filepath to the log file. If None, no logs will be written."""
        self.messages: list[Message] = []
        """The messages the player has sent and received."""
        self.prompt_queue: List[str] = []
        """A queue of prompts to be added to the next prompt."""

        if log_filepath:
            player_info = {
                "id": self.id,
                "name": self.name,
                "role": self.role,
                "controller": {
                    "name": controller_name,
                    "type": self.controller_type
                }
            }
            log(player_info, log_filepath)

        # initialize the runnables
        self.generate = RunnableLambda(self._generate)
        self.format_output = RunnableLambda(self._output_formatter)

    def assign_role(self, role: Role):
        self.role = role
        if role == "chameleon":
            self.rounds_played_as_chameleon += 1
        elif role == "herd":
            self.rounds_played_as_herd += 1

    async def respond_to(self, prompt: str, output_format: Type[BaseModel], max_retries=3):
        """Makes the player respond to a prompt. Returns the response in the specified format."""
        if self.prompt_queue:
            # If there are prompts in the queue, add them to the current prompt
            prompt = "\n".join(self.prompt_queue + [prompt])
            # Clear the prompt queue
            self.prompt_queue = []

        message = self.player_message("prompt", prompt)
        output = await self.generate.ainvoke(message)
        if self.controller_type == "ai":
            retries = 0
            try:
                output = await self.format_output.ainvoke({"output_format": output_format})
            except OutputParserException as e:
                if retries < max_retries:
                    retries += 1
                    logger.warning(f"Player {self.id} failed to format response: {output} due to an exception: {e} \n\n Retrying {retries}/{max_retries}")
                    retry_message = self.player_message("retry", f"Error formatting response: {e} \n\n Please try again.")
                    self.add_to_history(retry_message)
                    output = await self.format_output.ainvoke({"output_format": output_format})

                else:
                    error_message = self.player_message("error", f"Error formatting response: {e} \n\n Max retries reached.")
                    self.add_to_history(error_message)
                    logging.error(f"Max retries reached due to Error: {e}")
                    raise e
        else:
            # Convert the human message to the pydantic object format
            field_name = output_format.model_fields.copy().popitem()[0]  # only works because current outputs have only 1 field
            output = output_format.model_validate({field_name: output.content})

        return output

    def player_message(self, message_type: MessageType, content: str) -> Message:
        """Creates a message assigned to the player."""
        return Message(player_id=self.id, message_number=len(self.messages), type=message_type, content=content)


    def add_to_history(self, message: Message):
        self.messages.append(message)
        log(message.model_dump(), self.log_filepath)

    def is_human(self):
        return self.controller_type == "human"

    def is_ai(self):
        return not self.is_human()

    async def _generate(self, message: Message):
        """Entry point for the Runnable generating responses, automatically logs the message."""
        self.add_to_history(message)

        # AI's need to be fed the whole message history, but humans can just go back and look at it
        if self.controller_type == "human":
            response = await self.controller.ainvoke(message.content)
        else:
            formatted_messages = [message.to_controller() for message in self.messages]
            response = await self.controller.ainvoke(formatted_messages)

        self.add_to_history(self.player_message("player", response.content))

        return response

    async def _output_formatter(self, inputs: dict):
        """Formats the output of the response."""
        output_format: BaseModel = inputs["output_format"]

        prompt_template = PromptTemplate.from_template(
            "Please rewrite your previous response using the following format: \n\n{format_instructions}"
        )

        parser = PydanticOutputParser(pydantic_object=output_format)

        prompt = prompt_template.invoke({"format_instructions": parser.get_format_instructions()})

        message = self.player_message("format", prompt.text)

        response = await self.generate.ainvoke(message)

        return await parser.ainvoke(response)
