from game_chameleon import ChameleonGame
from player import Player
import asyncio
from player import Player

def main():
    print("Please Enter your name, or leave blank to run an AI only game")
    name = input()

    game = ChameleonGame.from_human_name(name)

    asyncio.run(game.run_game())


if __name__ == "__main__":
    main()