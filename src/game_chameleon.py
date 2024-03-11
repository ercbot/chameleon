from typing import Optional, Type

from game_utils import random_index
from game_utils_chameleon import *
from output_formats import *
from player import ChameleonPlayer, Player
from prompts import fetch_prompt, format_prompt
from message import Message, MessageType
from agent_interfaces import HumanAgentCLI, OpenAIAgentInterface, HumanAgentInterface
from game import Game

# Default Values
NUMBER_OF_PLAYERS = 6
WINNING_SCORE = 3


class ChameleonGame(Game):
    """The main game class, handles the game logic and player interactions."""

    number_of_players = NUMBER_OF_PLAYERS

    winning_score = WINNING_SCORE
    """The Number of points required to win the game."""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Convert the Players to ChameleonPlayers
        self.players: List[ChameleonPlayer] = [ChameleonPlayer.from_player(player) for player in self.players]

        # Instance Variables
        self.chameleon_ids: List[str] = []
        """Record of which player was the chameleon for each round."""
        self.herd_animals: List[str] = []
        """Record of what animal was the herd animal for each round."""
        self.all_animal_descriptions: List[List[dict]] = []
        """Record of the animal descriptions each player has given for each round."""
        self.chameleon_guesses: List[str] = []
        """Record of what animal the chameleon guessed for each round."""
        self.herd_vote_tallies: List[List[dict]] = []
        """Record of the votes of each herd member for the chameleon for each round."""



    @property
    def chameleon(self) -> ChameleonPlayer:
        """Returns the current chameleon."""
        return self.player_from_id(self.chameleon_ids[-1])

    @property
    def herd_animal(self) -> str:
        """Returns the current herd animal."""
        return self.herd_animals[-1]

    @property
    def round_animal_descriptions(self) -> List[dict]:
        """Returns the current animal descriptions."""
        return self.all_animal_descriptions[-1]

    @property
    def chameleon_guess(self) -> str:
        """Returns the current chameleon guess."""
        return self.chameleon_guesses[-1]

    @property
    def herd_vote_tally(self) -> List[dict]:
        """Returns the current herd vote tally."""
        return self.herd_vote_tallies[-1]

    @property
    def round_number(self) -> int:
        """Returns the current round number."""
        return len(self.herd_animals)

    def format_animal_descriptions(self, exclude: Player = None) -> str:
        """Formats the animal description responses of the players into a single string."""
        formatted_responses = ""
        for response in self.round_animal_descriptions:
            # Used to exclude the player who is currently responding, so they don't vote for themselves like a fool
            if response["player_id"] != exclude.id:
                player = self.player_from_id(response["player_id"])
                formatted_responses += f" - {player.name}: {response['description']}\n"

        return formatted_responses

    async def run_game(self):
        """Sets up the game. This includes assigning roles and gathering player names."""
        self.game_message(fetch_prompt("game_rules"))

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

        # Empty Animal Descriptions
        self.all_animal_descriptions.append([])

        # Empty Tally for Votes
        self.herd_vote_tallies.append([])

        self.game_message(f"Each player will now take turns describing themselves:")

    def run_round(self):
        """Starts the round."""
        # Phase I: Collect Player Animal Descriptions
        for current_player in self.players:
            self.game_message(fetch_prompt("player_describe_animal"), current_player)
            self.player_turn_animal_description(current_player)

        # Phase II: Chameleon Guesses the Animal
        self.game_message("All players have spoken. The Chameleon will now guess the secret animal...")
        player_responses = self.format_animal_descriptions(exclude=self.chameleon)
        self.game_message(format_prompt("chameleon_guess_animal", player_responses=player_responses), self.chameleon)
        self.player_turn_chameleon_guess(self.chameleon)

        # Phase III: The Herd Votes for who they think the Chameleon is
        for current_player in self.players:
            if current_player.role == "herd":
                player_responses = self.format_animal_descriptions(exclude=current_player)
                self.game_message(format_prompt("vote", player_responses=player_responses), current_player)
                self.player_turn_herd_vote(current_player)

    def player_turn_animal_description(self, player: Player):
        """Handles a player's turn to describe themselves."""
        if not self.awaiting_input:
            self.verbose_message(f"{player.name} is thinking...", recipient=player, exclude=True)
            self.game_message(fetch_prompt("player_describe_animal"), player)

        # Get Player Animal Description
        response = player.interface.generate_formatted_response(AnimalDescriptionFormat)

        if response:
            self.round_animal_descriptions.append({"player_id": player.id, "description": response.description})
            self.game_message(f"{player.name}: {response.description}", player, exclude=True)
            self.awaiting_input = False
        else:
            self.awaiting_input = True

        return response

    def player_turn_chameleon_guess(self, chameleon: Player):
        """Handles the Chameleon's turn to guess the secret animal."""
        if not self.awaiting_input:
            self.game_message("All players have spoken. The Chameleon will now guess the secret animal...")
            self.verbose_message("The Chameleon is thinking...", recipient=chameleon, exclude=True)
            player_responses = self.format_animal_descriptions(exclude=self.chameleon)
            self.game_message(format_prompt("chameleon_guess_animal", player_responses=player_responses),
                              self.chameleon)

        response = chameleon.interface.generate_formatted_response(ChameleonGuessFormat)

        if response:
            self.chameleon_guesses.append(response.animal)
            self.game_message(
                "The Chameleon has guessed the animal. Now the Herd will vote on who they think the chameleon is.")
            self.awaiting_input = False
            self.game_state = "herd_vote"
        else:
            # Await input and do not proceed to the next phase
            self.awaiting_input = True

    def player_turn_herd_vote(self, player: Player):
        """Handles a player's turn to vote for the Chameleon."""
        if not self.awaiting_input:
            self.verbose_message(f"{player.name} is thinking...", recipient=player, exclude=True)
            player_responses = self.format_animal_descriptions(exclude=player)
            self.game_message(format_prompt("vote", player_responses=player_responses), player)

        # Get Player Vote
        additional_fields = {"player_names": [p.name for p in self.players if p != player]}
        response = player.interface.generate_formatted_response(HerdVoteFormat, additional_fields=additional_fields)

        if response:
            self.debug_message(f"{player.name} voted for {response.vote}", recipient=player, exclude=True)

            voted_for_player = self.player_from_name(response.vote)

            player_vote = {"voter_id": player.id, "voted_for_id": voted_for_player.id}

            self.herd_vote_tally.append(player_vote)
            self.awaiting_input = False
        else:
            self.awaiting_input = True

        return response

    def resolve_round(self):
        """Resolves the round, assigns points, and prints the results."""
        self.game_message("All players have voted!")
        for vote in self.herd_vote_tally:
            voter = self.player_from_id(vote["voter_id"])
            voted_for = self.player_from_id(vote["voted_for_id"])
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
            if vote["voted_for_id"] == self.chameleon.id:
                self.player_from_id(vote['voter_id']).points += 1

        # If the Herd fails to accuse the Chameleon      =   +1 Point to the Chameleon
        if not accused_player_id or accused_player_id != self.chameleon.id:
            self.chameleon.points += 1

        # Print Scores
        player_points = "\n".join([f"{player.name}: {player.points}" for player in self.players])
        self.game_message(f"Current Game Score:\n{player_points}")