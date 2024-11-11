# chess_game/game/chess_player.py

from abc import ABC, abstractmethod
import random
import chess

class ChessPlayer(ABC):
    """Abstract base class for chess players (human or computer)."""
    
    @abstractmethod
    def make_move(self, board):
        """Make a move given the current board state."""
        pass

class RandomComputerPlayer(ChessPlayer):
    """Computer player that makes random moves."""
    
    def make_move(self, board):
        legal_moves = list(board.legal_moves)
        if legal_moves:
            move = random.choice(legal_moves)
            board.push(move)
            return True
        return False