# chess_game/main.py

from game.chess_game import ChessGame
from game.chess_player import RandomComputerPlayer

def main():
    # You can replace RandomComputerPlayer with your own AI implementation
    game = ChessGame(computer_player_class=RandomComputerPlayer)
    game.run()

if __name__ == "__main__":
    main()