# main.py

import sys
import importlib
from minesweeper import Minesweeper

def load_solver(solver_name):
    """Dynamically load a solver from the solvers folder."""
    try:
        solver_module = importlib.import_module(f'solvers.{solver_name}')
        SolverClass = getattr(solver_module, 'Solver')
        print(f"Using solver: {solver_name}")
        return SolverClass
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error loading solver '{solver_name}': {e}")
        return None

if __name__ == "__main__":
    solver_name = sys.argv[1] if len(sys.argv) > 1 else None
    SolverClass = load_solver(solver_name) if solver_name else None
    game = Minesweeper(solver=SolverClass)
    game.run()
