import Foundation

// A class to solve the puzzle by reducing it layer by layer
class LayeredSolver {
    private var path: [PuzzleState] = []
    private var solvedIndices: Set<Int> = []

    func solve(initialState: PuzzleState) -> [PuzzleState]? {
        path.append(initialState)
        var currentState = initialState

        for n in (4...currentState.size).reversed() {
            // Solve top row of the n x n subgrid
            for j in 0..<(n - 2) {
                let tile = (n - currentState.size) * currentState.size + j + 1
                let targetIndex = (n - currentState.size) * currentState.size + j
                currentState = solveTile(tile, targetIndex: targetIndex, currentState: currentState)
                solvedIndices.insert(targetIndex)
            }
            
            // Solve left column of the n x n subgrid
            for i in 0..<(n - 2) {
                let tile = (i + (n - currentState.size) + 1) * currentState.size + (n - currentState.size) + 1
                let targetIndex = (i + (n - currentState.size)) * currentState.size + (n - currentState.size)
                currentState = solveTile(tile, targetIndex: targetIndex, currentState: currentState)
                solvedIndices.insert(targetIndex)
            }
            
            // Special handling for the last two tiles in the row/column
            // This part is complex and will be implemented next.
        }

        // Once reduced to 3x3, use the A* solver
        let aStarSolver = PuzzleSolver()
        if var finalPath = aStarSolver.solve(initialState: currentState) {
            finalPath.removeFirst() // Avoid duplicate state
            path.append(contentsOf: finalPath)
        }

        return path.isEmpty ? nil : path
    }

    private func solveTile(_ tile: Int, targetIndex: Int, currentState: PuzzleState) -> PuzzleState {
        // A* search to move the tile to the target index
        // This is a simplified A* for moving one tile.
        var openSet = PriorityQueue<SolverNode>()
        var closedSet = Set<[Int]>()

        let startNode = SolverNode(state: currentState, parent: nil, g: 0, strategy: .greedy)
        openSet.enqueue(startNode)
        closedSet.insert(currentState.board)

        while let currentNode = openSet.dequeue() {
            if currentNode.state.index(of: tile) == targetIndex {
                // Found path to move the tile
                let tilePath = reconstructPath(from: currentNode)
                path.append(contentsOf: tilePath.dropFirst())
                return tilePath.last!
            }

            let neighbors = generateNeighbors(for: currentNode.state, restrictedIndices: solvedIndices)
            for neighborState in neighbors {
                if !closedSet.contains(neighborState.board) {
                    closedSet.insert(neighborState.board)
                    let neighborNode = SolverNode(state: neighborState, parent: currentNode, g: currentNode.g + 1, strategy: .greedy)
                    openSet.enqueue(neighborNode)
                }
            }
        }
        return currentState // Should not happen in a solvable puzzle
    }
    
    private func reconstructPath(from node: SolverNode) -> [PuzzleState] {
        var subPath: [PuzzleState] = []
        var currentNode: SolverNode? = node
        while let current = currentNode {
            subPath.insert(current.state, at: 0)
            currentNode = current.parent
        }
        return subPath
    }
}
