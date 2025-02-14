# SimpleGames 🎮

Welcome to **SimpleGames**! This is an open-source project featuring classic games built with Python. The project includes both interactive and AI-enhanced features, making it ideal for anyone interested in game development, AI, and the power of Python.

## 📚 Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Future Plans](#future-plans)
6. [Contributing](#contributing)
7. [License](#license)

## 🌟 Features

### Current Games
- **2048 with AI Solver** 🔢  
  Enjoy the addictive 2048 game where numbers merge to reach 2048 alongside an AI solver.
- **Bricks** 🧱  
  Challenge your reflexes in this classic brick-breaking arcade game.
- **FlappyBird** 🐦  
  Navigate through pipes in this fast-paced FlappyBird clone.
- **Game of Life** 🧬  
  Witness Conway’s cellular automaton evolve with interactive simulation.
- **Mazes** 🌀  
  Tackle intricate maze puzzles in both grid and hexagonal formats.
- **Minesweeper with Solver** 🧩  
  Uncover hidden mines with strategic logic enhanced by a built-in solver.
- **Pong** 🏓  
  Experience the timeless gameplay of the classic Pong game.
- **Sudoku with Solver** 🔢  
  Solve challenging Sudoku puzzles aided by an intelligent solver.
- **Tetris** 🎮  
  Enjoy the classic Tetris challenge with dynamic falling pieces.
- **Chess Replay Viewer** ♔♕  
  Relive chess games move-by-move by loading and replaying PGN files.

### Usage
1. Place your PGN file in the `pgns` folder (or provide the path to any other location).
2. Run the script:
   ```bash
   python chess_player.py path/to/your_game.pgn
   ```

## 🛠️ Tech Stack

- **[PyGame](https://www.pygame.org/)** for interactive game interfaces.
- **[Flask](https://flask.palletsprojects.com/)** for hosting the AI-based 2048 solver.
- **HTTP Client** to communicate with the AI solver for 2048.

## 🤖 AI-Generated Code

This project is also a showcase of **AI-assisted development**. Over 90% of the code was generated using tools like **GitHub Copilot**, **OpenAI**, and **Claude**. These tools helped streamline everything from game logic to integrating AI features, making SimpleGames a testament to the power of AI in coding.

## 🚀 Future Plans

We’re excited to keep expanding SimpleGames with more classic games and AI functionalities:
Sudoku and Chess are done

Stay tuned for these additions and more!

## 🛠️ Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/muonium-ai/simplegames.git
   cd simplegames
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Games:**
Each game project has a readme in the folder
   - **Minesweeper**:
     ```bash
     python minesweeper.py
     ```
   - **2048**:
     ```bash
     python 2048.py
     ```
   - **2048 AI Solver** (starts Flask server):
     ```bash
     python ai_solver.py
     ```
   - The 2048 game can make HTTP requests to the AI solver to see AI strategies in action.
   **Chess Replay Viewer**
      ```bash
      python chess_player.py path/to/your_game.pgn
      ```

## 🎮 Usage

Each game has its own controls and guidelines:

- **Minesweeper**: Left-click to uncover tiles, and right-click to mark mines.
- **2048**: Use arrow keys to move tiles and combine them. Try enabling the AI solver to watch the AI solve 2048 in real-time!

## 🌐 Contributing

Contributions are welcome! If you have ideas, bug fixes, or new features, please feel free to:

1. Fork the repository.
2. Create a new branch (`feature/your-feature`).
3. Commit changes and open a pull request.

Check out the [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

We hope you enjoy SimpleGames! Dive into the code, play around with the games, and join us in expanding this open-source project. Let’s have some fun with Python and AI! 🚀


## TODO

1. Test the code in linux and mac and fix their issues
2. Remove codes which are not used anymore as code is in git repo in history
3. standardise code and solver invoking across all the games