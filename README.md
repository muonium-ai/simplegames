

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
1. **Minesweeper with Solver** 🧩
   - The classic logic game where players uncover tiles and avoid hidden mines. Simple, fun, and challenging!

2. **2048 with AI Solver** 🔢
   - Enjoy the addictive 2048 game, where numbers merge to reach the 2048 tile!
   - **AI Solver**: A unique addition to this project, the AI solver is implemented using Flask and runs through HTTP requests. You can watch an AI tackle the game, exploring how an algorithm strategizes for optimal moves.

2. **Sudoku with Solver** 🔢
   - The Sudoku Game with Solver in SimpleGames offers the classic puzzle experience where players fill a 9x9 grid following Sudoku rules. Additionally, it includes an AI-based solver that can help players find solutions. 


## 🛠️ Tech Stack

- **[PyGame](https://www.pygame.org/)** for interactive game interfaces.
- **[Flask](https://flask.palletsprojects.com/)** for hosting the AI-based 2048 solver.
- **HTTP Client** to communicate with the AI solver for 2048.

## 🤖 AI-Generated Code

This project is also a showcase of **AI-assisted development**. Over 90% of the code was generated using tools like **GitHub Copilot**, **OpenAI**, and **Claude**. These tools helped streamline everything from game logic to integrating AI features, making SimpleGames a testament to the power of AI in coding.

## 🚀 Future Plans

We’re excited to keep expanding SimpleGames with more classic games and AI functionalities:
1. **Sudoku**: Implementing game mode and solver functionalities.
2. **Chess**: A fully playable chess game with AI move suggestions to challenge players.

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