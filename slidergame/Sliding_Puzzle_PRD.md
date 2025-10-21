# Sliding Puzzle (N‑Puzzle) — Product Requirements Document (PRD)

> Version: 1.0  
> Owner: Product / Game Design  
> Last updated: 2025-10-20  

---

## 0) Summary

A clean, modern take on the classic **sliding tile puzzle** (N‑Puzzle: 3×3, 4×4, … 10×10). Players slide tiles into the empty space to restore numeric order or reassemble an image. The app guarantees **solvable shuffles**, offers multiple modes (Classic, Timed, Move‑Limited, Zen, Daily), and includes an **optimal solver** for hints and replays.

**Targets**: iOS, Android, Web.  
**KPI**: Day‑1 retention ≥ 35%, median session length ≥ 4 minutes, 2+ puzzles/day/user within 2 weeks.

---

## 1) Goals & Non‑Goals

### Goals
- Delightful, tactile sliding‑puzzle experience with smooth animations & haptics.
- Fair shuffling that is **always solvable**.
- Smart hints and **auto‑solve** driven by an optimal/near‑optimal search.
- Shareable **seeded scrambles** (daily & friend challenges).
- Accessibility (large text, high contrast, screen reader labels).

### Non‑Goals
- Competitive PvP.  
- Online multiplayer.  
- Advanced social graph (beyond seed sharing & leaderboards).

---

## 2) Audience & Personas

- **Nostalgic Casual**: quick brain teaser, prefers numbers, short sessions.  
- **Perfectionist Puzzler**: pursues optimal moves & times, uses hints sparingly.  
- **Relaxed Zen**: picture mode, no timer, ASMR‑like feel.  
- **Learner**: appreciates in‑app guides for methods and parity/solvability.

---

## 3) Scope & Modes

### Board Sizes
- 3×3 (8‑puzzle), 4×4 (15‑puzzle) default. Unlock 5×5 … 10×10.

### Modes
- **Classic**: Normal, no constraints.  
- **Timed**: Beat the clock; overtime → time penalty.  
- **Move‑Limited**: Win under **M** moves.  
- **Zen**: No move/time counters.  
- **Daily Puzzle**: Deterministic seed from date.  
- **Picture Pack**: Built‑in gallery + “Use Camera/Photo”.  
- **Hardcore** (optional): Hide numbers in picture mode.

---

## 4) Core Gameplay

- **Controls**: Tap a movable tile to slide; drag/swipe toward the blank; optional multi‑tile slide along a row/column.  
- **Win Condition**: Board matches target ordering (1..N with blank last) or full image alignment.  
- **Scoring**: Moves, time, optimality bonus, board‑size multiplier.  
- **QoL**: Undo/redo, pause, left‑hand/right‑hand swap, high‑contrast theme, haptic on settle.  
- **Assist**: “Show goal” peek overlay; per‑tile lock glow when placed correctly; hint button (next optimal move).

---

## 5) Jumble (Scramble) — **Solvable by Construction**

### A) Random‑Walk Scramble (Recommended)
1. Start from solved state.  
2. Apply **k** random legal moves; avoid immediate backtracks to increase variety.  
3. Result is guaranteed solvable.

**Difficulty mapping (4×4 guidance)**:  
- Easy: k ≈ 20–40  
- Medium: k ≈ 60–100  
- Hard: k ≈ 200–400

### B) Fisher–Yates + Parity Fix
1. Fisher–Yates shuffle including blank (0).  
2. If unsolvable (see test below), swap any **two non‑blank tiles** (flips parity).

**Solvability test (classic N‑puzzle)**  
Let `W` = board width, `inv` = inversion count over tiles excluding the blank, and `rb` = row index of the blank **from the bottom** (1 = bottom row).  
- If `W` is **odd**: solvable iff `inv` is **even**.  
- If `W` is **even**: solvable iff `(inv % 2) != (rb % 2)` (parities differ).

**Pseudocode**
```text
shuffle_solvable(tiles, W):
  do:
    fisher_yates(tiles)              // includes 0 for blank
  while is_goal(tiles)               // avoid trivial start
  if !is_solvable(tiles, W):
    swap(two_non_blank_tiles(tiles)) // flip parity exactly once
  return tiles

is_solvable(tiles, W):
  arr = tiles without 0
  inv = count_inversions(arr)
  rb  = row_from_bottom(index_of(0), W)
  if W % 2 == 1: return inv % 2 == 0
  else:          return (inv % 2) != (rb % 2)
```

### C) Seeded Scrambles
- Seed = `YYYYMMDD` (daily) or user‑shared code. Seed drives RNG for Random‑Walk or Fisher–Yates.

