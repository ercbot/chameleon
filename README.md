# Chameleon

*A social deduction game powered by LLMs*

[Play Now](https://huggingface.co/spaces/ericbotti/chameleon)

## Description

Chameleon is a social deduction game (a la Mafia, Among Us, etc.) about blending in, and figuring out who doesn't belong.

At the start of the game, each player is assigned one of two roles:
- **Herd**: The herd is a group of players who are all the same animal. They are trying to identify the chameleon hidden amongst them, while keeping the true animal a secret.
- **Chameleon**: This player is pretending to be part of the herd. Their goal is to identify what animal the herd is while remaining undetected.

See the [game rules file](GAME_RULES.md) for more details.

## Running the Game

The Easiest way to play the game is to use [Hugging Face Space Demo](https://huggingface.co/spaces/ericbotti/chameleon)

If you want to run the game locally, you can clone the repository and run the game using the command line or the Streamlit app.

1. **Using the command line**:
    - Run `python src/main.py` from the root directory

2. **Using the Streamlit App**:
    - Run `streamlit run src/app.py` from the root directory

