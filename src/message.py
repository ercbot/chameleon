from typing import Literal

from pydantic import BaseModel


# Lots of AI Libraries use HumanMessage and AIMessage as the base classes for their messages.
# This doesn't make sense for our as Humans and AIs are both players in the game, meaning they have the same role.
# The Langchain type field is used to convert to that syntax.
class Message(BaseModel):
    type: Literal["game", "player", "retry", "error", "format"]
    """The type of the message. Can be "prompt" or "player"."""
    content: str
    """The content of the message."""
    @property
    def langchain_type(self):
        """Returns the langchain message type for the message."""
        if self.type in ["game", "retry", "error", "format"]:
            return "human"
        else:
            return "ai"


"""
Right now we have two separate systems that use the word "message":
1. The Game class uses messages to communicate with the players
   They have types:
     - "game" used for all players, these are sent to the players and converted into the the above message class
     - "verbose", and "debug" currently for the human player only
2. The Player class uses messsage is to communicate with the controller (either the AI or the human)
   - "game" type messages come from the Game and are responded to by the format.
   - "retry", "error", and "format"
   - "player" is used to communicate with the AI or human player.
   All of these messages are logged
   
Long term we should investigate merging these two systems so we can log verbose and debug messages if desired.
"""