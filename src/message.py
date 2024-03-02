from typing import Literal
from pydantic import BaseModel, computed_field

"""
Right now we have two separate systems that use the word "message":

1. The Game class uses messages to communicate with the players
     - "game" messages pile up in the queue and are responded to by the player once an "instructional" message is sent.
     - "verbose", and "debug" currently for the human player only
   This does **NOT** use the Message class defined below 

2. The Player class uses messages to communicate with the controller (either the AI or the human)
   - "prompt" type messages come from the Game and are responded to by the player.
   - "retry", "error", and "format" are internal messages used by the player to ensure the correct format
   - "player" is used to communicate with the AI or human player.
   All of these messages are logged, and use the Message class defined below

For the future we should investigate redesigning/merging these two systems to avoid confusion
"""

MessageType = Literal["prompt", "player", "retry", "error", "format"]

class Message(BaseModel):
    player_id: str
    """The id of the player that the message was sent by/to."""
    message_number: int
    """The number of the message, indicating the order in which it was sent."""
    type: MessageType
    """The type of the message. Can be "prompt", "player", "retry", "error", or "format"."""
    content: str
    """The content of the message."""

    @computed_field
    def conversation_role(self) -> str:
        """The message type in the format used by the LLM."""

        # Most LLMs expect the "prompt" to come from a "user" and the "response" to come from an "assistant"
        # Since the agents are the ones responding to messages, take on the llm_type of "assistant"
        # This can be counterintuitive since they can be controlled by either human or ai
        # Further, The programmatic messages from the game are always "user"

        if self.type in ["prompt", "retry", "error", "format"]:
            return "user"
        else:
            return "assistant"

    @computed_field
    def message_id(self) -> str:
        """Returns the message id in the format used by the LLM."""
        return f"{self.player_id}-{self.message_number}"

    def to_controller(self) -> tuple[str, str]:
        """Returns the message in a format that can be used by the controller."""
        return self.conversation_role, self.content


