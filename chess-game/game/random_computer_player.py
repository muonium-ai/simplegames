class RandomComputerPlayer(Player):
    def make_move(self, board):
        legal_moves = list(board.legal_moves)
        if legal_moves:
            return random.choice(legal_moves)
        else:
            return None