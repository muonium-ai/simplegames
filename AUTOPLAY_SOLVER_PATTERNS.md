# Autoplay and Solver Invocation Patterns

Ticket: **T-000057** — *cross-cutting: standardize autoplay and solver invocation pattern across all games*

This document is an inventory and design proposal. It is the deliverable for
T-000057 and the basis for future per-game cleanup tickets. No game has been
rewritten as part of T-000057; only two small unifying code edits were made
(see [Code changes applied here](#code-changes-applied-in-t-000057)).

The repo's high-level `todo.md` item 3 asks us to "standardise code and solver
invoking across all the games". Today the games handle autoplay and solver
selection inconsistently: some use a `--solver` CLI flag with a dynamic
`importlib.import_module(...)` lookup, some hard-code the AI into the game,
some expose autoplay via a start-screen button, and some have a separate
`*_autoplay.py` script entirely.

## 1. Inventory

Entry-point script per game, how autoplay (if any) is triggered, and how a
solver (if any) is selected. "N/A" means the game does not implement that
capability at all.

| Game | Entry-point script | Autoplay trigger | Solver selection | Run example |
|---|---|---|---|---|
| 2048 (pygame) | `2048/2048.py` | N/A (no AI in this file) | N/A | `python3 2048/2048.py` |
| 2048 (modular gui) | `2048/main.py` -> `2048/game_2048/gui.py` | N/A | N/A in entry; external solver scripts in `2048/solver/` talk to `2048/server.py` over HTTP | `python3 2048/main.py` |
| 2048 (server + external solvers) | `2048/server.py` + `2048/solver/*.py` | client script drives moves | choose by running a specific `2048/solver/<file>.py` | `python3 2048/server.py` then `python3 2048/solver/2048_solver.py` |
| Asteroid | `asteroid/asteroid.py` | Start-screen "autoplay" button (`action == "autoplay"`) | N/A (AI hard-coded in `auto_control()`) | `python3 asteroid/asteroid.py` |
| Bricks | `bricks/bricks.py` | Start modal buttons: `"autoplay"` / `"fast_autoplay"` | N/A (paddle AI hard-coded) | `python3 bricks/bricks.py` |
| Blackjack | `card_games/blackjack/blackjack.py` | N/A | N/A | `python3 card_games/blackjack/blackjack.py` |
| Klondike | `card_games/klondike/klondike.py` | Menu "autoplay" button (`self.autoplay`) | N/A (hard-coded foundation-stacking heuristic) | `python3 card_games/klondike/klondike.py` |
| Solitaire | `card_games/solitaire/Solitaire.py` | N/A | N/A | `python3 card_games/solitaire/Solitaire.py` |
| Solitaire-Klondike | `card_games/solitaire-klondike/solitaire.py` | N/A | N/A | `python3 card_games/solitaire-klondike/solitaire.py` |
| Chess (human vs computer) | `chess/chess_autoplay.py` | Always-on (computer plays White, human plays Black) | N/A (engine hard-coded) | `python3 chess/chess_autoplay.py` |
| Chess (PGN viewer) | `chess/chess_player.py` | N/A (replays a PGN file) | N/A; positional CLI: `sys.argv[1]` = PGN filename | `python3 chess/chess_player.py games.pgn` |
| chess-game (library) | `chess-game/game/*.py` | N/A — no `__main__`; library only | Player classes (`RandomComputerPlayer`, `MinimaxComputerPlayer`) chosen in code | (no entry point) |
| Flappy Bird | `flappybird/flappy_bird.py` | Start-screen "Autoplay" button OR in-game "Autoplay" button | N/A (heuristic hard-coded) | `python3 flappybird/flappy_bird.py` |
| Game of Life | `gameoflife/gameoflife.py` | Always-on (cellular automaton, no human input) | N/A | `python3 gameoflife/gameoflife.py` |
| Genetic Car | `genetic_car/genetic_car.py` | Always-on (genetic algorithm runs the cars) | N/A (GA is the algorithm itself) | `python3 genetic_car/genetic_car.py` |
| Grid Maze | `mazes/grid_maze.py` | `S` key triggers BFS auto-solve | N/A (BFS hard-coded) | `python3 mazes/grid_maze.py` |
| Hexagonal Maze | `mazes/hexagonal_maze.py` | UI buttons / key control | N/A | `python3 mazes/hexagonal_maze.py` |
| Minesweeper (basic) | `minesweeper/minesweeper.py` | N/A | N/A | `python3 minesweeper/minesweeper.py` |
| Minesweeper (probability) | `minesweeper/minesweeper_with_probability.py`, `…_probability2.py` | N/A | hard-coded probability solver | `python3 minesweeper/minesweeper_with_probability.py` |
| Minesweeper (with solver) | `minesweeper/minesweeper_with_solver.py` | always-on when a solver is chosen | `--solver <name>` flag (also accepts a positional name for backward compat); allowlist = `{"random_solver"}`; resolved via `importlib.import_module(f"solvers.{name}")` | `python3 minesweeper/minesweeper_with_solver.py --solver random_solver` |
| Minesweeper v2 | `minesweeper/v2/minesweeper.py` | N/A | N/A | `python3 minesweeper/v2/minesweeper.py` |
| Pong | `pong/pong.py` | N/A (two-player keyboard) | N/A | `python3 pong/pong.py` |
| Rubik's Cube (2D) | `rubiks_cube/rubiks_cube.py` | "Solve" button (`auto_solve` flag) | N/A (Kociemba solver hard-coded in `CubeSolver`) | `python3 rubiks_cube/rubiks_cube.py` |
| Rubik's Cube (3D) | `rubiks_cube/rubiks_cube_3d.py` | UI buttons | N/A (Kociemba hard-coded) | `python3 rubiks_cube/rubiks_cube_3d.py` |
| Slider Game | `slidergame/Slider Game/*` (Swift / iOS) | N/A (native app, separate stack) | N/A | `make -C slidergame ios-sim` |
| Snake | `snake/snake.py` | Start-screen "Autosnake" button (`mode == "autosnake"`) | N/A (AI heuristic hard-coded in `ai_direction`) | `python3 snake/snake.py` |
| Multi-Snake | `snake/multi-snake.py` | Always-on (`AIStrategy` drives each snake) | N/A | `python3 snake/multi-snake.py` |
| Snake (Grok3) | `snake/snake-grok3.py` | N/A | N/A | `python3 snake/snake-grok3.py` |
| Space Invaders | `spaceinvaders/spaceinvaders.py` | `A` key on the start/game-over screen OR new `--autoplay` flag | N/A (AI hard-coded in `auto_play()`) | `python3 spaceinvaders/spaceinvaders.py --autoplay` |
| Sudoku (with solver) | `sudoku/main.py` | always-on when a solver is chosen | `--solver <name>` flag; allowlist = `{"basic_solver", "solver_constraint"}`; resolved via `importlib.import_module(f"solvers.{name}")` | `python3 sudoku/main.py --solver basic_solver` |
| Sudoku (no solver) | `sudoku/sudoku.py` | N/A | N/A | `python3 sudoku/sudoku.py` |
| Tetris | `tetris/tetris.py` | N/A | N/A | `python3 tetris/tetris.py` |

### Summary of patterns observed

The audit found at least six distinct ways games expose autoplay/solvers:

1. `--solver <name>` argparse flag + allowlist + `importlib.import_module` —
   `sudoku/main.py`, `minesweeper/minesweeper_with_solver.py`.
2. Start-screen button only — `asteroid`, `bricks`, `flappybird`, `snake`,
   `card_games/klondike`.
3. In-game key or button only — `mazes/grid_maze.py` (`S` key),
   `spaceinvaders` (`A` key).
4. Always-on AI / no human option — `gameoflife`, `genetic_car`,
   `snake/multi-snake.py`, `chess/chess_autoplay.py` (computer-always-plays-White).
5. Hard-coded solver embedded in the game — `rubiks_cube/*` (Kociemba),
   `minesweeper/minesweeper_with_probability*.py`.
6. Separate entry-point script per mode —
   `chess/chess_autoplay.py` vs `chess/chess_player.py`, and 2048's `server.py`
   plus `solver/*.py` scripts driving the server over HTTP.

## 2. Proposed target pattern

For every game that has any form of AI/autoplay or pluggable solver, converge
on a single argparse-based pattern at the entry-point:

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="<game name>")
    parser.add_argument(
        "--autoplay",
        action="store_true",
        help="Start in autoplay (AI) mode instead of human input.",
    )
    # Only games that actually support pluggable solvers add this:
    parser.add_argument(
        "--solver",
        type=str,
        default=None,
        help="Name of the solver module to load from solvers/.",
    )
    args = parser.parse_args()
    ...
```

Rules:

- **Default `--autoplay=False`.** The human-playable mode is always the
  default. `--autoplay` shortcuts past the start screen and launches the
  AI-driven mode immediately.
- **Games without autoplay simply omit the flag.** Don't add a useless
  `--autoplay` to e.g. Tetris or Pong.
- **Solver selection is via `--solver <name>` plus a per-game allowlist.**
  The allowlist is required (security: prevents arbitrary `importlib` loads
  from crafted CLI input — see T-000054). When a solver is selected the game
  runs in autoplay mode automatically.
- **Start-screen buttons remain.** The argparse flag is an *additional* way
  to launch into a mode, not a replacement; clicking the on-screen "Autoplay"
  button must still work for users running the game without CLI arguments.
- **Prefer a single entry script per game.** Avoid splitting a game into
  `<game>.py` and `<game>_autoplay.py` — fold modes into one script gated by
  `--autoplay`. (Chess is the most visible exception today.)

## 3. Already matches the target pattern

These entry points already use `--solver` + an allowlist + `importlib`:

- `sudoku/main.py` (allowlist: `{basic_solver, solver_constraint}`)
- `minesweeper/minesweeper_with_solver.py` — now uses `--solver` after the
  T-000057 unification (also accepts a bare positional name for backward
  compatibility). Allowlist: `{random_solver}`.

`spaceinvaders/spaceinvaders.py` now also accepts `--autoplay` (T-000057
unification) and demonstrates the autoplay half of the target pattern.

## 4. Games that would need follow-up tickets

Each of the games below has autoplay (or could expose a solver) but does not
yet match the target pattern. A future ticket per row would converge them.

| Game | What the follow-up ticket would do |
|---|---|
| `asteroid/asteroid.py` | Add `--autoplay` argparse flag that calls `self.start_game(autoplay=True)` so the existing button is no longer the only entry point. |
| `bricks/bricks.py` | Add `--autoplay` and `--fast-autoplay` flags that bypass the modal and pick a mode directly. |
| `card_games/klondike/klondike.py` | Add `--autoplay` flag that sets `self.autoplay = True` after initial deal. |
| `flappybird/flappy_bird.py` | Add `--autoplay` flag that sets `auto_play = True` and `started = True` at startup. |
| `mazes/grid_maze.py` | Add `--autoplay` that triggers `bfs_solve` automatically at start. |
| `snake/snake.py` | Add `--autoplay` (a.k.a. "autosnake" mode) flag. |
| `rubiks_cube/rubiks_cube.py`, `rubiks_cube_3d.py` | Add `--autoplay` that scrambles + auto-solves at start; consider whether to expose `--solver` (today only Kociemba). |
| `chess/chess_autoplay.py` + `chess/chess_player.py` | Fold both into one entry, e.g. `chess.py --autoplay` and `chess.py --pgn games.pgn`. Document that PGN replay is itself a kind of autoplay. |
| `2048/main.py` + `2048/solver/*.py` | Decide whether to keep the client/server split or add an in-process `--solver` flag to `2048/main.py` that runs a solver against `GameGUI` directly. |
| `minesweeper/minesweeper.py`, `…_with_probability*.py`, `v2/minesweeper.py` | Decide whether to consolidate the four+ minesweeper entry points into one with `--solver` and `--autoplay`. |
| `gameoflife`, `genetic_car`, `snake/multi-snake.py` | "Always-on" — exempt from the target pattern. Document them as such; no flags needed. |
| `pong/pong.py`, `tetris/tetris.py`, `card_games/blackjack`, `card_games/solitaire`, `card_games/solitaire-klondike`, `sudoku/sudoku.py`, `minesweeper/minesweeper.py`, `2048/2048.py`, `snake/snake-grok3.py`, `mazes/hexagonal_maze.py` | No autoplay or solver today — exempt; do not add unused flags. |
| `slidergame/` | Swift/iOS, separate toolchain — out of scope. |

## 5. Code changes applied in T-000057

Two small unifications were applied as a first concrete step toward the
target pattern. Both files compile clean under `python3 -m py_compile`.

1. **`spaceinvaders/spaceinvaders.py`** — added an `argparse`-based
   `--autoplay` flag to `main()`. When passed, the start screen is bypassed
   and `Game.new_game(auto_mode=True)` is invoked directly. The existing
   `A`-key start-screen path is unchanged. This is the first game with a
   CLI `--autoplay` flag matching the proposed target pattern.

2. **`minesweeper/minesweeper_with_solver.py`** — migrated from the
   positional `sys.argv[1]` solver-name convention to a proper
   `argparse`-based `--solver <name>` flag. The positional form is still
   accepted (hidden in `--help`) so existing scripts/READMEs continue to
   work. After this change, both games with pluggable solvers (sudoku and
   minesweeper_with_solver) use a consistent `--solver` CLI.

Everything else in this document is deliberately scoped to follow-up
tickets — T-000057 is an inventory + design ticket, not a sweeping
refactor.
