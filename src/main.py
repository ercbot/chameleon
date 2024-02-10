from game import Game
from player import Player

def main():
    print("Please Enter your name:")
    name = input()

    game = Game(human_name=name)

    game.start()


if __name__ == "__main__":
    main()