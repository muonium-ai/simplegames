# Unity Port Plan

A pragmatic assessment of which games in this repo are worth porting to Unity, and what the friction looks like for each one.

## Why Unity (and what it changes)

Unity is C# + a scene/MonoBehaviour pattern, with strong built-in 2D sprites, 3D models, and PhysX. What translates cleanly:

- Grid logic, sprite movement, keyboard/mouse input
- Coroutines for tick-based simulations
- Prefabs for repeated entities (bricks, enemies, bullets)
- Built-in audio, particles, UI

What creates friction:

- Python-specific libraries (Kociemba solver, python-chess)
- Custom 2D physics with exact numeric parity (PhysX behaves differently from a hand-rolled vector loop)
- Flask servers and other backend services — Unity isn't a server platform
- Heavy command-line/argparse plumbing — Unity is launch-from-binary

## Tier 1 — natural Unity fits (small effort)

These are textbook Unity tutorials. Re-implementing them gives you a portfolio of polished mini-games quickly.

| Game | Why it fits |
|---|---|
| **pong** | Two paddles, one ball, score — the canonical Unity beginner tutorial |
| **snake** | Grid logic + sprite tail; multi-snake variant maps well to AI agents |
| **tetris** | Falling-block grid; rotation, lock, clear translate 1:1 |
| **bricks** | Breakout-style; Unity 2D physics covers paddle, ball, brick |
| **flappybird** | Side-scroller with gravity; tap-to-jump is one Input line |
| **spaceinvaders** | Sprite swarm + bullets; prefabs + colliders are ideal |
| **asteroid** | Vector physics already custom in Python — keep it or swap for Rigidbody2D |
| **2048** | Pure grid logic; UI is a 4×4 grid of TextMeshPro cells |
| **minesweeper** | Grid + click events; solver ports cleanly to C# |
| **sudoku** | Same shape — grid + input; solvers re-implement cleanly |
| **mazes (grid)** | DFS/BFS in C# is trivial |
| **gameoflife** | 2D array tick on a coroutine |

## Tier 2 — good fit, some friction

Worth porting but expect dependency work or asset re-import.

| Game | Friction |
|---|---|
| **rubiks_cube (3D version)** | Unity's 3D engine actually makes this *easier* than the current PyOpenGL version — but the Kociemba solver dependency needs a C# replacement (a port exists, or implement layer-by-layer) |
| **card_games (blackjack, klondike, solitaire)** | Logic is easy; need to re-import card image assets and rebuild drag-drop in Unity UI |
| **mazes (hexagonal)** | Hex rendering needs custom mesh or hex-grid asset; logic ports fine |
| **chess (replay viewer)** | `python-chess` has no direct Unity equivalent — use a C# chess library (ChessDotNet) or write PGN parsing yourself |

## Tier 3 — harder / questionable value

These either lose too much in translation, depend on services Unity doesn't host, or have nothing visual to port.

| Game | Issue |
|---|---|
| **genetic_car** | GA + neural net + custom physics. Doable, but Unity's PhysX is overkill and numeric parity will drift. More natural to keep in Python, or rebuild on Unity ML-Agents |
| **2048 AI solver** | Flask HTTP server + MCTS pipeline. The *game* ports to Unity easily; the solver service stays a separate Python backend the Unity client calls over HTTP |
| **chess-game** | Pure-logic module with no UI. "Porting" means writing a new Unity UI on top of a C# chess engine — effectively a from-scratch game |

## Already Apple-native

- **slidergame** is already Swift + SpriteKit. Unity port is possible but redundant unless you want cross-platform.

## Suggested execution order

Tackle them in a sequence that builds up reusable Unity infrastructure:

1. **pong** — input, scoring, scene reload
2. **tetris** — grid state, rotation, render loop
3. **snake** — grid + growing entity, food spawn
4. **2048** — pure-grid UI with animations
5. **flappybird, spaceinvaders, asteroid, bricks** — sprite movement, projectiles, swarms, particle effects
6. **minesweeper, sudoku, mazes** — grid puzzlers (share UI patterns)
7. **card_games** — sprite drag/drop + asset pipeline
8. **chess (replay)** — third-party-library integration (ChessDotNet)
9. **rubiks_cube_3d** — show off Unity's 3D advantage; tackle Kociemba port last

Steps 1–4 give you a reusable Unity project template (input handlers, audio bus, scene-loader, score persistence) that the rest of the games can inherit from.

## Suggested Unity project structure

```
SimpleGamesUnity/
├── Assets/
│   ├── _Shared/           # common helpers: ScoreStore, InputHelpers, SceneLoader
│   ├── Pong/              # one folder per game
│   │   ├── Scenes/
│   │   ├── Scripts/
│   │   └── Prefabs/
│   ├── Tetris/
│   └── ...
├── Packages/
└── ProjectSettings/
```

Each game gets its own scene and a top-level menu scene routes between them. Shared utilities live in `_Shared/` so a `ScoreStore` written for Pong is reused by Snake, Tetris, and 2048.

## Things to decide before starting

- **Target platform**: desktop only (Windows/macOS/Linux) is fastest; mobile adds touch-input rework; WebGL is great for sharing but limits some features (e.g., file I/O for PGN replay).
- **Unity version**: pin one LTS (e.g., 2022.3 LTS or 6 LTS) for the whole repo.
- **Render pipeline**: 2D Renderer (URP) covers all Tier 1 cleanly; the Rubik's Cube 3D version benefits from URP's lighting too.
- **Source layout**: keep the Unity project alongside this Python repo as a sibling directory, or as a `unity/` subfolder. Sibling is cleaner if you want separate CI.
