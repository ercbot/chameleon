import os
from datetime import datetime

from colorama import Fore, Style

from game_utils import *
from models import *
from player import Player
from prompts import fetch_prompt, format_prompt

# Default Values
NUMBER_OF_PLAYERS = 5

game_type = "streamlit"

class Game:
    log_dir = os.path.join(os.pardir, "experiments")
    player_log_file = "{player_id}.jsonl"
    game_log_file = "{game_id}-game.jsonl"

    def __init__(
            self,
            number_of_players: int = NUMBER_OF_PLAYERS,
            human_name: str = None,
            verbose: bool = False # If there is a human player game will always be verbose
    ):

        # This function is used to broadcast messages to the human player.
        # They are purely informative and do not affect the game.

        # Game ID
        self.game_id = game_id()
        self.start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_dir = os.path.join(self.log_dir, f"{self.start_time}-{self.game_id}")
        os.makedirs(self.log_dir, exist_ok=True)

        # Choose Chameleon
        self.chameleon_index = random_index(number_of_players)

        # Gather Player Names
        if human_name:
            ai_names = random_names(number_of_players - 1, human_name)
            self.human_index = random_index(number_of_players)
            self.verbose = True
        else:
            ai_names = random_names(number_of_players)
            self.human_index = None
            self.verbose = verbose

        # Add Players
        self.players = []
        for i in range(0, number_of_players):
            if self.human_index == i:
                name = human_name
                controller = "human"
            else:
                name = ai_names.pop()
                controller = "openai"

            if self.chameleon_index == i:
                role = "chameleon"
            else:
                role = "herd"

            player_id = f"{self.game_id}-{i + 1}-{role}"

            log_path = os.path.join(
                self.log_dir,
                self.player_log_file.format(player_id=player_id)
            )

            self.players.append(Player(name, controller, role, player_id, log_filepath=log_path))

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


    def game_message(self, message: str, excluded_player: Player = None):
        """Sends a message to all players. No response is expected."""
        for player in self.players:
            if player != excluded_player:
                player.prompt_queue.append(message)
                if player.controller_type == "human":
                    print(message)

    @staticmethod
    async def instructional_message(message: str, player: Player,  output_format: Type[BaseModel]):
        """Sends a message to a specific player and gets their response."""

        response = await player.respond_to(message, output_format)
        return response

    # The following methods are used to broadcast messages to a human.
    def verbose_message(self, message: str):
        """Sends a message for the human player to read. No response is expected."""
        if self.verbose:
            print(Fore.GREEN + message + Style.RESET_ALL)

    def debug_message(self, message: str):
        """Sends a message for a human observer. These messages contain secret information about the players such as their role."""
        if self.debug:
            print(Fore.YELLOW + message + Style.RESET_ALL)

    # def game_setup(self):
    #     """Sets up the game. This includes assigning roles and gathering player names."""
    #     self.verbose_message("Setting up the game...")
    #
    #     for i, player in enumerate(self.players):
    #         if player.controller_type != "human":
    #             self.verbose_message(f"Player {i + 1}: {player.name} - {player.role}")


    async def start(self):
        """Starts the game."""
        self.verbose_message(("Welcome to Chameleon! This is a social deduction game powered by LLMs."))
        self.game_message(fetch_prompt("game_rules"))

        self.player_responses = []
        herd_animal = random_animal()

        winner = None

        while not winner:
            # Phase I: Collect Player Animal Descriptions
            self.game_message(f"Each player will now take turns describing themselves.")
            for current_player in self.players:
                if current_player.controller_type != "human":
                    self.verbose_message(f"It's {current_player.name}'s turn to describe the animal.")
                    self.verbose_message(f"{current_player.name} is thinking...")

                if current_player.role == "chameleon":
                    prompt = format_prompt("chameleon_animal", player_responses=self.format_responses())
                else:
                    prompt = format_prompt("herd_animal", animal=herd_animal, player_responses=self.format_responses())

                # Get Player Animal Description
                response = await self.instructional_message(prompt, current_player, AnimalDescriptionModel)

                self.player_responses.append({"sender": current_player.name, "response": response.description})

                self.game_message(f"{current_player.name}: {response.description}", current_player)


            # Phase II: Chameleon Decides if they want to guess the animal (secretly)
            self.game_message("All players have spoken. Now the chameleon will decide if they want to guess the animal or not.")
            if self.human_index != self.chameleon_index:
                self.verbose_message("The chameleon is thinking...")

            chameleon = self.players[self.chameleon_index]
            prompt = format_prompt("chameleon_guess_decision", player_responses=self.format_responses(exclude=chameleon.name))
            response = await chameleon.respond_to(prompt, ChameleonGuessDecisionModel)

            if response.decision.lower() == "guess":
                chameleon_will_guess = True
            else:
                chameleon_will_guess = False

            # Phase III: Chameleon Guesses Animal or All Players Vote for Chameleon
            if chameleon_will_guess:
                # Chameleon Guesses Animal
                self.game_message(f"{chameleon.name} has revealed themselves to be the chameleon and is guessing the animal...", chameleon)

                prompt = fetch_prompt("chameleon_guess_animal")

                response = await self.players[self.chameleon_index].respond_to(prompt, ChameleonGuessAnimalModel)

                self.game_message(f"The chameleon guesses: {response.animal}")

                if response.animal.lower() == herd_animal.lower():
                    self.game_message(f"The Chameleon has guessed the correct animal! The Chameleon wins!")
                    winner = "chameleon"
                else:
                    self.game_message(f"The Chameleon is incorrect, the true animal is a {herd_animal}. The Herd wins!")
                    winner = "herd"


            else:
                # All Players Vote for Chameleon
                self.game_message("The chameleon has decided not to guess the animal. Now all players will vote on who they think the chameleon is.")

                player_votes = []
                for player in self.players:
                    if player.controller_type != "human":
                        self.verbose_message(f"It's {player.name}'s turn to vote.")
                        self.verbose_message(f"{player.name} is thinking...")

                    prompt = format_prompt("vote", player_responses=self.format_responses(exclude=player.name))

                    # Get Player Vote
                    response = await player.respond_to(prompt, VoteModel)

                    # check if a valid player was voted for...

                    # Add Vote to Player Votes
                    player_votes.append(response.vote)

                self.game_message("All players have voted!")
                self.game_message(f"Votes: {player_votes}")

                # Count Votes
                accused_player = count_chameleon_votes(player_votes)

                if accused_player:
                    self.game_message(f"The Herd has accused {accused_player} of being the Chameleon!")
                    if accused_player == self.players[self.chameleon_index].name:
                        self.game_message(f"{accused_player} is the Chameleon! The Herd wins!")
                        winner = "herd"
                    else:
                        self.game_message(f"{accused_player} is not the Chameleon! The Chameleon wins!")
                        self.game_message(f"The real Chameleon was {chameleon.name}.")
                        winner = "chameleon"
                else:
                    self.game_message("The Herd could not come to a consensus. We will play another round!")


        # Assign Points
        # Chameleon Wins - 3 Points
        # Herd Wins by Failed Chameleon Guess - 1 Point (each)
        # Herd Wins by Correctly Guessing Chameleon - 2 points (each)

        # Log Game Info
        game_log = {
            "game_id": self.game_id,
            "start_time": self.start_time,
            "herd_animal": herd_animal,
            "number_of_players": len(self.players),
            "human_player": self.players[self.human_index].id if self.human_index else "None",
            "chameleon": self.players[self.chameleon_index].id,
            "winner": winner
        }
        game_log_path = os.path.join(self.log_dir, self.game_log_file.format(game_id=self.game_id))

        log(game_log, game_log_path)
