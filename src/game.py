from game_utils import fetch_prompt, random_animal, random_names, random_index
from player import Player

# Default Values
NUMBER_OF_PLAYERS = 5

class Game:
    def __init__(self,
            human_name: str = None,
            number_of_players: int = NUMBER_OF_PLAYERS
        ):

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

            self.players.append(Player(name, controller, role))


        self.player_responses = []

        print("Game Created")


    def broadcast(self, message):
        """Sends a message to all the players, no response required."""
        for player_index in range(0, len(self.players)):
            self.players[player_index].add_message(message)
            if self.human_index == player_index:
                print(message)

    def format_responses(self) -> str:
        """Formats the responses of the players into a single string."""
        return "\n".join([f" - {response['sender']}: {response['response']}" for response in self.player_responses])

    def get_player_names(self) -> list[str]:
        """Returns the names of the players."""
        return [player.name for player in self.players]

    def start(self):
        """Starts the game."""
        print("Welcome to Chameleon! This is a social deduction game powered by LLMs.")

        self.player_responses = []
        herd_animal = random_animal()

        # Collect Player Animal Descriptions
        for player in self.players:
            match player.role:
                case "herd":
                    prompt_template = fetch_prompt("herd_animal")
                    prompt = prompt_template.format(animal=herd_animal, player_responses=self.format_responses())

                case "chameleon":
                    prompt_template = fetch_prompt("chameleon_animal")
                    prompt = prompt_template.format(player_responses=self.format_responses())

            response = player.collect_input(prompt)
            self.player_responses.append({"sender": player.name, "response": response})

        self.player_votes = []

        # Show All Player Responses
        self.broadcast(self.format_responses())

        # Chameleon Decides if they want to guess the animal
        # TODO: Add Chameleon Guess Decision Logic
        chameleon_will_guess = False

        if chameleon_will_guess:
            # Chameleon Guesses Animal
            # TODO: Add Chameleon Guessing Logic
            pass
        else:
            # All Players Vote for Chameleon
            for player in self.players:
                prompt_template = fetch_prompt("vote")
                prompt = prompt_template.format(players=self.get_player_names())

                response = player.collect_input(prompt)
                self.player_responses.append(response)

        # Assign Points
        # Chameleon Wins - 3 Points
        # Herd Wins by Failed Chameleon Guess - 1 Point (each)
        # Herd Wins by Correctly Guessing Chameleon - 2 points (each)

    @staticmethod
    def validate_animal_description(self, description: str) -> bool:
        """Validates that the description starts with I and is less than 10 words."""
        if not description.startswith("I"):
            return False

        if len(description.split(" ")) > 10:
            return False

        return True

    def validate_vote(self, vote: str) -> bool:
        """Validates that the vote is for a valid player."""
        player_names = [player.name.lower() for player in self.players]
        return vote.lower() in player_names