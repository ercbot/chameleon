import os
from typing import Type, Literal
import logging

from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda, chain

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AnyMessage

from langchain_core.exceptions import OutputParserException

from pydantic import BaseModel

from game_utils import log
from controllers import controller_from_name

Role = Literal["chameleon", "herd"]

logging.basicConfig(level=logging.WARNING)

class Player:

    role: Role | None = None
    """The role of the player in the game. Can be "chameleon" or "herd"."""
    rounds_played_as_chameleon: int = 0
    """The number of times the player has been the chameleon."""
    rounds_played_as_herd: int = 0
    """The number of times the player has been in the herd."""
    points: int = 0
    """The number of points the player has."""
    messages: list[AnyMessage] = []
    """The messages the player has sent and received."""
    prompt_queue: list[str] = []
    """A queue of prompts to be added to the next prompt."""

    def __init__(
            self,
            name: str,
            controller: str,
            player_id: str = None,
            log_filepath: str = None
    ):
        self.name = name
        self.id = player_id

        if controller == "human":
            self.controller_type = "human"
        else:
            self.controller_type = "ai"

        self.controller = controller_from_name(controller)
        self.log_filepath = log_filepath

        if log_filepath:
            player_info = {
                "id": self.id,
                "name": self.name,
                "role": self.role,
                "controller": {
                    "name": controller,
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

        message = HumanMessage(content=prompt)
        output = await self.generate.ainvoke(message)
        if self.controller_type == "ai":
            retries = 0
            try:
                output = await self.format_output.ainvoke({"output_format": output_format})
            except OutputParserException as e:
                if retries < max_retries:
                    retries += 1
                    logging.warning(f"Player {self.id} failed to format response: {output} due to an exception: {e} \n\n Retrying {retries}/{max_retries}")
                    self.add_to_history(HumanMessage(content=f"Error formatting response: {e} \n\n Please try again."))
                    output = await self.format_output.ainvoke({"output_format": output_format})

                else:
                    logging.error(f"Max retries reached due to Error: {e}")
                    raise e
        else:
            # Convert the human message to the pydantic object format
            field_name = output_format.model_fields.copy().popitem()[0]  # only works because current outputs have only 1 field
            output = output_format.model_validate({field_name: output.content})

        return output

    def add_to_history(self, message: AnyMessage):
        self.messages.append(message)
        log(message.dict(), self.log_filepath)

    def is_human(self):
        return self.controller_type == "human"

    def is_ai(self):
        return not self.is_human()

    def _generate(self, message: HumanMessage):
        """Entry point for the Runnable generating responses, automatically logs the message."""
        self.add_to_history(message)

        # AI's need to be fed the whole message history, but humans can just go back and look at it
        if self.controller_type == "human":
            response = self.controller.invoke(message.content)
        else:
            response = self.controller.invoke(self.messages)

        self.add_to_history(response)

        return response

    def _output_formatter(self, inputs: dict):
        """Formats the output of the response."""
        output_format: BaseModel = inputs["output_format"]

        prompt_template = PromptTemplate.from_template(
            "Please rewrite your previous response using the following format: \n\n{format_instructions}"
        )

        parser = PydanticOutputParser(pydantic_object=output_format)

        prompt = prompt_template.invoke({"format_instructions": parser.get_format_instructions()})

        message = HumanMessage(content=prompt.text)

        response = self.generate.invoke(message)

        return parser.invoke(response)
