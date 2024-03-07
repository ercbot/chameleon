from game import Game
from player import Player
import asyncio
from player import Player

def main():
    print("Please Enter your name, or leave blank to run an AI only game")
    name = input()

    if name:
        game = Game(human_name=name, verbose=True)
    else:
        game = Game(verbose=True)

    asyncio.run(game.run_game())


if __name__ == "__main__":
    main()