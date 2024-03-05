import os
from datetime import datetime
from typing import Optional, Type

from colorama import Fore, Style

from game_utils import *
from output_formats import *
from player import Player
from prompts import fetch_prompt, format_prompt
from message import Message
from agent_interfaces import HumanAgentCLI, OpenAIAgentInterface, HumanAgentInterface

# Default Values
NUMBER_OF_PLAYERS = 6
WINNING_SCORE = 3


class Game:
    """The main game class, handles the game logic and player interactions."""

    number_of_players = NUMBER_OF_PLAYERS
    """The number of players in the game."""
    winning_score = WINNING_SCORE
    """The Number of points required to win the game."""
    chameleon_ids: List[str] = []
    """Record of which player was the chameleon for each round."""
    herd_animals: List[str] = []
    """Record of what animal was the herd animal for each round."""
    chameleon_guesses: List[str] = []
    """Record of what animal the chameleon guessed for each round."""
    herd_vote_tallies: List[List[dict]] = []
    """Record of the votes of each herd member for the chameleon for each round."""

    def __init__(
            self,
            number_of_players: int = NUMBER_OF_PLAYERS,
            human_name: str = None,
            human_interface: Type[HumanAgentInterface] = HumanAgentCLI,
            verbose: bool = False,
            debug: bool = False
    ):
        # Game ID
        self.game_id = game_id()
        self.start_time = datetime.now().strftime('%y%m%d-%H%M%S')

        # Gather Player Names
        if human_name:
            ai_names = random_names(number_of_players - 1, human_name)
            self.human_index = random_index(number_of_players)
        else:
            ai_names = random_names(number_of_players)
            self.human_index = None

        # Add Players
        self.players = []

        for i in range(0, number_of_players):
            player_id = f"{self.game_id}-{i + 1}"

            if self.human_index == i:
                name = human_name
                interface = human_interface(player_id)
            else:
                name = ai_names.pop()
                interface = OpenAIAgentInterface(player_id)

            self.players.append(Player(name, player_id, interface))

        self.verbose = verbose
        """If True, the game will display verbose messages to the player."""
        self.debug = debug
        """If True, the game will display debug messages to the player."""

        # Add Observer - an Agent who can see all the messages, but doesn't actually play
        if (self.verbose or self.debug) and not self.human_index:
            self.observer = HumanAgentCLI("{self.game_id}-observer")
        else:
            self.observer = None

    def player_from_id(self, player_id: str) -> Player:
        """Returns a player from their ID."""
        return next((player for player in self.players if player.id == player_id), None)

    def player_from_name(self, name: str) -> Player:
        """Returns a player from their name."""
        return next((player for player in self.players if player.name == name), None)

    @property
    def chameleon(self) -> Player:
        """Returns the current chameleon."""
        return self.player_from_id(self.chameleon_ids[-1])

    @property
    def herd_animal(self) -> str:
        """Returns the current herd animal."""
        return self.herd_animals[-1]

    @property
    def chameleon_guess(self) -> str:
        """Returns the current chameleon guess."""
        return self.chameleon_guesses[-1]

    @property
    def herd_vote_tally(self) -> List[dict]:
        """Returns the current herd vote tally."""
        return self.herd_vote_tallies[-1]

    def observer_message(self, message: Message):
        """Sends a message to the observer if there is one."""
        if self.observer:
            self.observer.add_message(message)

    def game_message(
            self, content: str,
            recipient: Optional[Player] = None,  # If None, message is broadcast to all players
            exclude: bool = False  # If True, the message is broadcast to all players except the chosen player
    ):
        """Sends a message to a player. No response is expected, however it will be included next time the player is prompted"""
        message = Message(type="info", content=content)

        if exclude or not recipient:
            for player in self.players:
                if player != recipient:
                    player.interface.add_message(message)
            self.observer_message(message)
        else:
            recipient.interface.add_message(message)

    def verbose_message(self, content: str):
        """Sends a message for the human player to read. No response is expected."""
        if self.verbose:
            message = Message(type="verbose", content=content)
            if self.human_index:
                self.players[self.human_index].interface.add_message(message)
            self.observer_message(message)

    def debug_message(self, content: str):
        """Sends a message for a human observer. These messages contain secret information about the players such as their role."""
        if self.debug:
            message = Message(type="debug", content=content)
            if self.human_index:
                self.players[self.human_index].interface.add_message(message)
            self.observer_message(message)


    async def start(self):
        """Sets up the game. This includes assigning roles and gathering player names."""
        self.game_message(fetch_prompt("game_rules"))

        winner = None
        round_number = 0

        # while not winner:
        #     round_results = await self.run_round()
        #     round_number += 1

            # # Check for a Winner
            # for player in self.players:
            #     if player.points >= self.winning_score:
            #         winner = player # ignoring the possibility of a tie for now

        self.setup_round()

        self.run_round()

        self.resolve_round()

        # # Log Game Info
        # game_log = {
        #     "game_id": self.game_id,
        #     "start_time": self.start_time,
        #     "number_of_players": len(self.players),
        #     "human_player": self.players[self.human_index].id if self.human_index else "None",
        # }

    def setup_round(self):
        """Sets up the round. This includes assigning roles and gathering player names."""
        # Choose Animal
        herd_animal = random_animal()
        self.herd_animals.append(herd_animal)
        self.debug_message(f"The secret animal is {herd_animal}.")

        # Assign Roles
        chameleon_index = random_index(len(self.players))
        self.chameleon_ids.append(self.players[chameleon_index].id)

        for i, player in enumerate(self.players):
            if i == chameleon_index:
                player.assign_role("chameleon")
                self.game_message(fetch_prompt("assign_chameleon"), player)
                self.debug_message(f"{player.name} is the Chameleon!")
            else:
                player.assign_role("herd")
                self.game_message(format_prompt("assign_herd", herd_animal=herd_animal), player)

    def run_round(self):
        """Starts the round."""
        # Phase I: Collect Player Animal Descriptions

        self.game_message(f"Each player will now take turns describing themselves:")
        for i, current_player in enumerate(self.players):
            self.player_turn_animal_description(current_player)

        # Phase II: Chameleon Guesses the Animal

        self.player_turn_chameleon_guess(self.chameleon)

        # Phase III: The Herd Votes for who they think the Chameleon is
        self.game_message("The Chameleon has guessed the animal. Now the Herd will vote on who they think the chameleon is.")

        self.herd_vote_tallies.append([])
        for current_player in self.players:
            if current_player.role == "herd":
                self.player_turn_herd_vote(current_player)




    def player_turn_animal_description(self, player: Player):
        """Handles a player's turn to describe themselves."""
        if player.interface.is_ai:
            self.verbose_message(f"{player.name} is thinking...")

        prompt = fetch_prompt("player_describe_animal")

        # Get Player Animal Description
        message = Message(type="prompt", content=prompt)
        response = player.interface.respond_to_formatted(message, AnimalDescriptionFormat)

        self.game_message(f"{player.name}: {response.description}", player, exclude=True)

    def player_turn_chameleon_guess(self, chameleon: Player):
        """Handles the Chameleon's turn to guess the secret animal."""
        self.game_message("All players have spoken. The Chameleon will now guess the secret animal...")
        if chameleon.interface.is_ai or self.observer:
            self.verbose_message("The Chameleon is thinking...")

        prompt = fetch_prompt("chameleon_guess_animal")

        message = Message(type="prompt", content=prompt)
        response = chameleon.interface.respond_to_formatted(message, ChameleonGuessFormat)

        self.chameleon_guesses.append(response.animal)

    def player_turn_herd_vote(self, player: Player):
        """Handles a player's turn to vote for the Chameleon."""
        if player.interface.is_ai:
            self.verbose_message(f"{player.name} is thinking...")

        prompt = fetch_prompt("vote")

        # Get Player Vote
        message = Message(type="prompt", content=prompt)
        other_player_names = [p.name for p in self.players if p != player]
        response = player.interface.respond_to_formatted(message, HerdVoteFormat, player_names=other_player_names)

        if player.interface.is_ai:
            self.debug_message(f"{player.name} voted for {response.vote}")

        voted_for_player = self.player_from_name(response.vote)

        # Add Vote to Player Votes
        self.herd_vote_tally.append({"voter": player.id, "voted_for": voted_for_player.id})

    def resolve_round(self):
        """Resolves the round, assigns points, and prints the results."""
        self.game_message("All players have voted!")
        for vote in self.herd_vote_tally:
            voter = self.player_from_id(vote["voter"])
            voted_for = self.player_from_id(vote["voted_for"])
            self.game_message(f"{voter.name} voted for {voted_for.name}")

        accused_player_id = count_chameleon_votes(self.herd_vote_tally)

        self.game_message(f"The round is over. Calculating results...")
        self.game_message(
            f"The Chameleon was {self.chameleon.name}, and they guessed the secret animal was {self.chameleon_guess}.")
        self.game_message(f"The secret animal was actually was {self.herd_animal}.")

        if accused_player_id:
            accused_name = self.player_from_id(accused_player_id).name
            self.game_message(f"The Herd voted for {accused_name} as the Chameleon.")
        else:
            self.game_message(f"The Herd could not come to a consensus.")

        # Point Logic
        # If the Chameleon guesses the correct animal    =   +1 Point to the Chameleon
        if self.chameleon_guess.lower() == self.herd_animal.lower():
            self.chameleon.points += 1

        # If the Chameleon guesses the incorrect animal  =   +1 Point to each Herd player
        else:
            for player in self.players:
                if player.role == "herd":
                    player.points += 1
        # If a Herd player votes for the Chameleon       =   +1 Point to that player
        for vote in self.herd_vote_tally:
            if vote["voted_for"] == self.chameleon.id:
                self.player_from_id(vote['voter']).points += 1

        # If the Herd fails to accuse the Chameleon      =   +1 Point to the Chameleon
        if not accused_player_id or accused_player_id != self.chameleon.id:
            self.chameleon.points += 1

        # Print Scores
        player_points = "\n".join([f"{player.name}: {player.points}" for player in self.players])
        self.game_message(f"Current Game Score:\n{player_points}")


