from json import JSONDecodeError
from typing import Type, NewType
import json

from openai import OpenAI
from colorama import Fore, Style
from pydantic import BaseModel, ValidationError

from output_formats import OutputFormatModel
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
            agent_id: str = None,
            log_messages: bool = True
    ):
        self.id = agent_id
        """The id of the agent."""
        self.log_messages = log_messages
        """Whether to log messages or not."""
        self.messages = []
        """The message history of the agent."""

    @property
    def is_ai(self):
        return not self.is_human

    def add_message(self, message: Message):
        """Adds a message to the message history, without generating a response."""
        bound_message = AgentMessage.from_message(message, self.id, len(self.messages))
        if self.log_messages:
            save(bound_message)
        self.messages.append(bound_message)

    # Respond To methods - These take a message as input and generate a response

    def respond_to(self, message: Message) -> Message:
        """Take a message as input and return a response. Both the message and the response are added to history."""
        self.add_message(message)
        response = self.generate_response()
        return response

    def respond_to_formatted(
            self, message: Message,
            output_format: Type[OutputFormatModel],
            additional_fields: dict = None,
            **kwargs
    ) -> OutputFormatModel:
        """Responds to a message and logs the response."""
        self.add_message(message)
        output = self.generate_formatted_response(output_format, additional_fields, **kwargs)
        return output

    # Generate response methods - These do not take a message as input and only use the current message history

    def generate_response(self) -> Message | None:
        """Generates a response based on the current messages in the history."""
        content = self._generate()
        if content:
            response = Message(type="agent", content=content)
            self.add_message(response)
            return response
        else:
            return None

    def generate_formatted_response(
            self,
            output_format: Type[OutputFormatModel],
            additional_fields: dict = None,
            max_retries=3,
    ) -> OutputFormatModel:
        """Generates a response matching the provided format."""
        initial_response = self.generate_response()

        reformat_message = Message(type="format", content=output_format.get_format_instructions())

        output = None
        retries = 0

        while not output:
            try:
                formatted_response = self.respond_to(reformat_message)

                fields = json.loads(formatted_response.content)
                if additional_fields:
                    fields.update(additional_fields)

                output = output_format.model_validate(fields)

            except ValidationError as e:
                # If the response doesn't match the format, we ask the agent to try again
                if retries > max_retries:
                    raise e

                retry_message = Message(type="retry", content=f"Error formatting response: {e} \n\n Please try again.")
                reformat_message = retry_message

                retries += 1

            except JSONDecodeError as e:
                # Occasionally models will output json as a code block, which will cause a JSONDecodeError
                if retries > max_retries:
                    raise e

                retry_message = Message(type="retry",
                                        content="There was an Error with your JSON format. Make sure you are not using code blocks."
                                                "i.e. your response should be:\n{...}\n"
                                                "Instead of:\n```json\n{...}\n```\n\n Please try again.")
                reformat_message = retry_message

                retries += 1

        return output

    # How agents actually generate responses

    def _generate(self) -> str:
        """Generates a response from the Agent."""
        # This is the BaseAgent class, and thus has no response logic
        # Subclasses should implement this method to generate a response using the message history
        raise NotImplementedError


AgentInterface = NewType("AgentInterface", BaseAgentInterface)


class OpenAIAgentInterface(BaseAgentInterface):
    """An interface that uses the OpenAI API (or compatible 3rd parties) to generate responses."""

    def __init__(self, agent_id: str, model_name: str = "gpt-3.5-turbo"):
        super().__init__(agent_id)
        self.model_name = model_name
        self.client = OpenAI()

    def _generate(self) -> str:
        """Generates a response using the message history"""
        open_ai_messages = [message.to_openai() for message in self.messages]

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=open_ai_messages
        )

        return completion.choices[0].message.content


class HumanAgentInterface(BaseAgentInterface):
    is_human = True

    def generate_formatted_response(
            self,
            output_format: Type[OutputFormatModel],
            additional_fields: dict = None,
            max_retries: int = 3
    ) -> OutputFormatModel | None:
        """For Human agents, we can trust them enough to format their own responses... for now"""
        response = self.generate_response()

        if response:
            # only works because current outputs have only 1 field...
            fields = {output_format.model_fields.copy().popitem()[0]: response.content}
            if additional_fields:
                fields.update(additional_fields)
            output = output_format.model_validate(fields)
        else:
            output = None

        return output


class HumanAgentCLI(HumanAgentInterface):
    """A Human agent that uses the command line interface to generate responses."""
    def add_message(self, message: Message):
        super().add_message(message)
        if message.type == "verbose":
            print(Fore.GREEN + message.content + Style.RESET_ALL)
        elif message.type == "debug":
            print(Fore.YELLOW + "DEBUG: " + message.content + Style.RESET_ALL)
        elif message.type != "agent":
            # Prevents the agent from seeing its own messages on the command line
            print(message.content)

    def _generate(self) -> str:
        """Generates a response using the message history"""
        response = input()
        return response
