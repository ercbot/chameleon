import os
from datetime import datetime
from typing import Optional, Type

from colorama import Fore, Style

from game_utils import *
from models import *
from player import Player
from prompts import fetch_prompt, format_prompt
from message import Message
from agent_interfaces import HumanAgentCLI, OpenAIAgentInterface

# Default Values
NUMBER_OF_PLAYERS = 6
WINNING_SCORE = 11


class Game:

    log_dir = os.path.join(os.pardir, "experiments")
    """The directory where the logs will be saved."""
    player_log_file_template = "{player_id}.jsonl"
    """Template for the name of the log file for each player."""
    game_log_file_template = "{game_id}-game.jsonl"
    """Template for the name of the log file for the game."""
    number_of_players = NUMBER_OF_PLAYERS
    """The number of players in the game."""
    winning_score = WINNING_SCORE
    """The Number of points required to win the game."""

    def __init__(
            self,
            number_of_players: int = NUMBER_OF_PLAYERS,
            human_name: str = None,
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

        self.verbose = verbose
        """If True, the game will display verbose messages to the player."""
        self.debug = debug
        """If True, the game will display debug messages to the player."""

        # Add Players
        self.players = []
        for i in range(0, number_of_players):
            player_id = f"{self.game_id}-{i + 1}"

            if self.human_index == i:
                name = human_name
                interface = HumanAgentCLI(player_id)
            else:
                name = ai_names.pop()
                interface = OpenAIAgentInterface(player_id)

            self.players.append(Player(name, player_id, interface))

        # Add Observer - an Agent who can see all the messages, but doesn't actually play
        if self.verbose or self.debug and not self.human_index:
            self.observer = HumanAgentCLI("{self.game_id}-observer")
        else:
            self.observer = None

        # Game State
        self.player_responses = []

    def format_responses(self, exclude: str = None) -> str:
        """Formats the responses of the players into a single string."""
        if len(self.player_responses) == 0:
            return "None, you are the first player!"
        else:
            formatted_responses = ""
            for response in self.player_responses:
                # Used to exclude the player who is currently responding, so they don't vote for themselves like a fool
                if response["sender"] != exclude:
                    formatted_responses += f" - {response['sender']}: {response['response']}\n"

            return formatted_responses

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

        await self.run_round()

        # Log Game Info
        game_log = {
            "game_id": self.game_id,
            "start_time": self.start_time,
            "number_of_players": len(self.players),
            "human_player": self.players[self.human_index].id if self.human_index else "None",
        }
        game_log_path = os.path.join(self.log_dir, self.game_log_file_template.format(game_id=self.game_id))

        log(game_log, game_log_path)

    async def run_round(self):
        """Starts the round."""

        # Phase I: Choose Animal and Assign Roles

        herd_animal = random_animal()
        self.debug_message(f"The secret animal is {herd_animal}.")

        chameleon_index = random_index(len(self.players))
        chameleon = self.players[chameleon_index]

        for i, player in enumerate(self.players):
            if i == chameleon_index:
                player.assign_role("chameleon")
                self.game_message(fetch_prompt("assign_chameleon"), player)
                self.debug_message(f"{player.name} is the Chameleon!")
            else:
                player.assign_role("herd")
                self.game_message(format_prompt("assign_herd", herd_animal=herd_animal), player)

        # Phase II: Collect Player Animal Descriptions

        self.game_message(f"Each player will now take turns describing themselves:")
        for i, current_player in enumerate(self.players):
            if current_player.interface.is_ai:
                self.verbose_message(f"{current_player.name} is thinking...")

            prompt = fetch_prompt("player_describe_animal")

            # Get Player Animal Description
            message = Message(type="prompt", content=prompt)
            response = current_player.interface.respond_to_formatted(message, AnimalDescriptionModel)

            self.player_responses.append({"sender": current_player.name, "response": response.description})

            self.game_message(f"{current_player.name}: {response.description}", current_player, exclude=True)

        # Phase III: Chameleon Guesses the Animal

        self.game_message("All players have spoken. The Chameleon will now guess the secret animal...")
        if chameleon.interface.is_ai or self.observer:
            self.verbose_message("The Chameleon is thinking...")

        prompt = fetch_prompt("chameleon_guess_animal")

        message = Message(type="prompt", content=prompt)
        response = chameleon.interface.respond_to_formatted(message, ChameleonGuessAnimalModel)

        chameleon_animal_guess = response.animal

        # Phase IV: The Herd Votes for who they think the Chameleon is
        self.game_message("The Chameleon has guessed the animal. Now the Herd will vote on who they think the chameleon is.")

        player_votes = []
        for player in self.players:
            if player.role == "herd":
                if player.interface.is_ai:
                    self.verbose_message(f"{player.name} is thinking...")

                prompt = format_prompt("vote", player_responses=self.format_responses(exclude=player.name))

                # Get Player Vote
                message = Message(type="prompt", content=prompt)
                response = player.interface.respond_to_formatted(message, VoteModel)

                # check if a valid player was voted for...

                # Add Vote to Player Votes
                player_votes.append({"voter": player, "vote": response.vote})
                if player.interface.is_ai:
                    self.debug_message(f"{player.name} voted for {response.vote}")


        self.game_message("All players have voted!")
        formatted_votes = '\n'.join([f'{vote["voter"].name}: {vote["vote"]}' for vote in player_votes])
        self.game_message(f"Votes:\n{formatted_votes}")

        # Count Votes
        accused_player = count_chameleon_votes(player_votes)

        # Phase V: Assign Points

        self.game_message(f"The round is over. Caclulating results...")
        self.game_message(
            f"The Chameleon was {chameleon.name}, and they guessed the secret animal was {chameleon_animal_guess}.")
        self.game_message(f"The secret animal was actually was {herd_animal}.")

        if accused_player:
            self.game_message(f"The Herd voted for {accused_player} as the Chameleon.")
        else:
            self.game_message(f"The Herd could not come to a consensus.")

        # Point Logic
        # If the Chameleon guesses the correct animal    =   +1 Point to the Chameleon
        if chameleon_animal_guess.lower() == herd_animal.lower():
            chameleon.points += 1
        # If the Chameleon guesses the incorrect animal  =   +1 Point to each Herd player
        else:
            for player in self.players:
                if player.role == "herd":
                    player.points += 1
        # If a Herd player votes for the Chameleon       =   +1 Point to that player
        for vote in player_votes:
            if vote["vote"] == chameleon.name:
                vote['voter'].points += 1

        # If the Herd fails to accuse the Chameleon      =   +1 Point to the Chameleon
        if not accused_player or accused_player != chameleon.name:
            chameleon.points += 1

        # Check for a Winner
        player_points = "\n".join([f"{player.name}: {player.points}" for player in self.players])

        self.game_message(f"Current Game Score: {player_points}")

        # Log Round Info
        round_log = {
            "herd_animal": herd_animal,
            "chameleon_name": chameleon.name,
            "chameleon_guess": chameleon_animal_guess,
            "herd_votes": player_votes,
        }
