#!/usr/bin/env bash
# Run every SimpleGames target in autoplay/solver mode with a per-game timeout.
#
# Usage:
#   ./play-all-auto.sh                       # run every autoplayable game (30s each)
#   TIMEOUT_SECS=10 ./play-all-auto.sh        # override per-game timeout
#   ./play-all-auto.sh --from snake          # resume starting at a specific game
#
# This is non-interactive — intended to demo the autoplay rollout. Each game
# runs until it finishes or hits the timeout, then we move on.
# Ctrl-C anywhere aborts the whole sequence.

set -u

cd "$(dirname "$0")"

PY=${PY:-uv run python}
TIMEOUT_SECS=${TIMEOUT_SECS:-30}

# Pick a timeout binary: prefer gtimeout (macOS coreutils), fall back to
# plain timeout (Linux), warn and run without one if neither is available.
TIMEOUT_BIN=""
if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN="gtimeout"
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout"
else
  printf "note: no 'timeout' or 'gtimeout' found; using bash-only fallback.\n" >&2
  printf "      install coreutils (brew install coreutils) for cleaner timeout handling.\n" >&2
fi

# Each entry: "name|command-and-args"
# Skipped (no autoplay or out of scope): 2048, klondike, solitaire, multi-snake,
# minesweeper (tier 1 single-player only), chess (needs PGN), 2048-server.
GAMES=(
  "asteroid|asteroid/asteroid.py --autoplay"
  "blackjack|card_games/blackjack/blackjack.py --autoplay"
  "bricks|bricks/bricks.py --autoplay"
  "chess-autoplay|chess/chess_autoplay.py"
  "chess-game|chess-game/main.py --white minimax --black minimax --delay 0"
  "flappybird|flappybird/flappy_bird.py --autoplay"
  "gameoflife|gameoflife/gameoflife.py"
  "genetic-car|genetic_car/genetic_car.py"
  "grid-maze|mazes/grid_maze.py --autoplay"
  "hex-maze|mazes/hexagonal_maze.py --autoplay"
  "minesweeper-probability|minesweeper/minesweeper_with_probability.py --autoplay"
  "minesweeper-solver|minesweeper/minesweeper_with_solver.py --solver random_solver"
  "pong|pong/pong.py --autoplay both"
  "rubiks|rubiks_cube/rubiks_cube.py --autoplay"
  "rubiks-3d|rubiks_cube/rubiks_cube_3d.py --autoplay"
  "snake|snake/snake.py --autoplay"
  "spaceinvaders|spaceinvaders/spaceinvaders.py --autoplay"
  "sudoku|sudoku/main.py --solver basic_solver"
  "tetris|tetris/tetris.py --autoplay"
)

start_at=""
if [[ "${1:-}" == "--from" && -n "${2:-}" ]]; then
  start_at="$2"
fi

# Validate --from points at a known game; otherwise exit gracefully.
if [[ -n "$start_at" ]]; then
  found=0
  for entry in "${GAMES[@]}"; do
    name="${entry%%|*}"
    if [[ "$name" == "$start_at" ]]; then
      found=1
      break
    fi
  done
  if [[ $found -eq 0 ]]; then
    printf "error: --from '%s' is not a known game.\n" "$start_at" >&2
    printf "known games:\n" >&2
    for entry in "${GAMES[@]}"; do
      printf "  %s\n" "${entry%%|*}" >&2
    done
    exit 1
  fi
fi

total=${#GAMES[@]}
i=0
seen_start=0
if [[ -z "$start_at" ]]; then
  seen_start=1
fi

ran=0
timed_out=0
failed=0
succeeded=0

printf "Running %d games in autoplay mode (timeout=%ss each).\n" "$total" "$TIMEOUT_SECS"
if [[ -n "$TIMEOUT_BIN" ]]; then
  printf "Using '%s' for per-game timeouts.\n" "$TIMEOUT_BIN"
fi
printf "Ctrl-C here to abort the whole sequence.\n\n"

for entry in "${GAMES[@]}"; do
  i=$((i + 1))
  name="${entry%%|*}"
  cmd="${entry#*|}"

  if [[ $seen_start -eq 0 ]]; then
    if [[ "$name" == "$start_at" ]]; then
      seen_start=1
    else
      continue
    fi
  fi

  printf "\n========================================\n"
  printf "[%d/%d] Autoplaying: %s\n" "$i" "$total" "$name"
  printf "       cmd: %s %s\n" "$PY" "$cmd"
  printf "========================================\n\n"

  ran=$((ran + 1))

  # shellcheck disable=SC2086
  if [[ -n "$TIMEOUT_BIN" ]]; then
    $TIMEOUT_BIN "$TIMEOUT_SECS" $PY $cmd
    status=$?
  else
    # Portable bash-only timeout: run the game in the background and SIGTERM
    # it after TIMEOUT_SECS. Treat the kill path as exit code 124 to match
    # GNU timeout semantics so the footer counters line up.
    $PY $cmd &
    game_pid=$!
    ( sleep "$TIMEOUT_SECS" && kill -TERM "$game_pid" 2>/dev/null ) &
    sleeper_pid=$!
    wait "$game_pid" 2>/dev/null
    status=$?
    # If the sleeper is still alive, the game finished on its own — kill the sleeper.
    if kill -0 "$sleeper_pid" 2>/dev/null; then
      kill -TERM "$sleeper_pid" 2>/dev/null
      wait "$sleeper_pid" 2>/dev/null
    else
      # Sleeper already fired — game was killed. Normalize to 124.
      status=124
    fi
  fi

  # GNU timeout exits 124 on SIGTERM, 137 on SIGKILL (timeout --kill-after).
  if [[ $status -eq 124 || $status -eq 137 ]]; then
    timed_out=$((timed_out + 1))
    printf "\n[%s] timed out after %ss (status=%d).\n" "$name" "$TIMEOUT_SECS" "$status"
  elif [[ $status -ne 0 ]]; then
    failed=$((failed + 1))
    printf "\n[%s] exited with status %d.\n" "$name" "$status"
  else
    succeeded=$((succeeded + 1))
  fi
done

printf "\n========================================\n"
printf "Autoplay run complete.\n"
printf "  ran:        %d / %d\n" "$ran" "$total"
printf "  succeeded:  %d\n" "$succeeded"
printf "  timed out:  %d (treated as clean stop)\n" "$timed_out"
printf "  failed:     %d\n" "$failed"
printf "========================================\n"
