#!/usr/bin/env bash
# Run every SimpleGames target sequentially via the Makefile.
#
# Usage:
#   ./play-all.sh              # run all games in order
#   ./play-all.sh --from snake # resume starting at a specific game
#
# Press ESC inside each game to quit it and advance to the next.
# Ctrl-C anywhere aborts the whole sequence.

set -u

cd "$(dirname "$0")"

# Order mirrors the Makefile's GAMES list.
GAMES=(
  2048
  asteroid
  blackjack
  bricks
  chess-autoplay
  flappybird
  gameoflife
  genetic-car
  grid-maze
  hex-maze
  klondike
  minesweeper
  minesweeper-probability
  minesweeper-solver
  multi-snake
  pong
  rubiks
  rubiks-3d
  snake
  solitaire
  spaceinvaders
  sudoku
  tetris
)

# Targets that need extra arguments or aren't a "game" you sit and play.
# (chess needs a PGN file; 2048-server is a Flask service.)
SKIP_NOTE=(
  "chess         - needs PGN: 'make chess PGN=path/to/your.pgn'"
  "2048-server   - background Flask service: 'make 2048-server'"
)

start_at=""
if [[ "${1:-}" == "--from" && -n "${2:-}" ]]; then
  start_at="$2"
fi

total=${#GAMES[@]}
i=0
seen_start=0
if [[ -z "$start_at" ]]; then
  seen_start=1
fi

printf "Playing %d games sequentially.\n" "$total"
printf "Press ESC inside each game to quit it and advance.\n"
printf "Ctrl-C here to abort the whole sequence.\n\n"

for game in "${GAMES[@]}"; do
  i=$((i + 1))

  if [[ $seen_start -eq 0 ]]; then
    if [[ "$game" == "$start_at" ]]; then
      seen_start=1
    else
      continue
    fi
  fi

  printf "\n========================================\n"
  printf "[%d/%d] Launching: %s\n" "$i" "$total" "$game"
  printf "========================================\n\n"

  make "$game"
  status=$?

  if [[ $status -ne 0 ]]; then
    printf "\n%s exited with status %d.\n" "$game" "$status"
  fi
done

printf "\nAll games finished.\n\n"
printf "Skipped (handle manually if you want them):\n"
for note in "${SKIP_NOTE[@]}"; do
  printf "  %s\n" "$note"
done
