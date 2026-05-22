"""CLI entry point for the chess-game player demo.

Wires up the player implementations under ``chess-game/game/`` so users
can watch two configured engines play a full game from the command line.

Usage:
    python3 chess-game/main.py --white random --black minimax --depth 3
"""

import argparse
import os
import sys
import time

import chess

# Make the sibling ``game`` package importable when this script is invoked
# directly (i.e. ``python3 chess-game/main.py``) rather than as a module.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from game.minimax_computer_player import MinimaxComputerPlayer  # noqa: E402
from game.random_computer_player import RandomComputerPlayer  # noqa: E402


PLAYER_KINDS = ("random", "minimax")


def build_player(kind, depth):
    """Construct a Player given the CLI ``kind`` string."""
    if kind == "random":
        return RandomComputerPlayer()
    if kind == "minimax":
        return MinimaxComputerPlayer(depth=depth)
    raise ValueError("unknown player kind: {0}".format(kind))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Watch two configured chess engines play each other.",
    )
    parser.add_argument(
        "--white",
        choices=PLAYER_KINDS,
        default="random",
        help="Engine controlling the white pieces (default: random).",
    )
    parser.add_argument(
        "--black",
        choices=PLAYER_KINDS,
        default="random",
        help="Engine controlling the black pieces (default: random).",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Search depth used by the minimax engine (default: 2).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds to pause between moves so the game is watchable.",
    )
    parser.add_argument(
        "--max-moves",
        type=int,
        default=0,
        help="Stop after this many half-moves (0 means play to completion).",
    )
    return parser.parse_args(argv)


def play_game(white_kind, black_kind, depth, delay, max_moves):
    """Drive a full game and return the python-chess result string."""
    white = build_player(white_kind, depth)
    black = build_player(black_kind, depth)
    board = chess.Board()

    print("Starting position:")
    print(board.unicode())
    print("")

    plies = 0
    while not board.is_game_over():
        if max_moves and plies >= max_moves:
            print("Reached --max-moves limit ({0}); stopping.".format(max_moves))
            break

        is_white_turn = board.turn == chess.WHITE
        mover = white if is_white_turn else black
        mover_kind = white_kind if is_white_turn else black_kind
        side_label = "White" if is_white_turn else "Black"

        move = mover.make_move(board)
        if move is None:
            print("{0} ({1}) has no legal move.".format(side_label, mover_kind))
            break

        move_uci = move.uci()
        board.push(move)
        plies += 1

        print("{0} ({1}) plays {2}".format(side_label, mover_kind, move_uci))
        print(board.unicode())
        print("")

        if delay > 0:
            time.sleep(delay)

    result = board.result()
    print("Game over: {0}".format(result))
    if board.is_checkmate():
        print("Reason: checkmate")
    elif board.is_stalemate():
        print("Reason: stalemate")
    elif board.is_insufficient_material():
        print("Reason: insufficient material")
    elif board.is_seventyfive_moves():
        print("Reason: 75-move rule")
    elif board.is_fivefold_repetition():
        print("Reason: fivefold repetition")
    return result


def main(argv=None):
    args = parse_args(argv)
    play_game(
        white_kind=args.white,
        black_kind=args.black,
        depth=args.depth,
        delay=args.delay,
        max_moves=args.max_moves,
    )


if __name__ == "__main__":
    main()
