from typing import Literal
import logging

from agent_interfaces import AgentInterface

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
            player_id: str,
            interface: AgentInterface
    ):
        self.name = name
        self.id = player_id
        self.interface = interface

    def assign_role(self, role: Role):
        self.role = role
        if role == "chameleon":
            self.rounds_played_as_chameleon += 1
        elif role == "herd":
            self.rounds_played_as_herd += 1
