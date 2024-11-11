# game/chess_player.py

import random
import chess
from abc import ABC, abstractmethod

class Player(ABC):
    @abstractmethod
    def make_move(self, board):
        pass

class RandomComputerPlayer(Player):
    def make_move(self, board):
        legal_moves = list(board.legal_moves)
        if legal_moves:
            move = random.choice(legal_moves)
            return move
        else:
            return None