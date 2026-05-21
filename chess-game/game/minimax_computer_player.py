import chess

from .player import Player


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


class MinimaxComputerPlayer(Player):
    def __init__(self, depth=2):
        self.depth = depth
        self.transposition_table = {}

    def _evaluate(self, board):
        # Terminal states.
        if board.is_checkmate():
            # Side to move is checkmated -> very bad for that side.
            return -10000 if board.turn else 10000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        for piece_type, value in PIECE_VALUES.items():
            score += value * len(board.pieces(piece_type, chess.WHITE))
            score -= value * len(board.pieces(piece_type, chess.BLACK))
        return score

    def _minimax(self, board, depth, maximizing):
        if depth == 0 or board.is_game_over():
            return self._evaluate(board), None

        best_move = None
        if maximizing:
            best_value = float("-inf")
            for move in board.legal_moves:
                board.push(move)
                value, _ = self._minimax(board, depth - 1, False)
                board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
            return best_value, best_move
        else:
            best_value = float("inf")
            for move in board.legal_moves:
                board.push(move)
                value, _ = self._minimax(board, depth - 1, True)
                board.pop()
                if value < best_value:
                    best_value = value
                    best_move = move
            return best_value, best_move

    def make_move(self, board):
        board_state_key = board.fen()
        if board_state_key in self.transposition_table:
            cached_move = self.transposition_table[board_state_key][1]
            if cached_move in board.legal_moves:
                return cached_move

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        maximizing = board.turn == chess.WHITE
        value, move = self._minimax(board, self.depth, maximizing)
        if move is None:
            # Fallback: any legal move (e.g., depth=0 corner case).
            move = legal_moves[0]
        self.transposition_table[board_state_key] = (value, move)
        return move
