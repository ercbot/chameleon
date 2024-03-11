from typing import Literal, List, Type

from agent_interfaces import AgentInterface, HumanAgentCLI, BaseAgentInterface
from message import MessageType

Role = Literal["chameleon", "herd"]


# Abstraction is a WIP and a little premature, but I'd like to reuse this framework to create more Games in the future
class Player:
    """Base class for a player"""

    def __init__(self,
                 name: str,
                 player_id: str,
                 interface: BaseAgentInterface,
                 message_level: str = "info"
                 ):
        self.name = name
        """The name of the player."""
        self.id = player_id
        """The id of the player."""
        self.interface = interface
        """The interface used by the agent controlling the player to communicate with the game."""
        self.message_level = message_level
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
        player_id = f"{game_id}_observer"
        interface = interface_type(player_id, log_messages)

        return cls(name, player_id, interface, message_level)


class PlayerSubclass(Player):
    @classmethod
    def from_player(cls, player: Player):
        """Creates a new instance of the subclass from a player instance."""
        return cls(player.name, player.id, player.interface, player.message_level)


class ChameleonPlayer(PlayerSubclass):
    """A player in the game Chameleon"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.points: int = 0
        """The number of points the player has."""
        self.roles: List[Role] = []
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
