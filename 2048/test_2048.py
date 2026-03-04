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
        self.game.add_new_tile = lambda: None

        self.game.grid = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        self.game.move('RIGHT')
        self.assertEqual(self.game.grid[0][3], 4)

    def test_move_updates_score_and_moves(self):
        self.game.add_new_tile = lambda: None
        self.game.grid = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        moved = self.game.move('LEFT')

        self.assertTrue(moved)
        self.assertEqual(self.game.score, 4)
        self.assertEqual(self.game.total_moves, 1)
        self.assertEqual(self.game.grid[0], [4, 0, 0, 0])

    def test_noop_move_does_not_change_score_or_moves(self):
        self.game.add_new_tile = lambda: None
        self.game.grid = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        moved = self.game.move('LEFT')

        self.assertFalse(moved)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.total_moves, 0)

    def test_game_over_detection(self):
        self.game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]

        self.assertTrue(self.game.is_game_over())