### D) Patterned Jumbles (optional)
- Spiral shifts, mirrored rows/cols, checkerboard pair swaps; always parity‑check & fix.

---

## 6) Built‑in Solver (Hints & Auto‑Solve)

### Algorithm
- **Search**: A* (or IDA* for lower memory on large boards).  
- **Heuristic**: Manhattan Distance + **Linear Conflict** (+2 per pair in same row/column blocking order).  
- **Optimality**: Heuristic is admissible → optimal paths for A* when feasible.

**A* Outline**
```text
a_star(start):
  open = min-PQ keyed by f=g+h
  push(start, g=0, h=H(start))
  while open not empty:
    s = pop_min(open)
    if is_goal(s): return reconstruct_path(s)
    for n in neighbors(s):
      g2 = g(s) + 1
      if g2 < g(n):
        parent[n] = s
        set g(n)=g2, f(n)=g2+H(n)
        push_or_decrease(open, n)
```

**Heuristic H(state)**
```text
H(state) = Σ tiles t (|r(t)-r*(t)| + |c(t)-c*(t)|) + linear_conflict_bonus(state)
```

### Uses
- **Hint**: Next optimal move (or 3‑step preview).  
- **Auto‑Solve**: Replay the optimal path at 1×–3× speed.  
- **Difficulty**: Bucket by optimal path length (4×4: Easy < 30, Med 30–80, Hard > 80).

---

## 7) Content & Visuals

- **Tile Types**: Numbers; Image slices with optional borders & faint ghost background.  
- **Themes**: Light/Dark, High‑contrast, Color‑blind safe.  
- **Assets**: Minimal; rasterizable SVG for numbers, dynamic image slicing.

---

## 8) Accessibility

- Large text toggle, scalable tiles.  
- VoiceOver / TalkBack labels (e.g., “Tile 14, left of blank, movable”).  
- Haptics on valid moves; visual feedback for invalid actions.  
- Color‑blind safe palettes; don’t rely on color alone.

---

## 9) System Architecture

- **Core Engine**: Framework‑agnostic module with:
  - Board representation & legal move gen
  - Solvability utilities (parity, inversions, row‑from‑bottom)
  - Scramblers (Random‑Walk, Fisher–Yates+Fix, Seeded)
  - Solver (A*/IDA*, Manhattan+Linear Conflict)
- **Platforms**
  - **Mobile**: Native (Swift/Kotlin) or cross‑platform (Flutter/React Native).  
  - **Web**: Canvas/WebGL. Arrow‑key support for desktop play.
- **Persistence**: Local (CoreData/Room/IndexedDB). Cloud backup optional.  
- **Share**: Deep links with `seed`, `size`, and `mode` params.

---

## 10) Data Model

```json
GameState {
  "id": "uuid",
  "seed": "string|null",
  "size": 4,
  "tiles": [1,2,3,...,0],         // 0 = blank
  "moves": 123,
  "time_ms": 84567,
  "created_at": 1740142000,
  "completed_at": 1740142900,
  "image_id": "optional",
  "mode": "classic|timed|move_limited|zen|daily|picture",
  "undo_stack": [...],
  "redo_stack": [...]
}
UserPrefs {
  "haptics": true,
  "show_numbers_in_picture": true,
  "left_handed": false,
  "high_contrast": true
}
```

---

## 11) Functional Requirements

### FR‑1 Gameplay
- FR‑1.1 Slide tiles via tap or drag; multi‑tile row/col slides (configurable).  
- FR‑1.2 Legal moves only; invalid attempts give subtle feedback.  
- FR‑1.3 Undo/redo stack up to last 100 moves (configurable).  
- FR‑1.4 Win detection & celebratory animation.

### FR‑2 Scramble
- FR‑2.1 Provide **Random‑Walk** and **Fisher–Yates+Fix** methods.  
- FR‑2.2 Difficulty presets map to scramble lengths.  
- FR‑2.3 Seeded scrambles for **Daily** and share codes.  
- FR‑2.4 100% **solvable** guarantee with unit tests.

### FR‑3 Solver & Hints
- FR‑3.1 A* solver with Manhattan + Linear Conflict.  
- FR‑3.2 “Hint” shows next move; “Auto‑Solve” replays the path.  
- FR‑3.3 Difficulty tagging via optimal path length.

### FR‑4 Modes & Content
- FR‑4.1 Classic, Timed, Move‑Limited, Zen, Daily.  
- FR‑4.2 Picture mode: crop user image into grid, optional numbers overlay.  
- FR‑4.3 Theming & high‑contrast support.

