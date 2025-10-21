import Foundation

// Represents a state of the puzzle board. Must be Hashable for use in Sets.
struct PuzzleState: Hashable {
    let board: [Int]
    let size: Int
    var emptyTileIndex: Int

    // Heuristic function: Manhattan Distance
    func manhattanDistance() -> Int {
        var distance = 0
        for (i, value) in board.enumerated() {
            if value != 0 { // 0 is the empty tile
                let goalIndex = value - 1
                let goalRow = goalIndex / size
                let goalCol = goalIndex % size
                let currentRow = i / size
                let currentCol = i % size
                distance += abs(goalRow - currentRow) + abs(goalCol - currentCol)
            }
        }
        return distance
    }

    func isGoal() -> Bool {
        for i in 0..<(board.count - 1) {
            if board[i] != i + 1 {
                return false
            }
        }
        return true
    }
    
    func index(of value: Int) -> Int? {
        return board.firstIndex(of: value)
    }

    func coordinates(of index: Int) -> (row: Int, col: Int) {
        return (index / size, index % size)
    }
}

func generateNeighbors(for state: PuzzleState, restrictedIndices: Set<Int> = []) -> [PuzzleState] {
    var neighbors: [PuzzleState] = []
    let emptyIndex = state.emptyTileIndex
    let size = state.size
    let emptyRow = emptyIndex / size
    let emptyCol = emptyIndex % size

    let moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] // Up, Down, Left, Right

    for move in moves {
        let newRow = emptyRow + move.0
        let newCol = emptyCol + move.1
        let newIndex = newRow * size + newCol

        if newRow >= 0 && newRow < size && newCol >= 0 && newCol < size && !restrictedIndices.contains(newIndex) {
            var newBoard = state.board
            newBoard.swapAt(emptyIndex, newIndex)
            let newState = PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex)
            neighbors.append(newState)
        }
    }
    return neighbors
}
