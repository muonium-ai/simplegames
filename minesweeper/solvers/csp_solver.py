"""Constraint enumeration / CSP solver.

Splits the frontier into connected components (constraints sharing any
cell), enumerates every valid mine configuration per component via
backtracking with constraint propagation, and computes exact P(mine)
for each frontier cell. Cells with P=0 are revealed; P=1 are flagged.
For guesses, the minimum exact probability across the frontier wins;
interior cells (not adjacent to any constraint) use a residual base
probability derived from the global mine count minus the frontier's
expected mines.

Components whose enumeration would exceed MAX_CONFIGS configurations
are skipped — their cells fall back to base probability for guessing.
This bounds worst-case time per move."""
from collections import defaultdict, deque

from minesweeper_with_solver import MINE_COUNT

MAX_CONFIGS = 50000


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
        self._last_probs = {}
        # Resolved lazily on first next_move(): game.grid doesn't exist
        # yet when load_solver runs Solver(game). Pulling CellState from
        # a live cell avoids the __main__-vs-imported double-Enum trap.
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

    def _build_constraints(self):
        w, h = self._w(), self._h()
        g = self._grid()
        out = []
        for y in range(h):
            for x in range(w):
                c = g[y][x]
                if c.state != self.CellState.REVEALED or c.neighbor_mines <= 0:
                    continue
                hidden = []
                flagged = 0
                for nx, ny in _neighbors(x, y, w, h):
                    n = g[ny][nx]
                    if n.state == self.CellState.HIDDEN:
                        hidden.append((nx, ny))
                    elif n.state == self.CellState.FLAGGED:
                        flagged += 1
                if hidden:
                    out.append((frozenset(hidden), c.neighbor_mines - flagged))
        return out

    def _components(self, constraints):
        """Union-find over constraints: two constraints join iff they share a cell."""
        cell_to_cs = defaultdict(set)
        for i, (cells, _) in enumerate(constraints):
            for cell in cells:
                cell_to_cs[cell].add(i)
        parent = list(range(len(constraints)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for cs_set in cell_to_cs.values():
            cs_list = list(cs_set)
            for i in range(1, len(cs_list)):
                a, b = find(cs_list[0]), find(cs_list[i])
                if a != b:
                    parent[a] = b
        groups = defaultdict(list)
        for i in range(len(constraints)):
            groups[find(i)].append(i)
        return list(groups.values())

    def _enumerate(self, comp_indices, all_constraints):
        """Enumerate valid 0/1 assignments to the component's cells.
        Returns (configs, cells_list) or (None, cells_list) if MAX_CONFIGS
        is exceeded (component too large to enumerate safely)."""
        cs = [all_constraints[i] for i in comp_indices]
        cells = sorted({c for cells, _ in cs for c in cells})
        cell_idx = {c: i for i, c in enumerate(cells)}
        n = len(cells)
        # Pre-compute, per constraint, the cell indices it covers.
        cs_idx = [(sorted(cell_idx[c] for c in cells_set), m) for cells_set, m in cs]

        configs = []
        partial = [0] * n
        # For pruning: per-constraint running tally of mines + remaining cells.
        # constraint_pos[k] = next index in cs_idx[k][0] that we haven't decided yet
        cs_count = len(cs_idx)
        # Map: depth -> list of (constraint_idx, position in cs_idx[k][0])
        # for efficient pruning. Build a per-depth list of constraints that include
        # cell `depth`, so we update those at depth time.
        cell_to_constraints = [[] for _ in range(n)]
        for k, (idxs, _) in enumerate(cs_idx):
            for i in idxs:
                cell_to_constraints[i].append(k)
        # Per-constraint state: used mines so far, remaining uncoverable cells.
        used = [0] * cs_count
        remaining = [len(idxs) for idxs, _ in cs_idx]
        target = [m for _, m in cs_idx]

        result_too_big = [False]

        def backtrack(depth):
            if result_too_big[0]:
                return
            if len(configs) > MAX_CONFIGS:
                result_too_big[0] = True
                return
            if depth == n:
                configs.append(tuple(partial))
                return
            for val in (0, 1):
                # Apply
                changed = []
                ok = True
                for k in cell_to_constraints[depth]:
                    used[k] += val
                    remaining[k] -= 1
                    changed.append(k)
                    if used[k] > target[k] or used[k] + remaining[k] < target[k]:
                        ok = False
                if ok:
                    partial[depth] = val
                    backtrack(depth + 1)
                # Undo
                for k in changed:
                    used[k] -= val
                    remaining[k] += 1
            partial[depth] = 0

        backtrack(0)
        if result_too_big[0]:
            return None, cells
        return configs, cells

    def _deduce(self):
        self._last_probs = {}
        constraints = self._build_constraints()
        if not constraints:
            return set(), set()
        components = self._components(constraints)
        mines = set()
        safes = set()
        for comp in components:
            configs, cells = self._enumerate(comp, constraints)
            if configs is None or not configs:
                continue
            n_configs = len(configs)
            for i, cell in enumerate(cells):
                mine_count = sum(c[i] for c in configs)
                p = mine_count / n_configs
                self._last_probs[cell] = p
                if p == 0.0:
                    safes.add(cell)
                elif p == 1.0:
                    mines.add(cell)
        return mines, safes

    def _pick_guess(self):
        hidden_cells = self._hidden_cells()
        if not hidden_cells:
            return None
        flagged = self._flagged_count()
        mines_left = max(0, MINE_COUNT - flagged)
        # Residual mines outside enumerated frontier are spread over interior cells.
        interior = [c for c in hidden_cells if c not in self._last_probs]
        if interior:
            frontier_mines_est = sum(self._last_probs.values())
            interior_mines = max(0.0, mines_left - frontier_mines_est)
            base = interior_mines / len(interior)
        else:
            base = 1.0
        best = (float("inf"), None)
        for cell in hidden_cells:
            p = self._last_probs.get(cell, base)
            if p < best[0]:
                best = (p, cell)
        return best[1]

    def next_move(self):
        self._resolve_cell_state()
        if self.queue:
            x, y, action = self.queue.popleft()
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
