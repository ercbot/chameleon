import string
import random

# Utilities
ALPHABET = string.ascii_lowercase + string.digits
ID_LENGTH = 8
AVAILABLE_NAMES = ["Aiden", "Bianca", "Charlie", "Dylan", "Eva", "Finn", "Grace", "Henry", "Isabella", "Julian", "Kaitlyn", "Lucas", "Mia", "Nolan", "Oliver", "Penelope", "Quinn", "Riley", "Sophia", "Tessa", "Ulysses", "Violet", "Wyatt", "Xavier", "Yara", "Zoe"]


def generate_game_id():
    """Generates a unique game id."""
    alphabet = string.ascii_lowercase + string.digits
    id_length = 8

    return ''.join(random.choices(alphabet, k=id_length))  # Using this instead of uuid for shorter game ids


def random_names(number_of_samples: int, human_name: str = None) -> list[str]:
    """Returns a list of random names, excluding the one of the human player (if provided)"""
    if human_name and human_name in AVAILABLE_NAMES:
        AVAILABLE_NAMES.remove(human_name)
    return random.sample(AVAILABLE_NAMES, number_of_samples)


def random_index(number_of_players: int) -> int:
    return random.randint(0, number_of_players - 1)