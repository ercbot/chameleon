from game import ChameleonGame
from player import Player
import asyncio
from player import Player

def main():
    print("Please Enter your name, or leave blank to run an AI only game")
    name = input()

    if name:
        game = ChameleonGame(human_name=name, verbose=True)
    else:
        game = ChameleonGame(verbose=True)

    asyncio.run(game.run_game())


if __name__ == "__main__":
    main()