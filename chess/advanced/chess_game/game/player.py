# game/player.py

from abc import ABC, abstractmethod
import chess

class Player(ABC):
    @abstractmethod
    def make_move(self, board: chess.Board):
        pass