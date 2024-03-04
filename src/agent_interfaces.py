from typing import Type, NewType
import json

from openai import OpenAI
from colorama import Fore, Style
from pydantic import BaseModel, ValidationError

from output_formats import OutputFormat, OutputFormatModel
from message import Message, AgentMessage
from data_collection import save

class BaseAgentInterface:
    """
    The interface that agents use to receive info from and interact with the game.
    This is the base class and should not be used directly.
    """

    is_human: bool = False

    def __init__(
            self,
            agent_id: str = None
    ):
        self.id = agent_id
        self.messages = []

    def add_message(self, message: Message):
        """Adds a message to the message history, without generating a response."""
        bound_message = AgentMessage.from_message(message, self.id, len(self.messages))
        save(bound_message)
        self.messages.append(bound_message)

    def respond_to(self, message: Message) -> Message:
        """Adds a message to the message history, and generates a response message."""
        self.add_message(message)
        response = Message(type="agent", content=self._generate_response())
        self.add_message(response)
        return response

    def respond_to_formatted(self, message: Message, output_format: OutputFormat, max_retries = 3) -> OutputFormatModel:
        """Adds a message to the message history, and generates a response matching the provided format."""
        initial_response = self.respond_to(message)

        reformat_message = Message(type="format", content=output_format.get_format_instructions())

        output = None
        retries = 0

        while not output and retries < max_retries:
            try:
                formatted_response = self.respond_to(reformat_message)
                output = output_format.output_format_model.model_validate_json(formatted_response.content)
            except ValidationError as e:
                if retries > max_retries:
                    raise e
                retry_message = Message(type="retry", content=f"Error formatting response: {e} \n\n Please try again.")
                if output_format.few_shot_examples:
                    self.add_message(retry_message)
                    reformat_message = Message(type="few_shot", content=output_format.get_few_shot()) # not implemented
                else:
                    reformat_message = retry_message

                retries += 1

        return output

    def _generate_response(self) -> str:
        """Generates a response from the Agent."""
        # This is the BaseAgent class, and thus has no response logic
        # Subclasses should implement this method to generate a response using the message history
        raise NotImplementedError

    @property
    def is_ai(self):
        return not self.is_human

AgentInterface = NewType("AgentInterface", BaseAgentInterface)


class OpenAIAgentInterface(BaseAgentInterface):
    """An interface that uses the OpenAI API (or compatible 3rd parties) to generate responses."""
    def __init__(self, agent_id: str, model_name: str = "gpt-3.5-turbo"):
        super().__init__(agent_id)
        self.model_name = model_name
        self.client = OpenAI()

    def _generate_response(self) -> str:
        """Generates a response using the message history"""
        open_ai_messages = [message.to_openai() for message in self.messages]

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=open_ai_messages
        )

        return completion.choices[0].message.content


class HumanAgentInterface(BaseAgentInterface):

    is_human = True

    def respond_to_formatted(self, message: Message, output_format: OutputFormat, **kwargs) -> OutputFormatModel:
        """For Human agents, we can trust them enough to format their own responses... for now"""
        response = super().respond_to(message)
        # only works because current outputs have only 1 field...
        field_name = output_format.output_format_model.model_fields.copy().popitem()[0]
        output = output_format.output_format_model.model_validate({field_name: response.content})

        return output


class HumanAgentCLI(HumanAgentInterface):
    """A Human agent that uses the command line interface to generate responses."""

    def __init__(self, agent_id: str):
        super().__init__(agent_id)

    def add_message(self, message: Message):
        super().add_message(message)
        if message.type == "verbose":
            print(Fore.GREEN + message.content + Style.RESET_ALL)
        elif message.type == "debug":
            print(Fore.YELLOW + "DEBUG: " + message.content + Style.RESET_ALL)
        elif message.type != "agent":
            # Prevents the agent from seeing its own messages on the command line
            print(message.content)

    def _generate_response(self) -> str:
        """Generates a response using the message history"""
        response = input()
        return response
