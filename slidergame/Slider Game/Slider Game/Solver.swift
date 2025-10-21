import Foundation

// A generic Priority Queue (Min-Heap) implementation for the A* solver
struct PriorityQueue<T: Comparable> {
    private var heap: [T] = []

    var isEmpty: Bool {
        return heap.isEmpty
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
        var parentIndex = index
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
            parentIndex = candidate
        }
    }
}

// Represents a state of the puzzle board.
struct PuzzleState: Hashable {
    let board: [Int]
    let size: Int
    let emptyTileIndex: Int

    func manhattanDistance() -> Int {
        var distance = 0
        for (i, value) in board.enumerated() {
            if value != 0 {
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
        return board.last == 0
    }
}

// Node for the standard A* search
class AStarNode: Comparable {
    let state: PuzzleState
    let parent: AStarNode?
    let g: Int
    let h: Int
    var f: Int { return g + h }

    init(state: PuzzleState, parent: AStarNode?, g: Int) {
        self.state = state
        self.parent = parent
        self.g = g
        self.h = state.manhattanDistance()
    }

    static func < (lhs: AStarNode, rhs: AStarNode) -> Bool {
        return lhs.f < rhs.f
    }

    static func == (lhs: AStarNode, rhs: AStarNode) -> Bool {
        return lhs.state == rhs.state
    }
}

class PuzzleSolver {

    // Main router for solving
    func solve(initialState: PuzzleState) -> [PuzzleState]? {
        if initialState.size <= 3 {
            return solveAStar(initialState: initialState)
        } else {
            return solveIDAStar(initialState: initialState)
        }
    }

    // Standard A* for small puzzles
    private func solveAStar(initialState: PuzzleState) -> [PuzzleState]? {
        var openSet = PriorityQueue<AStarNode>()
        var closedSet = Set<PuzzleState>()

        let startNode = AStarNode(state: initialState, parent: nil, g: 0)
        openSet.enqueue(startNode)

        while let currentNode = openSet.dequeue() {
            if currentNode.state.isGoal() {
                return reconstructAStarPath(from: currentNode)
            }

            closedSet.insert(currentNode.state)

            for neighborState in generateNeighbors(for: currentNode.state) {
                if closedSet.contains(neighborState) {
                    continue
                }
                let gScore = currentNode.g + 1
                let neighborNode = AStarNode(state: neighborState, parent: currentNode, g: gScore)
                openSet.enqueue(neighborNode)
            }
        }
        return nil
    }
    
    // IDA* for larger puzzles
    private func solveIDAStar(initialState: PuzzleState) -> [PuzzleState]? {
        let initialHeuristic = initialState.manhattanDistance()
        var bound = initialHeuristic
        
        while true {
            var path: [PuzzleState] = [initialState]
            var visited: Set<PuzzleState> = [initialState]
            let result = search(&path, &visited, g: 0, bound: bound)
            
            switch result {
            case .found:
                return path
            case .notFound:
                // This case means no solution exists, which shouldn't happen for our puzzles
                return nil
            case .newBound(let newBound):
                bound = newBound
            }
            
            // Safety break for extremely difficult puzzles
            if bound > 100 {
                 print("IDA* bound exceeded 100, aborting.")
                 return nil
            }
        }
    }

    private enum SearchResult {
        case found
        case notFound
        case newBound(Int)
    }

    private func search(_ path: inout [PuzzleState], _ visited: inout Set<PuzzleState>, g: Int, bound: Int) -> SearchResult {
        let currentState = path.last!
        let f = g + currentState.manhattanDistance()

        if f > bound {
            return .newBound(f)
        }
        if currentState.isGoal() {
            return .found
        }

        var minBound: Int = .max

        for neighbor in generateNeighbors(for: currentState) {
            if !visited.contains(neighbor) {
                path.append(neighbor)
                visited.insert(neighbor)
                
                let result = search(&path, &visited, g: g + 1, bound: bound)
                
                switch result {
                case .found:
                    return .found
                case .newBound(let newBound):
                    minBound = min(minBound, newBound)
                case .notFound:
                    break // Continue
                }

                // Backtrack
                visited.remove(path.last!)
                path.removeLast()
            }
        }
        
        return minBound == .max ? .notFound : .newBound(minBound)
    }

    private func generateNeighbors(for state: PuzzleState) -> [PuzzleState] {
        var neighbors: [PuzzleState] = []
        let emptyIndex = state.emptyTileIndex
        let size = state.size
        let emptyRow = emptyIndex / size
        let emptyCol = emptyIndex % size

        let moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for move in moves {
            let newRow = emptyRow + move.0
            let newCol = emptyCol + move.1

            if newRow >= 0 && newRow < size && newCol >= 0 && newCol < size {
                let newIndex = newRow * size + newCol
                var newBoard = state.board
                newBoard.swapAt(emptyIndex, newIndex)
                neighbors.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
            }
        }
        return neighbors
    }

    private func reconstructAStarPath(from node: AStarNode) -> [PuzzleState] {
        var path: [PuzzleState] = []
        var currentNode: AStarNode? = node
        while currentNode != nil {
            path.insert(currentNode!.state, at: 0)
            currentNode = currentNode?.parent
        }
        return path
    }
}
