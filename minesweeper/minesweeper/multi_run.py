# run_multiple_times.py

import sys
import subprocess

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_multiple_times.py <N> <filename> [solver] [debug]")
        sys.exit(1)

    # Parse arguments
    try:
        N = int(sys.argv[1])
        filename = sys.argv[2]
    except ValueError:
        print("Error: N must be an integer.")
        sys.exit(1)

    # Optional arguments
    solver = sys.argv[3] if len(sys.argv) > 3 else None
    debug = sys.argv[4] if len(sys.argv) > 4 else None

    # Prepare command with optional arguments
    base_command = ["python", filename]
    if solver:
        base_command.append(solver)
    if debug:
        base_command.append(debug)

    # Run the specified file N times
    for i in range(N):
        print(f"Running {filename}, iteration {i + 1}/{N}")
        result = subprocess.run(base_command, capture_output=True, text=True)

        # Print output and errors from each run
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Error:\n{result.stderr}")

if __name__ == "__main__":
    main()
