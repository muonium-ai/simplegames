# game/chess_player.py

import random
import chess
from abc import ABC, abstractmethod
import math

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
        self.transposition_table = {}

    def make_move(self, board):
        board_fen = board.board_fen()
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen][1]
        _, move = self.minimax(board, self.depth, -math.inf, math.inf, board.turn)
        return move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        board_fen = board.board_fen()
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen]

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        best_move = None
        legal_moves = list(board.legal_moves)

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

    def evaluate_board(self, board):
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

class MinimaxComputerPlayer2(Player):
    def __init__(self, depth=3):
        self.depth = depth
        self.transposition_table = {}
        self.piece_square_tables = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 5, 5, 5, 5, 5, 5, 5,
                1, 1, 2, 3, 3, 2, 1, 1,
                0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
                0, 0, 0, 2, 2, 0, 0, 0,
                0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
                0.5, 1, 1, -2, -2, 1, 1, 0.5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.KNIGHT: [
                -5, -4, -3, -3, -3, -3, -4, -5,
                -4, -2, 0, 0, 0, 0, -2, -4,
                -3, 0, 1, 1.5, 1.5, 1, 0, -3,
                -3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3,
                -3, 0, 1.5, 2, 2, 1.5, 0, -3,
                -3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3,
                -4, -2, 0, 0.5, 0.5, 0, -2, -4,
                -5, -4, -3, -3, -3, -3, -4, -5
            ],
            chess.BISHOP: [
                -2, -1, -1, -1, -1, -1, -1, -2,
                -1, 0, 0, 0, 0, 0, 0, -1,
                -1, 0, 0.5, 1, 1, 0.5, 0, -1,
                -1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1,
                -1, 0, 1, 1, 1, 1, 0, -1,
                -1, 1, 1, 1, 1, 1, 1, -1,
                -1, 0.5, 0, 0, 0, 0, 0.5, -1,
                -2, -1, -1, -1, -1, -1, -1, -2
            ],
            chess.ROOK: [
                0, 0, 0, 0.5, 0.5, 0, 0, 0,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                0.5, 1, 1, 1, 1, 1, 1, 0.5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.QUEEN: [
                -2, -1, -1, -0.5, -0.5, -1, -1, -2,
                -1, 0, 0, 0, 0, 0, 0, -1,
                -1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1,
                -0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
                0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
                -1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1,
                -1, 0, 0.5, 0, 0, 0, 0, -1,
                -2, -1, -1, -0.5, -0.5, -1, -1, -2
            ],
            chess.KING: [
                -3, -4, -4, -5, -5, -4, -4, -3,
                -3, -4, -4, -5, -5, -4, -4, -3,
                -3, -4, -4, -5, -5, -4, -4, -3,
                -3, -4, -4, -5, -5, -4, -4, -3,
                -2, -3, -3, -4, -4, -3, -3, -2,
                -1, -2, -2, -2, -2, -2, -2, -1,
                2, 2, 0, 0, 0, 0, 2, 2,
                2, 3, 1, 0, 0, 1, 3, 2
            ]
        }

    def make_move(self, board):
        _, move = self.minimax(board, self.depth, -math.inf, math.inf, board.turn)
        return move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        board_fen = board.fen()
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen]

        legal_moves = list(board.legal_moves)

        # Move Ordering: prioritize captures and checks
        def move_order(move):
            score = 0
            if board.is_capture(move):
                score += 10
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    score += self.get_piece_value(captured_piece.piece_type)
            if board.gives_check(move):
                score += 5
            return score

        legal_moves.sort(key=move_order, reverse=True)

        best_move = None

        if is_maximizing:
            max_eval = -math.inf
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
            self.transposition_table[board_fen] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = math.inf
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
            self.transposition_table[board_fen] = (min_eval, best_move)
            return min_eval, best_move

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn:
                return -math.inf  # Black wins
            else:
                return math.inf   # White wins
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        value = 0
        for piece_type in self.piece_square_tables:
            value += self.count_piece_value(board, piece_type, chess.WHITE)
            value -= self.count_piece_value(board, piece_type, chess.BLACK)

        # Mobility
        value += len(list(board.legal_moves)) * 0.1

        return value

    def count_piece_value(self, board, piece_type, color):
        piece_value = self.get_piece_value(piece_type)
        square_values = self.piece_square_tables.get(piece_type, [0] * 64)
        total = 0
        for square in board.pieces(piece_type, color):
            total += piece_value + square_values[square]
        return total

    def get_piece_value(self, piece_type):
        if piece_type == chess.PAWN:
            return 1
        elif piece_type == chess.KNIGHT:
            return 3
        elif piece_type == chess.BISHOP:
            return 3.25
        elif piece_type == chess.ROOK:
            return 5
        elif piece_type == chess.QUEEN:
            return 9
        elif piece_type == chess.KING:
            return 0  # King value is handled separately
        return 0