### FR‑5 Accessibility & Input
- FR‑5.1 Large text & scalable UI.  
- FR‑5.2 Screen reader labels for tiles and blank.  
- FR‑5.3 Keyboard arrows on web/desktop.

### FR‑6 Analytics & Share
- FR‑6.1 Log board size, seed, scramble length **k**, optimal distance, user moves/time, hint use.  
- FR‑6.2 Leaderboard (optional) with server‑side verification using solver.  
- FR‑6.3 Deep link sharing of seeds.

---

## 12) Non‑Functional Requirements

- **Performance**: 60 fps target on mid‑tier devices; input→animation latency < 50 ms.  
- **Solver**: Hint computation < 100 ms for 4×4 median boards (on recent phones).  
- **Stability**: Crash‑free sessions ≥ 99.9%.  
- **Battery**: Idle CPU near 0%; no busy loops.  
- **Privacy**: Images stay on device unless user opts into cloud backup.  
- **Localization**: Ready for string externalization.

---

## 13) Human “How to Solve” (In‑App Guide)

1. **Row‑by‑row**: Solve top row left→right; lock completed row.  
2. **Next rows**: Repeat, leaving a 2×N (or 3×2) area to maneuver.  
3. **Pairing/Three‑cycle**: Use the blank to cycle 3 tiles within a 2×3 block without breaking solved rows.  
4. **Finish**: Resolve final 2×2 corner. Scramble parity ensures feasibility.  
5. **Practice Boards**: Interactive micro‑lessons for each maneuver.

---

## 14) Telemetry & KPIs

- Session length, puzzles/day, hint usage, abandon rate before first move.  
- Difficulty distribution & solve rates by size and mode.  
- **Targets**: DAU/WAU ≥ 0.35, Day‑7 retention ≥ 18%, average hints < 1 per Classic puzzle.

---

## 15) Monetization (Optional)

- Free: 3×3–5×5, numbers, daily puzzle, light ads.  
- Premium (IAP/subscription): larger grids, picture packs, themes, ad‑free, Hardcore.  
- Cosmetic only; no pay‑to‑win.

---

## 16) QA & Acceptance Criteria

### Scramble & Solvability
- [ ] 10,000 randomized shuffles per size → **0** unsolvable starts.  
- [ ] Seed `YYYYMMDD` yields identical board across devices.  
- [ ] Random‑Walk difficulty correlates with solver optimal length.

### Solver
- [ ] Matches known optimal lengths on benchmark positions (regression suite).  
- [ ] Hint latency < 100 ms (p50) on 4×4; < 250 ms (p95).  
- [ ] Auto‑Solve reproduces solution path exactly.

### UX/Access
- [ ] Screen reader announces movable tiles & blank position.  
- [ ] Large text option scales without clipping.  
- [ ] 60 fps animations on target devices.

### Stability
- [ ] Crash‑free sessions ≥ 99.9% over 7‑day rolling window.

---

## 17) Milestones & Deliverables

1. **M1 — Core Engine (2 wks)**  
   - Board, moves, scramblers, parity tests, basic solver (A*).  
2. **M2 — UI/Controls (2–3 wks)**  
   - Grid rendering, input, animations, win detection.  
3. **M3 — Modes & Hints (2 wks)**  
   - Timed/Move‑Limited/Zen, hint & auto‑solve, seeded daily.  
4. **M4 — Picture Mode & Accessibility (1–2 wks)**  
   - Image slicing, numbers overlay, screen reader support.  
5. **M5 — Polish & Release (2 wks)**  
   - Themes, SFX/haptics, analytics, QA, store assets.

---

## 18) Open Questions

- Cross‑platform stack: **Flutter vs React Native vs Unity/Godot**?  
- Server components: leaderboards now or post‑MVP?  
- Photo permissions & cloud backup policy.  
- Multi‑tile slide (allowed by UX?) default ON or OFF?

---

## 19) Appendix — Helper Definitions

### Manhattan Distance
For tile `t` at `(r,c)` with goal `(r*,c*)`, `|r−r*| + |c−c*|`.

### Linear Conflict
For any row (or column), if two tiles `a` and `b` both belong in that row (or column) but are in reversed order relative to their goal, add **+2** to the heuristic. Keeps admissibility.

### Random‑Walk Scramble (outline)
```text
scramble_random_walk(state, steps):
  last = None
  repeat steps:
    moves = legal_moves(state)
    if last exists: remove opposite(last) from moves
    m = random_choice(moves)
    state = apply_move(state, m)
    last = m
  return state
```

---

© 2025 Sliding Puzzle Team
