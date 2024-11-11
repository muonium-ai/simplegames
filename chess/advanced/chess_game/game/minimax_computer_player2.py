# game/minimax_computer_player2.py

import random
import chess
import math
from .player import Player

class MinimaxComputerPlayer2(Player):
    def __init__(self, depth=3):
        self.depth = depth
        self.transposition_table = {}

    def make_move(self, board: chess.Board):
        board_fen = board.board_fen()
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen][1]
        _, move = self.minimax(board, self.depth, -math.inf, math.inf, board.turn)
        return move

    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, is_maximizing: bool):
        board_fen = board.board_fen()
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen]

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        best_move = None
        legal_moves = list(board.legal_moves)
        legal_moves.sort(key=lambda move: self.move_order(board, move), reverse=True)

        if is_maximizing:
            max_eval = -math.inf
            best_moves = []
            for move in legal_moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_moves = [move]
                elif eval == max_eval:
                    best_moves.append(move)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            best_move = random.choice(best_moves) if best_moves else None
            self.transposition_table[board_fen] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = math.inf
            best_moves = []
            for move in legal_moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_moves = [move]
                elif eval == min_eval:
                    best_moves.append(move)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            best_move = random.choice(best_moves) if best_moves else None
            self.transposition_table[board_fen] = (min_eval, best_move)
            return min_eval, best_move

    def move_order(self, board: chess.Board, move: chess.Move):
        score = 0
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += self.get_piece_value(captured_piece.piece_type)
        return score

    def get_piece_value(self, piece_type: int):
        """Assigns a numerical value to each piece type."""
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
        return piece_values.get(piece_type, 0)

    def evaluate_board(self, board: chess.Board):
        if board.is_checkmate():
            if board.turn:
                return -math.inf  # Black wins
            else:
                return math.inf   # White wins
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