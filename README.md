```yaml
title: Chameleon
emoji: 🦎
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: 1.31.1
```

# Chameleon

*A social deduction game powered by LLMs*

## Game Rules

Chameleon is a social deduction game (a la Mafia, Among Us, etc.) about blending in, and finding out who doesn't belong.


At the start of the game, each player is assigned one of two roles:
- **The Herd**: The herd is a group of players who are all the same animal. They are trying to identify the chameleon hidden amongst them, while keeping the true animal a secret.
- **The Chameleon**: The chameleon is pretending to be part of the herd. Their goal is to identify what animal the herd is while remaining undetected.

Each round, all players say something about themselves, in the form of a "I am a/have/do/etc..." sentence in 10 words or less. 

After all players have spoken, the Chameleon is given the choice to guess what animal the herd is. If they guess correctly, they win. If they guess incorrectly, the herd wins.

If the Chameleon chooses not to guess the herd then votes on what player they think the Chameleon is. 
If the majority of the herd votes for the Chameleon, the herd wins. If the majority of the herd votes for a member of the herd, the Chameleon wins.

Example Round:
*The secret animal is an owl Owl*
Herd player 1: I have sharp claws.
Herd player 2: I am a creature of the night.
Herd player 3: I soar the skies looking for prey.
Herd player 4: I have a keen eye.
Chameleon: I am a predator.
