"""
Utilities for the game including random selections and prompts.
"""
import random
import string
import json
from collections import Counter


def random_animal():
    return random.choice(available_animals)


available_animals = ["Giraffe", "Elephant", "Lion", "Zebra", "Monkey", "Gorilla"]


def count_chameleon_votes(player_votes: list[dict]) -> str | None:
    """Counts the votes for each player."""
    votes = [vote['voted_for_id'] for vote in player_votes]

    freq = Counter(votes)
    most_voted_player, number_of_votes = freq.most_common()[0]

    # If one player has more than 50% of the votes, the herd accuses them of being the chameleon
    if number_of_votes / len(player_votes) >= 0.5:
        return most_voted_player
    else:
        return None
