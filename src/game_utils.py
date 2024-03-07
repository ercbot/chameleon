"""
Utilities for the game including random selections and prompts.
"""
import random
import string
import json
from collections import Counter

ALPHABET = string.ascii_lowercase + string.digits
ID_LENGTH = 8


def game_id():
    return ''.join(random.choices(ALPHABET, k=ID_LENGTH)) # Using this instead of uuid for shorter game ids


def random_animal():
    return random.choice(available_animals)


available_animals = ["Giraffe", "Elephant", "Lion", "Zebra", "Monkey", "Gorilla"]


def random_names(number_of_samples: int, human_name: str = None) -> list[str]:
    """Returns a list of random names, excluding the one of the human player (if provided)"""
    if human_name and human_name in available_names:
        available_names.remove(human_name)
    return random.sample(available_names, number_of_samples)


available_names = ["Jack", "Jill", "Bob", "Courtney", "Fizz", "Mallory"]


def random_index(number_of_players : int) -> int:
    return random.randint(0, number_of_players - 1)


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


def log(log_object, log_file):
    with open(log_file, "a+") as f:
        f.write(json.dumps(log_object) + "\n")