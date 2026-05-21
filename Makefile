# Run the games via uv.
#
# Usage:
#   make                          # show help
#   make install                  # uv sync (install/refresh deps)
#   make list                     # list every game target
#   make <game>                   # run a game (see `make list`)
#   make chess PGN=path/to.pgn    # chess replay viewer needs a PGN file
#   make 2048-server              # start the 2048 AI solver Flask service

PY ?= uv run python

GAMES := 2048 asteroid blackjack bricks chess chess-autoplay \
         flappybird gameoflife genetic-car grid-maze hex-maze \
         klondike minesweeper minesweeper-probability minesweeper-solver \
         multi-snake pong rubiks rubiks-3d snake solitaire \
         spaceinvaders sudoku tetris

EXTRA_TARGETS := 2048-server

.PHONY: help install list $(GAMES) $(EXTRA_TARGETS)

help:
	@echo "SimpleGames - pygame collection"
	@echo ""
	@echo "Common targets:"
	@echo "  make install                  # uv sync (install/refresh deps)"
	@echo "  make list                     # list every game target"
	@echo "  make <game>                   # run a game (see 'make list')"
	@echo "  make chess PGN=path/to.pgn    # chess replay viewer needs a PGN file"
	@echo "  make 2048-server              # start the 2048 AI solver Flask service"
	@echo ""
	@echo "Run 'make list' for the full set of games."

list:
	@printf '  %s\n' $(sort $(GAMES) $(EXTRA_TARGETS))

install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. See https://docs.astral.sh/uv/"; exit 1; }
	uv sync

# --- Games ---

2048:
	$(PY) 2048/2048.py

2048-server:
	$(PY) 2048/2048_server.py

asteroid:
	$(PY) asteroid/asteroid.py

blackjack:
	$(PY) card_games/blackjack/blackjack.py

bricks:
	$(PY) bricks/bricks.py

chess:
	@if [ -z "$(PGN)" ]; then \
	  echo "chess needs a PGN file: make chess PGN=path/to/your.pgn" >&2; \
	  exit 1; \
	fi
	$(PY) chess/chess_player.py $(PGN)

chess-autoplay:
	$(PY) chess/chess_autoplay.py

flappybird:
	$(PY) flappybird/flappy_bird.py

gameoflife:
	$(PY) gameoflife/gameoflife.py

genetic-car:
	$(PY) genetic_car/genetic_car.py

grid-maze:
	$(PY) mazes/grid_maze.py

hex-maze:
	$(PY) mazes/hexagonal_maze.py

klondike:
	$(PY) card_games/klondike/klondike.py

minesweeper:
	$(PY) minesweeper/minesweeper.py

minesweeper-probability:
	$(PY) minesweeper/minesweeper_with_probability.py

minesweeper-solver:
	$(PY) minesweeper/minesweeper_with_solver.py

multi-snake:
	$(PY) snake/multi-snake.py

pong:
	$(PY) pong/pong.py

rubiks:
	$(PY) rubiks_cube/rubiks_cube.py

rubiks-3d:
	$(PY) rubiks_cube/rubiks_cube_3d.py

snake:
	$(PY) snake/snake.py

solitaire:
	$(PY) card_games/solitaire/Solitaire.py

spaceinvaders:
	$(PY) spaceinvaders/spaceinvaders.py

sudoku:
	$(PY) sudoku/main.py

tetris:
	$(PY) tetris/tetris.py
