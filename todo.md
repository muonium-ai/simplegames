# Archived Ticket Verification TODO

Generated: 2026-03-05

Purpose: verify each archived ticket and map it to concrete source lines containing the implemented fix.

## Verification Legend
- ✅ `verified-code` = direct code fix located with line references.
- ⚠️ `verified-no-direct-code` = ticket archived but no specific source-code delta (workflow/coordination/admin ticket).

## Ticket-by-ticket verification

- [x] T-000001 — ⚠️ verified-no-direct-code (example seed ticket; no real game-code fix linked)
- [x] T-000002 — ✅ verified-code: `2048/game_2048/gui.py:5`, `2048/server.py:8`, `2048/server.py:92`, `2048/test_2048.py:28`, `2048/test_2048.py:59`
- [x] T-000003 — ✅ verified-code: `asteroid/asteroid.py:281`, `asteroid/asteroid.py:480`, `asteroid/asteroid.py:487-488`
- [x] T-000004 — ✅ verified-code: `bricks/brick_levels/bricks_levels.py:104`
- [x] T-000005 — ✅ verified-code: `card_games/solitaire-klondike/solitaire.py:9`, `:12`, `:15`, `:16`
- [x] T-000006 — ✅ verified-code: `chess-game/game/player.py:6`, `chess-game/game/minimax_computer_player.py:10`
- [x] T-000007 — ✅ verified-code: `flappybird/flappy_bird.py:17-19`, `flappybird/flappy_bird.py:27`, `flappybird/flappy_bird.py:32`
- [x] T-000008 — ✅ verified-code: `gameoflife/gameoflife.py:11`, `:16`, `:30`, `:32`, `:43`
- [x] T-000009 — ✅ verified-code: `genetic_car/genetic_car.py:216`
- [x] T-000010 — ✅ verified-code: `mazes/grid_maze.py:6`, `:103`, `:167`; `mazes/hexagonal_maze.py:285`, `:287`
- [x] T-000011 — ✅ verified-code: `minesweeper/minesweeper/minesweeper.py:6`, `minesweeper/v2/common.py:3`, `minesweeper/v2/minesweeper.py:3`
- [x] T-000012 — ✅ verified-code: `pong/pong.py:1`, `:109`, `:191`, `:194-195`
- [x] T-000013 — ✅ verified-code: `rubiks_cube/rubiks_cube.py:5`, `rubiks_cube/rubiks_cube_3d.py:5-6`, `rubiks_cube/rubiks_cube_3d.py:59`
- [x] T-000014 — ✅ verified-code: `slidergame/Makefile:61-69`, `slidergame/Makefile:63`, `slidergame/scripts/run_ios_sim.sh:25`, `:46`, `:55`, `:58`
- [x] T-000015 — ✅ verified-code: `snake/snake.py:200`
- [x] T-000016 — ✅ verified-code: `spaceinvaders/spaceinvaders.py:141`
- [x] T-000017 — ✅ verified-code: `sudoku/main.py:36`, `:43`
- [x] T-000018 — ✅ verified-code: `tetris/tetris.py:119-140` (row-clear hardening), `tetris/tetris.py:120`
- [x] T-000019 — ⚠️ verified-no-direct-code (repo-wide coordination/index ticket; no direct source-code patch linked)
- [x] T-000020 — ✅ verified-code: `2048/game_2048/gui.py:5`, `2048/server.py:92`, `2048/test_2048.py:28`, `2048/test_2048.py:59`
- [x] T-000021 — ✅ verified-code: `asteroid/asteroid.py:281`, `asteroid/asteroid.py:487-488`
- [x] T-000022 — ✅ verified-code: `bricks/brick_levels/bricks_levels.py:104`
- [x] T-000023 — ✅ verified-code: `card_games/solitaire-klondike/solitaire.py:9`, `:12`, `:15`, `:16`
- [x] T-000024 — ✅ verified-code: `chess-game/game/player.py:6`, `chess-game/game/minimax_computer_player.py:10`
- [x] T-000025 — ✅ verified-code: `chess-game/game/player.py:6`, `chess-game/game/minimax_computer_player.py:10`
- [x] T-000026 — ✅ verified-code: `flappybird/flappy_bird.py:17-19`, `flappybird/flappy_bird.py:27-32`
- [x] T-000027 — ✅ verified-code: `gameoflife/gameoflife.py:11`, `:16`, `:30`, `:32`, `:43`
- [x] T-000028 — ✅ verified-code: `genetic_car/genetic_car.py:216`
- [x] T-000029 — ✅ verified-code: `mazes/grid_maze.py:6`, `:103`, `:167`; `mazes/hexagonal_maze.py:285`, `:287`
- [x] T-000030 — ✅ verified-code: `minesweeper/minesweeper/minesweeper.py:6`, `minesweeper/v2/common.py:3`, `minesweeper/v2/minesweeper.py:3`
- [x] T-000031 — ✅ verified-code: `pong/pong.py:109`, `:191`, `:194-195`
- [x] T-000032 — ✅ verified-code: `rubiks_cube/rubiks_cube.py:5`, `rubiks_cube/rubiks_cube_3d.py:5-6`, `rubiks_cube/rubiks_cube_3d.py:59`
- [x] T-000033 — ✅ verified-code: `slidergame/Makefile:61-69`, `slidergame/scripts/run_ios_sim.sh:25`, `:46`, `:55`, `:58`
- [x] T-000034 — ✅ verified-code: `snake/snake.py:200`
- [x] T-000035 — ✅ verified-code: `spaceinvaders/spaceinvaders.py:141`
- [x] T-000036 — ✅ verified-code: `sudoku/main.py:36`, `:43`
- [x] T-000037 — ✅ verified-code: `tetris/tetris.py:119-140`

## Notes
- Ticket pairs (broad + line-review) often map to the same source-file fixes, so line references can repeat.
- Two tickets were coordination/admin in nature (`T-000001`, `T-000019`) and do not map to a direct gameplay code patch.
