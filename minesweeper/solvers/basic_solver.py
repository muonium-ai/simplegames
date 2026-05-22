"""Single-cell deduction solver.

For each revealed numbered cell, count its hidden and flagged neighbours.
If `number - flagged == 0`, every hidden neighbour is safe. If
`number - flagged == len(hidden)`, every hidden neighbour is a mine.
When no certain move is available, pick the lowest-probability frontier
cell (lowest local mine fraction from any adjacent constraint, falling
back to the global base probability)."""
from collections import deque

from minesweeper_with_solver import MINE_COUNT


def _neighbors(x, y, w, h):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny


class Solver:
    def __init__(self, game):
        self.game = game
        self.queue = deque()
        self.first_move = True
        # Resolved lazily on first next_move(): game.grid doesn't exist
        # yet when load_solver runs Solver(game). Pulling CellState from
        # a live cell avoids the __main__-vs-imported double-Enum trap
        # where `from minesweeper_with_solver import CellState` returns a
        # different Enum class than the one the framework's cells use.
        self.CellState = None

    def _resolve_cell_state(self):
        if self.CellState is None:
            self.CellState = type(self.game.grid[0][0].state)

    def _w(self):
        return self.game.GRID_WIDTH

    def _h(self):
        return self.game.GRID_HEIGHT

    def _grid(self):
        return self.game.grid

    def _hidden_cells(self):
        w, h = self._w(), self._h()
        g = self._grid()
        return [
            (x, y) for y in range(h) for x in range(w)
            if g[y][x].state == self.CellState.HIDDEN
        ]

    def _flagged_count(self):
        return sum(1 for row in self._grid() for c in row if c.state == self.CellState.FLAGGED)

    def _deduce(self):
        w, h = self._w(), self._h()
        g = self._grid()
        mines = set()
        safes = set()
        for y in range(h):
            for x in range(w):
                c = g[y][x]
                if c.state != self.CellState.REVEALED or c.neighbor_mines <= 0:
                    continue
                hidden = []
                flagged = 0
                for nx, ny in _neighbors(x, y, w, h):
                    n = g[ny][nx]
                    if n.state == self.CellState.FLAGGED:
                        flagged += 1
                    elif n.state == self.CellState.HIDDEN:
                        hidden.append((nx, ny))
                if not hidden:
                    continue
                remaining = c.neighbor_mines - flagged
                if remaining == 0:
                    safes.update(hidden)
                elif remaining == len(hidden):
                    mines.update(hidden)
        return mines, safes

    def _pick_guess(self):
        w, h = self._w(), self._h()
        g = self._grid()
        hidden_cells = self._hidden_cells()
        if not hidden_cells:
            return None
        flagged = self._flagged_count()
        base = max(0, MINE_COUNT - flagged) / len(hidden_cells)
        best_prob = float("inf")
        best_cell = None
        for x, y in hidden_cells:
            local_min = base
            for nx, ny in _neighbors(x, y, w, h):
                c = g[ny][nx]
                if c.state == self.CellState.REVEALED and c.neighbor_mines > 0:
                    hidden = 0
                    flagged_nb = 0
                    for nnx, nny in _neighbors(nx, ny, w, h):
                        nn = g[nny][nnx]
                        if nn.state == self.CellState.HIDDEN:
                            hidden += 1
                        elif nn.state == self.CellState.FLAGGED:
                            flagged_nb += 1
                    if hidden > 0:
                        local_min = min(local_min, (c.neighbor_mines - flagged_nb) / hidden)
            if local_min < best_prob:
                best_prob = local_min
                best_cell = (x, y)
        return best_cell

    def next_move(self):
        self._resolve_cell_state()
        if self.queue:
            x, y, action = self.queue.popleft()
            # Skip stale entries: the framework changes state between calls.
            if self._grid()[y][x].state != self.CellState.HIDDEN:
                return self.next_move()
            return (x, y, action)
        if self.first_move:
            self.first_move = False
            return (self._w() // 2, self._h() // 2, "reveal")
        mines, safes = self._deduce()
        for x, y in mines:
            self.queue.append((x, y, "flag"))
        for x, y in safes:
            self.queue.append((x, y, "reveal"))
        if self.queue:
            return self.next_move()
        guess = self._pick_guess()
        if guess is None:
            return None
        return (guess[0], guess[1], "reveal")
