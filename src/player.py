from typing import Literal, List, Type

from pydantic import BaseModel, Field

from agent_interfaces import HumanAgentCLI, BaseAgentInterface
from message import MessageType

Role = Literal["chameleon", "herd"]


# Abstraction is a WIP and a little premature, but I'd like to reuse this framework to create more Games in the future
class Player(BaseModel):
    """Base class for a player"""

    name: str
    """The name of the player."""
    player_id: str
    """The id of the player."""
    game_id: str
    """The id of the game the player is in."""
    interface: BaseAgentInterface = Field(exclude=True)
    """The interface used by the agent controlling the player to communicate with the game."""
    message_level: str = "info"
    """The level of messages that the player will receive. Can be "info", "verbose", or "debug"."""

    def can_receive_message(self, message_type: MessageType) -> bool:
        """Returns True if the player can receive a message of the type."""
        if message_type == "verbose" and self.message_level not in ["verbose", "debug"]:
            return False
        elif message_type == "debug" and self.message_level != "debug":
            return False
        else:
            return True

    @classmethod
    def observer(
            cls,
            game_id: str,
            message_level: str = "verbose",
            interface_type: Type[BaseAgentInterface] = HumanAgentCLI,
            log_messages: bool = False
    ):
        """Creates an observer player."""
        name = "Observer"
        player_id = f"{game_id}-observer"
        interface = interface_type(agent_id=player_id)

        return cls(name=name, player_id=player_id, game_id=game_id, interface=interface, message_level=message_level)


class PlayerSubclass(Player):
    @classmethod
    def from_player(cls, player: Player):
        """Creates a new instance of the subclass from a player instance."""
        fields = player.model_dump()
        fields['interface'] = player.interface
        return cls(**fields)


class ChameleonPlayer(PlayerSubclass):
    """A player in the game Chameleon"""

    points: int = 0
    """The number of points the player has."""
    roles: List[Role] = []
    """The role of the player in the game. Can be "chameleon" or "herd". This changes every round."""

    def assign_role(self, role: Role):
        self.roles.append(role)

    @property
    def role(self) -> Role:
        """The current role of the player."""
        return self.roles[-1]

    @property
    def rounds_played_as_chameleon(self) -> int:
        """The number of times the player has been the Chameleon."""
        return self.roles.count("chameleon")

    @property
    def rounds_played_as_herd(self) -> int:
        """The number of times the player has been in the Herd."""
        return self.roles.count("herd")
