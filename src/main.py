from game import Game
import asyncio
from player import Player

def main():
    print("Please Enter your name:")
    name = input()

    game = Game(human_name=name)

    asyncio.run(game.start())


if __name__ == "__main__":
    main()