import os
from datetime import datetime

from game_utils import *
from models import *
from player import Player
from prompts import fetch_prompt, format_prompt

# Default Values
NUMBER_OF_PLAYERS = 5


class Game:
    log_dir = os.path.join(os.pardir, "experiments")
    player_log_file = "{player_id}.jsonl"
    game_log_file = "{game_id}-game.jsonl"

    def __init__(
            self,
            human_name: str = None,
            number_of_players: int = NUMBER_OF_PLAYERS
    ):

        # Game ID
        self.game_id = game_id()
        self.start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_dir = os.path.join(self.log_dir, f"{self.start_time}-{self.game_id}")
        os.makedirs(self.log_dir, exist_ok=True)

        # Gather Player Names
        if human_name:
            ai_names = random_names(number_of_players - 1, human_name)
            self.human_index = random_index(number_of_players)
        else:
            ai_names = random_names(number_of_players)
            self.human_index = None

        # Choose Chameleon
        self.chameleon_index = random_index(number_of_players)

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

    def get_player_names(self) -> list[str]:
        """Returns the names of the players."""
        return [player.name for player in self.players]

    async def start(self):
        """Starts the game."""
        # print("Welcome to Chameleon! This is a social deduction game powered by LLMs.")

        self.player_responses = []
        herd_animal = random_animal()

        winner = None

        while not winner:
            # Phase I: Collect Player Animal Descriptions
            for player in self.players:
                if player.role == "chameleon":
                    prompt = format_prompt("chameleon_animal", player_responses=self.format_responses())
                else:
                    prompt = format_prompt("herd_animal", animal=herd_animal, player_responses=self.format_responses())

                # Get Player Animal Description
                response = await player.respond_to(prompt, AnimalDescriptionModel)

                self.player_responses.append({"sender": player.name, "response": response.description})

            # Phase II: Chameleon Decides if they want to guess the animal (secretly)
            prompt = format_prompt("chameleon_guess_decision", player_responses=self.format_responses())

            response = await self.players[self.chameleon_index].respond_to(prompt, ChameleonGuessDecisionModel)

            if response.decision.lower() == "guess":
                chameleon_will_guess = True
            else:
                chameleon_will_guess = False

            # Phase III: Chameleon Guesses Animal or All Players Vote for Chameleon
            if chameleon_will_guess:
                # Chameleon Guesses Animal
                prompt = fetch_prompt("chameleon_guess_animal")

                response = await self.players[self.chameleon_index].respond_to(prompt, ChameleonGuessAnimalModel)

                if response.animal.lower() == herd_animal.lower():
                    winner = "chameleon"
                else:
                    winner = "herd"

            else:
                # All Players Vote for Chameleon
                player_votes = []
                for player in self.players:
                    prompt = format_prompt("vote", player_responses=self.format_responses())

                    # Get Player Vote
                    response = await player.respond_to(prompt, VoteModel)

                    # check if a valid player was voted for...

                    # Add Vote to Player Votes
                    player_votes.append(response.vote)

                print(player_votes)

                # Count Votes
                accused_player = count_chameleon_votes(player_votes)

                if accused_player:
                    if accused_player == self.players[self.chameleon_index].name:
                        winner = "herd"
                    else:
                        winner = "chameleon"

        print(f"Game Over! The {winner} wins!")

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
