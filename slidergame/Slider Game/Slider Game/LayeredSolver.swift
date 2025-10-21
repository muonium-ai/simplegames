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
            currentState = solveLastTwoInRow(n: n, currentState: currentState)
            currentState = solveLastTwoInColumn(n: n, currentState: currentState)
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
        var state = currentState
        var tileIndex = state.index(of: tile)!

        while tileIndex != targetIndex {
            // Determine where the empty tile needs to go. It needs to move to the spot
            // that the tile we are solving for will occupy next.
            let tileCoords = state.coordinates(of: tileIndex)
            let targetCoords = state.coordinates(of: targetIndex)

            var emptyTargetRow = tileCoords.row
            var emptyTargetCol = tileCoords.col

            if tileCoords.row < targetCoords.row {
                emptyTargetRow += 1
            } else if tileCoords.row > targetCoords.row {
                emptyTargetRow -= 1
            } else if tileCoords.col < targetCoords.col {
                emptyTargetCol += 1
            } else if tileCoords.col > targetCoords.col {
                emptyTargetCol -= 1
            }
            
            let emptyTargetIndex = emptyTargetRow * state.size + emptyTargetCol

            // Move the empty tile to the calculated target position.
            // We must temporarily allow movement into the tile's own spot.
            var tempSolved = solvedIndices
            tempSolved.remove(tileIndex)
            state = moveEmptyTo(target: emptyTargetIndex, currentState: state, restricted: tempSolved)

            // Now that the empty tile is adjacent, swap it with our tile.
            tileIndex = state.index(of: tile)! // The tile's index might have changed
            state.board.swapAt(tileIndex, state.emptyTileIndex)
            
            // Update the state
            let oldEmptyIndex = state.emptyTileIndex
            state.emptyTileIndex = tileIndex
            tileIndex = oldEmptyIndex
            path.append(state)
        }
        return state
    }
    
    private func solveLastTwoInRow(n: Int, currentState: PuzzleState) -> PuzzleState {
        let size = currentState.size
        let row = size - n
        
        let tile1_val = row * size + n - 1
        let tile2_val = row * size + n
        
        let target1_idx = row * size + n - 2
        let target2_idx = row * size + n - 1
        
        let preTarget1_idx = (row + 1) * size + n - 2

        var state = currentState
        
        // Move tile1 to its pre-target position (just below its final spot)
        state = solveTile(tile1_val, targetIndex: preTarget1_idx, currentState: state)
        solvedIndices.insert(preTarget1_idx) // Block this spot

        // Move tile2 to tile1's final position
        state = solveTile(tile2_val, targetIndex: target1_idx, currentState: state)
        solvedIndices.insert(target1_idx)

        // Move empty tile to tile2's final position to setup rotation
        state = moveEmptyTo(target: target2_idx, currentState: state, restricted: solvedIndices)
        solvedIndices.remove(preTarget1_idx) // Unblock
        solvedIndices.remove(target1_idx)

        // Perform the 3-move rotation to place tile1 and tile2
        let finalMoveSequence = [
            target1_idx,
            (row + 1) * size + n - 1,
            preTarget1_idx
        ]
        
        for move_idx in finalMoveSequence {
            state = moveEmptyTo(target: move_idx, currentState: state, restricted: solvedIndices)
        }
        
        solvedIndices.insert(target1_idx)
        solvedIndices.insert(target2_idx)
        
        return state
    }

    private func solveLastTwoInColumn(n: Int, currentState: PuzzleState) -> PuzzleState {
        let size = currentState.size
        let col = size - n

        let tile1_val = (n - 2 + col) * size + col + 1
        let tile2_val = (n - 1 + col) * size + col + 1

        let target1_idx = (n - 2 + col) * size + col
        let target2_idx = (n - 1 + col) * size + col
        
        let preTarget1_idx = (n - 2 + col) * size + col + 1

        var state = currentState

        // Move tile1 to its pre-target position (to the right of its final spot)
        state = solveTile(tile1_val, targetIndex: preTarget1_idx, currentState: state)
        solvedIndices.insert(preTarget1_idx)

        // Move tile2 to tile1's final position
        state = solveTile(tile2_val, targetIndex: target1_idx, currentState: state)
        solvedIndices.insert(target1_idx)

        // Move empty tile to tile2's final position
        state = moveEmptyTo(target: target2_idx, currentState: state, restricted: solvedIndices)
        solvedIndices.remove(preTarget1_idx)
        solvedIndices.remove(target1_idx)
        
        // Perform the 3-move rotation
        let finalMoveSequence = [
            target1_idx,
            (n - 1 + col) * size + col + 1,
            preTarget1_idx
        ]

        for move_idx in finalMoveSequence {
            state = moveEmptyTo(target: move_idx, currentState: state, restricted: solvedIndices)
        }

        solvedIndices.insert(target1_idx)
        solvedIndices.insert(target2_idx)

        return state
    }

    private func moveEmptyTo(target: Int, currentState: PuzzleState, restricted: Set<Int>) -> PuzzleState {
        var state = currentState
        if state.emptyTileIndex == target { return state }

        var openSet = PriorityQueue<SolverNode>()
        var closedSet = Set<[Int]>()

        // We use a "greedy" search here, where the heuristic is the Manhattan distance of the empty tile to the target.
        let h: (PuzzleState) -> Int = { s in
            let emptyCoords = s.coordinates(of: s.emptyTileIndex)
            let targetCoords = s.coordinates(of: target)
            return abs(emptyCoords.row - targetCoords.row) + abs(emptyCoords.col - targetCoords.col)
        }

        let startNode = SolverNode(state: currentState, parent: nil, g: 0, strategy: .greedy, heuristic: h)
        openSet.enqueue(startNode)
        closedSet.insert(currentState.board)

        while let currentNode = openSet.dequeue() {
            if currentNode.state.emptyTileIndex == target {
                let subPath = reconstructPath(from: currentNode)
                path.append(contentsOf: subPath.dropFirst())
                return subPath.last!
            }

            let neighbors = generateNeighbors(for: currentNode.state, restrictedIndices: restricted)
            for neighborState in neighbors {
                if !closedSet.contains(neighborState.board) {
                    closedSet.insert(neighborState.board)
                    let neighborNode = SolverNode(state: neighborState, parent: currentNode, g: currentNode.g + 1, strategy: .greedy, heuristic: h)
                    openSet.enqueue(neighborNode)
                }
            }
        }
        return state // Should not happen
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
