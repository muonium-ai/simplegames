import Foundation

// A generic Priority Queue (Min-Heap) implementation
struct PriorityQueue<T: Comparable> {
    private var heap: [T] = []

    var isEmpty: Bool {
        return heap.isEmpty
    }

    var count: Int {
        return heap.count
    }

    mutating func enqueue(_ element: T) {
        heap.append(element)
        siftUp(from: heap.count - 1)
    }

    mutating func dequeue() -> T? {
        guard !isEmpty else { return nil }
        heap.swapAt(0, heap.count - 1)
        let element = heap.removeLast()
        siftDown(from: 0)
        return element
    }

    private mutating func siftUp(from index: Int) {
        var childIndex = index
        let child = heap[childIndex]
        var parentIndex = (childIndex - 1) / 2
        
        while childIndex > 0 && child < heap[parentIndex] {
            heap[childIndex] = heap[parentIndex]
            childIndex = parentIndex
            parentIndex = (childIndex - 1) / 2
        }
        heap[childIndex] = child
    }

    private mutating func siftDown(from index: Int) {
        let parentIndex = index
        while true {
            let leftChildIndex = 2 * parentIndex + 1
            let rightChildIndex = leftChildIndex + 1
            var candidate = parentIndex
            
            if leftChildIndex < heap.count && heap[leftChildIndex] < heap[candidate] {
                candidate = leftChildIndex
            }
            if rightChildIndex < heap.count && heap[rightChildIndex] < heap[candidate] {
                candidate = rightChildIndex
            }
            if candidate == parentIndex {
                return
            }
            heap.swapAt(parentIndex, candidate)
            siftDown(from: candidate)
        }
    }
}


// Represents a state of the puzzle board. Must be Hashable for use in Sets.
struct PuzzleState: Hashable {
    let board: [Int]
    let size: Int
    let emptyTileIndex: Int

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
}

// A node in the search tree
class SolverNode: Comparable {
    let state: PuzzleState
    let parent: SolverNode?
    let g: Int // Cost from start
    let h: Int // Heuristic cost to goal
    private let strategy: SolverStrategy

    var f: Int {
        switch strategy {
        case .aStar:
            return g + h
        case .greedy:
            return h
        }
    }

    init(state: PuzzleState, parent: SolverNode?, g: Int, strategy: SolverStrategy) {
        self.state = state
        self.parent = parent
        self.g = g
        self.h = state.manhattanDistance()
        self.strategy = strategy
    }

    static func < (lhs: SolverNode, rhs: SolverNode) -> Bool {
        if lhs.f == rhs.f {
            return lhs.g > rhs.g // Prefer deeper paths for tie-breaking in greedy
        }
        return lhs.f < rhs.f
    }

    static func == (lhs: SolverNode, rhs: SolverNode) -> Bool {
        return lhs.state == rhs.state
    }
}

enum SolverStrategy {
    case aStar
    case greedy
}

class PuzzleSolver {
    func solve(initialState: PuzzleState) -> [PuzzleState]? {
        let strategy: SolverStrategy = initialState.size > 3 ? .greedy : .aStar
        
        var openSet = PriorityQueue<SolverNode>()
        var closedSet = Set<PuzzleState>()

        let startNode = SolverNode(state: initialState, parent: nil, g: 0, strategy: strategy)
        openSet.enqueue(startNode)

        while let currentNode = openSet.dequeue() {
            if currentNode.state.isGoal() {
                return reconstructPath(from: currentNode)
            }

            closedSet.insert(currentNode.state)

            for neighborState in generateNeighbors(for: currentNode.state) {
                if closedSet.contains(neighborState) {
                    continue
                }

                let gScore = currentNode.g + 1
                let neighborNode = SolverNode(state: neighborState, parent: currentNode, g: gScore, strategy: strategy)
                
                // A more optimized version would check if a better path to this state already exists in the open set.
                // For this greedy approach, we prioritize speed of implementation.
                openSet.enqueue(neighborNode)
            }
        }

        return nil // No solution found
    }

    private func generateNeighbors(for state: PuzzleState) -> [PuzzleState] {
        var neighbors: [PuzzleState] = []
        let emptyIndex = state.emptyTileIndex
        let size = state.size
        let emptyRow = emptyIndex / size
        let emptyCol = emptyIndex % size

        let moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] // Up, Down, Left, Right

        for move in moves {
            let newRow = emptyRow + move.0
            let newCol = emptyCol + move.1

            if newRow >= 0 && newRow < size && newCol >= 0 && newCol < size {
                let newIndex = newRow * size + newCol
                var newBoard = state.board
                newBoard.swapAt(emptyIndex, newIndex)
                let newState = PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex)
                neighbors.append(newState)
            }
        }
        return neighbors
    }

    private func reconstructPath(from node: SolverNode) -> [PuzzleState] {
        var path: [PuzzleState] = []
        var currentNode: SolverNode? = node
        while currentNode != nil {
            path.insert(currentNode!.state, at: 0)
            currentNode = currentNode?.parent
        }
        return path
    }
}
