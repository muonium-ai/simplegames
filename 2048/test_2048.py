# test_game.py
import unittest
from game_2048.game import Game2048

class TestGame2048(unittest.TestCase):
    def setUp(self):
        self.game = Game2048()

    def test_new_game(self):
        state = self.game.get_state()
        self.assertEqual(state['score'], 0)
        self.assertEqual(state['moves'], 0)
        self.assertEqual(state['max_tile'], 2)

    def test_move(self):
        # Test moves
        self.game.grid = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.game.move('RIGHT')
        self.assertEqual(self.game.grid[0][3], 4)