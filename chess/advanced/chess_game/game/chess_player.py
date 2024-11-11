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
            return random.choice(legal_moves)
        else:
            return None

class MinimaxComputerPlayer(Player):
    def __init__(self, depth=2):
        self.depth = depth

    def make_move(self, board):
        _, move = self.minimax(board, self.depth, -float('inf'), float('inf'), board.turn)
        return move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        best_move = None
        legal_moves = list(board.legal_moves)

        if is_maximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn:
                return -float('inf')  # Black wins
            else:
                return float('inf')   # White wins
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        value = 0
        for piece_type in piece_values:
            value += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            value -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
        return value