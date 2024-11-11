# game/random_computer_player.py

import random
import chess
from .player import Player

class RandomComputerPlayer(Player):
    def make_move(self, board: chess.Board):
        legal_moves = list(board.legal_moves)
        if legal_moves:
            return random.choice(legal_moves)
        else:
            return None