class MinimaxComputerPlayer3(Player):
    def __init__(self, depth=3):
        self.depth = depth
        self.transposition_table = {}
        self.piece_square_tables = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 5, 5, 5, 5, 5, 5, 5,
                1, 1, 2, 3, 3, 2, 1, 1,
                0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
                0, 0, 0, 2, 2, 0, 0, 0,
                0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
                0.5, 1, 1, -2, -2, 1, 1, 0.5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.KNIGHT: [
                -5, -4, -3, -3, -3, -3, -4, -5,
                -4, -2, 0, 0, 0, 0, -2, -4,
                -3, 0, 1, 1.5, 1.5, 1, 0, -3,
                -3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3,
                -3, 0, 1.5, 2, 2, 1.5, 0, -3,
                -3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3,
                -4, -2, 0, 0.5, 0.5, 0, -2, -4,
                -5, -4, -3, -3, -3, -3, -4, -5
            ],
            chess.BISHOP: [
                -2, -1, -1, -1, -1, -1, -1, -2,
                -1, 0, 0, 0, 0, 0, 0, -1,
                -1, 0, 0.5, 1, 1, 0.5, 0, -1,
                -1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1,
                -1, 0, 1, 1, 1, 1, 0, -1,
                -1, 1, 1, 1, 1, 1, 1, -1,
                -1, 0.5, 0, 0, 0, 0, 0.5, -1,
                -2, -1, -1, -1, -1, -1, -1, -2
            ],
            chess.ROOK: [
                0, 0, 0, 0.5, 0.5, 0, 0, 0,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                0.5, 1, 1, 1, 1, 1, 1, 0.5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.QUEEN: [
                -2, -1, -1, -0.5, -0.5, -1, -1, -2,
                -1, 0, 0, 0, 0, 0, 0, -1,
                -1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1,
                -0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
                0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
                -1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1,
                -1, 0, 0.5, 0, 0, 0, 0, -1,
                -2, -1, -1, -0.5, -0.5, -1, -1, -2
            ],
            chess.KING: [
                -3, -4, -4, -5, -5, -4, -4, -3,
                -3, -4, -4, -5, -5, -4, -4, -3,
                -3, -4, -4, -5, -5, -4, -4, -3,
                -3, -4, -4, -5, -5, -4, -4, -3,
                -2, -3, -3, -4, -4, -3, -3, -2,
                -1, -2, -2, -2, -2, -2, -2, -1,
                2, 2, 0, 0, 0, 0, 2, 2,
                2, 3, 1, 0, 0, 1, 3, 2
            ]
        }
        self.opening_book = [
            [chess.Move.from_uci('e2e4'), chess.Move.from_uci('e7e5')],
            [chess.Move.from_uci('d2d4'), chess.Move.from_uci('d7d5')],
            [chess.Move.from_uci('g1f3'), chess.Move.from_uci('b8c6')],
            [chess.Move.from_uci('c2c4'), chess.Move.from_uci('e7e6')]
        ]
        self.opening_moves_played = 0
        self.max_opening_moves = 8  # Number of moves to follow the opening book

    def make_move(self, board):
        if self.opening_moves_played < self.max_opening_moves and board.fullmove_number <= self.max_opening_moves // 2:
            opening_variation = random.choice(self.opening_book)
            if self.opening_moves_played < len(opening_variation):
                move = opening_variation[self.opening_moves_played]
                if move in board.legal_moves:
                    self.opening_moves_played += 1
                    return move
        _, move = self.minimax(board, self.depth, -math.inf, math.inf, board.turn)
        return move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        board_fen = board.fen()
        if board_fen in self.transposition_table:
            return self.transposition_table[board_fen]

        legal_moves = list(board.legal_moves)

        # Move Ordering: prioritize captures and checks
        def move_order(move):
            score = 0
            if board.is_capture(move):
                score += 10
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    score += self.get_piece_value(captured_piece.piece_type)
            if board.gives_check(move):
                score += 5
            return score

        legal_moves.sort(key=move_order, reverse=True)

        best_move = None

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

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn:
                return -math.inf  # Black wins
            else:
                return math.inf   # White wins
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        value = 0
        for piece_type in self.piece_square_tables:
            value += self.count_piece_value(board, piece_type, chess.WHITE)
            value -= self.count_piece_value(board, piece_type, chess.BLACK)

        # Mobility
        value += len(list(board.legal_moves)) * 0.1

        return value

    def count_piece_value(self, board, piece_type, color):
        piece_value = self.get_piece_value(piece_type)
        square_values = self.piece_square_tables.get(piece_type, [0] * 64)
        total = 0
        for square in board.pieces(piece_type, color):
            total += piece_value + square_values[square]
        return total

    def get_piece_value(self, piece_type):
        if piece_type == chess.PAWN:
            return 1
        elif piece_type == chess.KNIGHT:
            return 3
        elif piece_type == chess.BISHOP:
            return 3.25
        elif piece_type == chess.ROOK:
            return 5
        elif piece_type == chess.QUEEN:
            return 9
        elif piece_type == chess.KING:
            return 0  # King value is handled separately
        return 0