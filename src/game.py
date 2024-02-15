import os

from game_utils import *
from models import *
from player import Player
from parser import ParserKani

# Default Values
NUMBER_OF_PLAYERS = 5

class Game:

    log_dir = os.path.join(os.pardir, "experiments")
    player_log_file = "{game_id}-{role}-{player_num}.jsonl"
    parser_log_file = "{game_id}-parser.jsonl"

    def __init__(self,
            human_name: str = None,
            number_of_players: int = NUMBER_OF_PLAYERS
        ):

        # Game ID
        self.game_id = game_id()

        # Gather Player Names
        if human_name:
            ai_names = random_names(number_of_players - 1)
            self.human_index = random_index(number_of_players)
        else:
            ai_names = random_names(number_of_players)

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
                controller = "ai"

            if self.chameleon_index == i:
                role = "chameleon"
            else:
                role = "herd"

            log_path = os.path.join(self.log_dir, self.player_log_file.format(game_id=self.game_id, role=role, player_num=i))

            self.players.append(Player(name, controller, role, log_filepath=log_path))

        # Game State
        self.player_responses = []

        # Parser
        parser_log_path = os.path.join(self.log_dir, self.parser_log_file.format(game_id=self.game_id))
        self.parser = ParserKani.default(parser_log_path)

    def format_responses(self) -> str:
        """Formats the responses of the players into a single string."""
        return "\n".join([f" - {response['sender']}: {response['response']}" for response in self.player_responses])

    def get_player_names(self) -> list[str]:
        """Returns the names of the players."""
        return [player.name for player in self.players]

    async def start(self):
        """Starts the game."""
        # print("Welcome to Chameleon! This is a social deduction game powered by LLMs.")

        self.player_responses = []
        herd_animal = random_animal()

        game_over = False

        while not game_over:
            # Phase I: Collect Player Animal Descriptions
            for player in self.players:
                if player.role == "chameleon":
                    prompt_template = fetch_prompt("chameleon_animal")
                    prompt = prompt_template.format(player_responses=self.format_responses())
                else:
                    prompt_template = fetch_prompt("herd_animal")
                    prompt = prompt_template.format(animal=herd_animal, player_responses=self.format_responses())

                # Get Player Animal Description
                response = await player.respond_to(prompt)
                # Parse Animal Description
                output = await self.parser.parse(prompt, response, AnimalDescriptionModel)

                self.player_responses.append({"sender": player.name, "response": output.description})

            # Phase II: Chameleon Decides if they want to guess the animal (secretly)
            chameleon_will_guess = False

            # Phase III: Chameleon Guesses Animal or All Players Vote for Chameleon
            if chameleon_will_guess:
                # Chameleon Guesses Animal
                # TODO: Add Chameleon Guessing Logic
                pass
            else:
                # All Players Vote for Chameleon
                player_votes = []
                for player in self.players:
                    prompt_template = fetch_prompt("vote")
                    prompt = prompt_template.format(player_responses=self.format_responses())

                    # Get Player Vote
                    response = await player.respond_to(prompt)
                    # Parse Vote
                    output = await self.parser.parse(prompt, response, VoteModel)

                    # check if a valid player was voted for...

                    # Add Vote to Player Votes
                    player_votes.append(output.vote)

                print(player_votes)

                # Count Votes
                accused_player = count_chameleon_votes(player_votes)

                if accused_player:
                    game_over = True
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


