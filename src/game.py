from typing import Optional, Type, List, ClassVar

from pydantic import BaseModel, Field

from game_utils import *
from message import Message, MessageType
from agent_interfaces import HumanAgentCLI, OpenAIAgentInterface, HumanAgentInterface
from player import Player
from data_collection import save

# Abstracting the Game Class is a WIP so that future games can be added
class Game(BaseModel):
    """Base class for all games."""

    # Required

    players: List[Player] = Field(exclude=True)
    """The players in the game."""
    observer: Optional[Player]
    """An observer who can see all public messages, but doesn't actually play."""
    game_id: str
    """The unique id of the game."""

    # Default

    winner_id: str | None = None
    """The id of the player who has won the game."""
    game_state: str = Field("game_start", exclude=True)
    """Keeps track of the current state of the game."""
    awaiting_input: bool = Field(False, exclude=True)
    """Whether the game is currently awaiting input from a player."""

    # Class Variables

    number_of_players: ClassVar[int]
    """The number of players in the game."""
    player_class: ClassVar[Type[Player]] = Player
    """The class of the player used in the game."""

    def player_from_id(self, player_id: str) -> Player:
        """Returns a player from their ID."""
        return next((player for player in self.players if player.player_id == player_id), None)

    def player_from_name(self, name: str) -> Player:
        """Returns a player from their name."""
        return next((player for player in self.players if player.name == name), None)

    def game_message(
            self,
            content: str,
            recipient: Optional[Player] = None,  # If None, message is broadcast to all players
            exclude: bool = False,  # If True, the message is broadcast to all players except the chosen player
            message_type: MessageType = "info"
    ):
        """
        Sends a message to a player or all players.
        If no recipient is specified, the message is broadcast to all players.
        If exclude is True, the message is broadcast to all players except the recipient.
        Some message types are only available to player with access (e.g. verbose, debug).
        """
        message = Message(type=message_type, content=content)

        if exclude or not recipient:
            for player in self.players + [self.observer] if self.observer else self.players:
                if player != recipient and player.can_receive_message(message_type):
                    player.interface.add_message(message)
        else:
            recipient.interface.add_message(message)

    def verbose_message(self, content: str, **kwargs):
        """
        Sends a verbose message to all players capable of receiving them.
        Verbose messages are used to communicate in real time what is happening that cannot be seen publicly.

        Ex: "Abby is thinking..."
        """
        self.game_message(content, **kwargs, message_type="verbose")

    def debug_message(self, content: str, **kwargs):
        """
        Sends a debug message to all players capable of receiving them.
        Debug messages usually contain secret information and should only be sent when it wouldn't spoil the game.

        Ex: "Abby is the chameleon."
        """
        self.game_message(content, **kwargs, message_type="debug")

    def run_game(self):
        """Runs the game."""
        raise NotImplementedError("The run_game method must be implemented by the subclass.")

    def end_game(self):
        """Ends the game and declares a winner."""
        for player in self.players:
            save(player)

        save(self)



    @classmethod
    def from_human_name(
            cls, human_name: str = None,
            human_interface: Type[HumanAgentInterface] = HumanAgentCLI,
            human_message_level: str = "verbose"
    ):
        """
        Instantiates a game with a human player if a name is provided.
        Otherwise, the game is instantiated with all AI players and an observer.
        """
        game_id = generate_game_id()

        # Gather Player Names
        if human_name:
            ai_names = random_names(cls.number_of_players - 1, human_name)
            human_index = random_index(cls.number_of_players)
        else:
            ai_names = random_names(cls.number_of_players)
            human_index = None

        # Add Players
        players = []

        for i in range(0, cls.number_of_players):
            player_id = f"{game_id}-{i + 1}"
            player_dict = {"game_id": game_id, "player_id": player_id}

            if human_index == i:
                player_dict["name"] = human_name
                player_dict["interface"] = human_interface(agent_id=player_id)
                player_dict["message_level"] = human_message_level
            else:
                player_dict["name"] = ai_names.pop()
                # all AI players use the OpenAI interface for now - this can be changed in the future
                player_dict["interface"] = OpenAIAgentInterface(agent_id=player_id)
                player_dict["message_level"] = "info"

            players.append(cls.player_class(**player_dict))

        # Add Observer - an Agent who can see all the messages, but doesn't actually play
        if human_index is None:
            observer = Player.observer(game_id, interface_type=human_interface)
        else:
            observer = None

        return cls(game_id=game_id, players=players, observer=observer)



