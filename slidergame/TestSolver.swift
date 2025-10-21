#if TEST_HARNESS
import Foundation

struct RandomPuzzle {
    static func generate(size: Int, moves: Int = 100) -> PuzzleState {
        let total = size * size
        var board = Array(1..<total)
        board.append(0)
    let emptyIndex = total - 1

        var state = PuzzleState(board: board, size: size, emptyTileIndex: emptyIndex)
        var rng = SystemRandomNumberGenerator()
        let offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        func neighbors(of state: PuzzleState) -> [PuzzleState] {
            let size = state.size
            let empty = state.emptyTileIndex
            let row = empty / size
            let col = empty % size
            var result: [PuzzleState] = []
            for (dr, dc) in offsets {
                let newRow = row + dr
                let newCol = col + dc
                if newRow >= 0, newRow < size, newCol >= 0, newCol < size {
                    let newIndex = newRow * size + newCol
                    var newBoard = state.board
                    newBoard.swapAt(empty, newIndex)
                    result.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
                }
            }
            return result
        }

        for _ in 0..<moves {
            let options = neighbors(of: state)
            if let next = options.randomElement(using: &rng) {
                state = next
            }
        }
        return state
    }
}

@main
struct Runner {
    static func main() {
        let args = CommandLine.arguments
        let size = args.count > 1 ? max(3, Int(args[1]) ?? 4) : 4
        let trials = args.count > 2 ? max(1, Int(args[2]) ?? 1) : 1
        let moveBudget = max(60, size * size * 3)

        for run in 1...trials {
            let puzzle = RandomPuzzle.generate(size: size, moves: moveBudget)
            print("Run #\(run) size=\(size) puzzle: \(puzzle.board)")
            guard let solution = PuzzleSolver().solve(initialState: puzzle) else {
                print("Failed to solve puzzle on run #\(run)")
                exit(1)
            }
            print("Solved in \(solution.count - 1) moves")
            if let last = solution.last {
                print("Solved board: \(last.board)")
            }
        }
    }
}
#endif
