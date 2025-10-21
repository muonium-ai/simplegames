import Foundation

struct PriorityQueue<T: Comparable> {
    private var heap: [T] = []

    var isEmpty: Bool {
        heap.isEmpty
    }

    mutating func enqueue(_ element: T) {
        heap.append(element)
        siftUp(from: heap.count - 1)
    }

    mutating func dequeue() -> T? {
        guard !heap.isEmpty else { return nil }
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

struct PuzzleState: Hashable {
    let board: [Int]
    let size: Int
    let emptyTileIndex: Int

    func isGoal() -> Bool {
        let lastIndex = board.count - 1
        for index in 0..<lastIndex {
            if board[index] != index + 1 {
                return false
            }
        }
        return board[lastIndex] == 0
    }

    func manhattanDistance() -> Int {
        var distance = 0
        for (index, value) in board.enumerated() where value != 0 {
            let goalIndex = value - 1
            let goalRow = goalIndex / size
            let goalCol = goalIndex % size
            let currentRow = index / size
            let currentCol = index % size
            distance += abs(goalRow - currentRow) + abs(goalCol - currentCol)
        }
        return distance
    }

    func isSolvable() -> Bool {
        let inversions = inversionCount()
        if size % 2 == 1 {
            return inversions % 2 == 0
        }

        let blankRowFromBottom = size - (emptyTileIndex / size)
        if blankRowFromBottom % 2 == 0 {
            return inversions % 2 == 1
        } else {
            return inversions % 2 == 0
        }
    }

    private func inversionCount() -> Int {
        var count = 0
        let flat = board.filter { $0 != 0 }
        for i in 0..<flat.count {
            for j in (i + 1)..<flat.count where flat[i] > flat[j] {
                count += 1
            }
        }
        return count
    }
}

private final class AStarNode: Comparable {
    let state: PuzzleState
    let parent: AStarNode?
    let g: Int
    let h: Int

    var f: Int { g + h }

    init(state: PuzzleState, parent: AStarNode?, g: Int) {
        self.state = state
        self.parent = parent
        self.g = g
        self.h = state.manhattanDistance()
    }

    static func < (lhs: AStarNode, rhs: AStarNode) -> Bool {
        lhs.f < rhs.f
    }

    static func == (lhs: AStarNode, rhs: AStarNode) -> Bool {
        lhs.state == rhs.state
    }
}

final class PuzzleSolver {

    func solve(initialState: PuzzleState) -> [PuzzleState]? {
        guard initialState.isSolvable() else { return nil }
        if initialState.isGoal() { return [initialState] }

        if initialState.size <= 3 {
            return solveAStar(initialState: initialState)
        }
        let constructive = ConstructiveSolver(initialState: initialState)
        return constructive.solve()
    }

    private func solveAStar(initialState: PuzzleState) -> [PuzzleState]? {
        var open = PriorityQueue<AStarNode>()
        var closed: Set<PuzzleState> = []

        let start = AStarNode(state: initialState, parent: nil, g: 0)
        open.enqueue(start)

        while let current = open.dequeue() {
            if current.state.isGoal() {
                return reconstructPath(from: current)
            }
            closed.insert(current.state)

            for neighbor in generateNeighbors(for: current.state) where !closed.contains(neighbor) {
                let node = AStarNode(state: neighbor, parent: current, g: current.g + 1)
                open.enqueue(node)
            }
        }
        return nil
    }

    private func generateNeighbors(for state: PuzzleState) -> [PuzzleState] {
        let size = state.size
        let empty = state.emptyTileIndex
        let row = empty / size
        let col = empty % size
        var result: [PuzzleState] = []

        let offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for (dr, dc) in offsets {
            let newRow = row + dr
            let newCol = col + dc
            guard newRow >= 0, newRow < size, newCol >= 0, newCol < size else { continue }
            let newIndex = newRow * size + newCol
            var newBoard = state.board
            newBoard.swapAt(empty, newIndex)
            result.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
        }
        return result
    }

    private func reconstructPath(from node: AStarNode) -> [PuzzleState] {
        var path: [PuzzleState] = []
        var cursor: AStarNode? = node
        while let current = cursor {
            path.insert(current.state, at: 0)
            cursor = current.parent
        }
        return path
    }
}

private final class LegacyConstructiveSolver {

    private struct Board {
        var tiles: [Int]
        let size: Int
        var emptyIndex: Int

        mutating func swapEmpty(with index: Int) {
            tiles.swapAt(emptyIndex, index)
            emptyIndex = index
        }

        func isSolved() -> Bool {
            let lastIndex = tiles.count - 1
            for index in 0..<lastIndex {
                if tiles[index] != index + 1 {
                    return false
                }
            }
            return tiles[lastIndex] == 0
        }

        func toPuzzleState() -> PuzzleState {
            PuzzleState(board: tiles, size: size, emptyTileIndex: emptyIndex)
        }

        func index(forRow row: Int, col: Int) -> Int {
            row * size + col
        }

        func neighbors(of index: Int) -> [Int] {
            let row = index / size
            let col = index % size
            var result: [Int] = []
            if row > 0 { result.append(index - size) }
            if row < size - 1 { result.append(index + size) }
            if col > 0 { result.append(index - 1) }
            if col < size - 1 { result.append(index + 1) }
            return result
        }

        func goalValue(for index: Int) -> Int {
            index == tiles.count - 1 ? 0 : index + 1
        }
    }

    private struct TileMoveState: Hashable {
        let tileIndex: Int
        let emptyIndex: Int
    }

    private struct RowPairState: Hashable {
        var tiles: [Int]
        var emptyPos: Int
    }

    private struct BlockState: Hashable {
        var tiles: [Int]
        var emptyPosition: Int
    }

    private var board: Board
    private var locked: Set<Int> = []
    private var states: [PuzzleState] = []

    init(initialState: PuzzleState) {
        board = Board(tiles: initialState.board, size: initialState.size, emptyIndex: initialState.emptyTileIndex)
    }

    func solve() -> [PuzzleState]? {
        states = [board.toPuzzleState()]
        guard constructSolution() else { return nil }
        return board.isSolved() ? states : nil
    }

    private func constructSolution() -> Bool {
        let size = board.size
        guard size >= 3 else { return board.isSolved() }

        for row in 0..<(size - 2) {
            for col in 0..<(size - 2) {
                let value = row * size + col + 1
                guard placeTile(value: value, row: row, col: col) else { return false }
            }

            guard placeRowPair(row: row) else { return false }
        }

        for col in 0..<(size - 2) {
            guard placeColumnPair(col: col) else { return false }
        }

        return solveFinalBlock()
    }

    private func placeTile(value: Int, row: Int, col: Int) -> Bool {
        let targetIndex = board.index(forRow: row, col: col)
        if board.tiles[targetIndex] == value {
            locked.insert(targetIndex)
            return true
        }

        guard let path = planPathForTile(value: value, targetIndex: targetIndex) else {
            print("ConstructiveSolver: failed to route tile \(value) to position \(row),\(col)")
            print("  board: \(board.tiles)")
            print("  locked: \(Array(locked).sorted()) empty: \(board.emptyIndex)")
            return false
        }
        applyBlankPath(path)
        guard board.tiles[targetIndex] == value else { return false }
        locked.insert(targetIndex)
        return true
    }

    private func routeTile(value: Int, targetIndex: Int) -> Bool {
        if board.tiles[targetIndex] == value {
            return true
        }

        guard let path = planPathForTile(value: value, targetIndex: targetIndex) else {
            print("ConstructiveSolver: failed to stage tile \(value) to index \(targetIndex)")
            print("  board: \(board.tiles)")
            print("  locked: \(Array(locked).sorted()) empty: \(board.emptyIndex)")
            return false
        }
        applyBlankPath(path)
        return board.tiles[targetIndex] == value
    }

    private func planPathForTile(value: Int, targetIndex: Int) -> [Int]? {
        guard let startTileIndex = board.tiles.firstIndex(of: value) else { return nil }
        let startState = TileMoveState(tileIndex: startTileIndex, emptyIndex: board.emptyIndex)

        if startState.tileIndex == targetIndex {
            return []
        }

        var queue: [TileMoveState] = [startState]
        var parents: [TileMoveState: (TileMoveState, Int)] = [:]
        var visited: Set<TileMoveState> = [startState]
        var cursor = 0

        while cursor < queue.count {
            let state = queue[cursor]
            cursor += 1

            if state.tileIndex == targetIndex {
                return reconstructTilePath(from: state, parents: parents)
            }

            for neighbor in board.neighbors(of: state.emptyIndex) {
                if locked.contains(neighbor) && neighbor != state.tileIndex && neighbor != targetIndex {
                    continue
                }

                var nextTileIndex = state.tileIndex
                if neighbor == state.tileIndex {
                    nextTileIndex = state.emptyIndex
                }

                let nextState = TileMoveState(tileIndex: nextTileIndex, emptyIndex: neighbor)
                if visited.insert(nextState).inserted {
                    parents[nextState] = (state, neighbor)
                    queue.append(nextState)
                }
            }
        }
        return nil
    }

    private func placeRowPair(row: Int) -> Bool {
        let size = board.size
        var regionIndices: [Int] = []
        regionIndices.reserveCapacity((size - row) * 2)
        for r in row..<size {
            regionIndices.append(board.index(forRow: r, col: size - 2))
            regionIndices.append(board.index(forRow: r, col: size - 1))
        }

        let leftGoalIndex = regionIndices[0]
        let rightGoalIndex = regionIndices[1]
        let leftGoalValue = board.goalValue(for: leftGoalIndex)
        let rightGoalValue = board.goalValue(for: rightGoalIndex)

        if !regionIndices.contains(where: { board.tiles[$0] == leftGoalValue }) {
            let stagingIndex = board.index(forRow: row + 1, col: size - 2)
            guard routeTile(value: leftGoalValue, targetIndex: stagingIndex) else { return false }
        }

        if !regionIndices.contains(where: { board.tiles[$0] == rightGoalValue }) {
            let stagingIndex = board.index(forRow: row + 1, col: size - 1)
            guard routeTile(value: rightGoalValue, targetIndex: stagingIndex) else { return false }
        }

        if !regionIndices.contains(board.emptyIndex) {
            guard let blankPath = findBlankPath(to: regionIndices.last!, forbidden: locked) else {
                print("ConstructiveSolver: failed to enter row pair region for row \(row)")
                return false
            }
            applyBlankPath(blankPath)
        }

        guard let path = solveRowPair(regionIndices: regionIndices) else {
            print("ConstructiveSolver: failed to solve row pair for row \(row)")
            print("  region: \(regionIndices)")
            print("  board: \(board.tiles)")
            return false
        }
        applyBlankPath(path)

        let leftIndex = leftGoalIndex
        let rightIndex = rightGoalIndex
        if board.tiles[leftIndex] != leftGoalValue || board.tiles[rightIndex] != rightGoalValue {
            print("ConstructiveSolver: row pair placement did not lock row \(row)")
            return false
        }

        locked.insert(leftIndex)
        locked.insert(rightIndex)
        return true
    }

    private func placeColumnPair(col: Int) -> Bool {
        let size = board.size
        var regionIndices: [Int] = []
        regionIndices.reserveCapacity((size - col) * 2)
        for c in col..<size {
            regionIndices.append(board.index(forRow: size - 2, col: c))
            regionIndices.append(board.index(forRow: size - 1, col: c))
        }

        let topGoalIndex = regionIndices[0]
        let bottomGoalIndex = regionIndices[1]
        let topGoalValue = board.goalValue(for: topGoalIndex)
        let bottomGoalValue = board.goalValue(for: bottomGoalIndex)

        if !regionIndices.contains(where: { board.tiles[$0] == topGoalValue }) && col + 1 < size {
            let stagingIndex = board.index(forRow: size - 2, col: col + 1)
            guard routeTile(value: topGoalValue, targetIndex: stagingIndex) else { return false }
        }

        if !regionIndices.contains(where: { board.tiles[$0] == bottomGoalValue }) && col + 1 < size {
            let stagingIndex = board.index(forRow: size - 1, col: col + 1)
            guard routeTile(value: bottomGoalValue, targetIndex: stagingIndex) else { return false }
        }

        if !regionIndices.contains(board.emptyIndex) {
            guard let blankPath = findBlankPath(to: regionIndices.last!, forbidden: locked) else {
                print("ConstructiveSolver: failed to enter column pair region for col \(col)")
                return false
            }
            applyBlankPath(blankPath)
        }

        guard let path = solveColumnPair(regionIndices: regionIndices) else {
            print("ConstructiveSolver: failed to solve column pair for col \(col)")
            print("  region: \(regionIndices)")
            print("  board: \(board.tiles)")
            return false
        }
        applyBlankPath(path)

        if board.tiles[topGoalIndex] != topGoalValue || board.tiles[bottomGoalIndex] != bottomGoalValue {
            print("ConstructiveSolver: column pair placement did not lock col \(col)")
            return false
        }

        locked.insert(topGoalIndex)
        locked.insert(bottomGoalIndex)
        return true
    }

    private func solveRowPair(regionIndices: [Int]) -> [Int]? {
        var tiles: [Int] = []
        tiles.reserveCapacity(regionIndices.count)
        for index in regionIndices {
            tiles.append(board.tiles[index])
        }
        guard let emptyPos = regionIndices.firstIndex(of: board.emptyIndex) else { return nil }

        let goalLeft = board.goalValue(for: regionIndices[0])
        let goalRight = board.goalValue(for: regionIndices[1])

        if tiles[0] == goalLeft && tiles[1] == goalRight {
            return []
        }

        let startState = RowPairState(tiles: tiles, emptyPos: emptyPos)

        var indexToRegion: [Int: Int] = [:]
        for (regionPos, index) in regionIndices.enumerated() {
            indexToRegion[index] = regionPos
        }

        let adjacency: [[Int]] = regionIndices.map { index in
            board.neighbors(of: index).compactMap { neighbor in
                indexToRegion[neighbor]
            }
        }

        var queue: [RowPairState] = [startState]
        var parents: [RowPairState: (RowPairState, Int)] = [:]
        var visited: Set<RowPairState> = [startState]
        var cursor = 0

        while cursor < queue.count {
            let state = queue[cursor]
            cursor += 1

            if state.tiles[0] == goalLeft && state.tiles[1] == goalRight {
                return reconstructRowPairPath(finalState: state, parents: parents)
            }

            let emptyPos = state.emptyPos
            for neighborPos in adjacency[emptyPos] {
                var nextTiles = state.tiles
                nextTiles.swapAt(emptyPos, neighborPos)
                let nextState = RowPairState(tiles: nextTiles, emptyPos: neighborPos)
                if visited.insert(nextState).inserted {
                    parents[nextState] = (state, regionIndices[neighborPos])
                    queue.append(nextState)
                }
            }
        }

        print("ConstructiveSolver: row pair BFS exhausted. tiles=\(tiles) goalLeft=\(goalLeft) goalRight=\(goalRight)")
        return nil
    }

    private func solveColumnPair(regionIndices: [Int]) -> [Int]? {
        var tiles: [Int] = []
        tiles.reserveCapacity(regionIndices.count)
        for index in regionIndices {
            tiles.append(board.tiles[index])
        }
        guard let emptyPos = regionIndices.firstIndex(of: board.emptyIndex) else { return nil }

        let goalTop = board.goalValue(for: regionIndices[0])
        let goalBottom = board.goalValue(for: regionIndices[1])

        if tiles[0] == goalTop && tiles[1] == goalBottom {
            return []
        }

        let startState = RowPairState(tiles: tiles, emptyPos: emptyPos)

        var indexToRegion: [Int: Int] = [:]
        for (regionPos, index) in regionIndices.enumerated() {
            indexToRegion[index] = regionPos
        }

        let adjacency: [[Int]] = regionIndices.map { index in
            board.neighbors(of: index).compactMap { neighbor in
                indexToRegion[neighbor]
            }
        }

        var queue: [RowPairState] = [startState]
        var parents: [RowPairState: (RowPairState, Int)] = [:]
        var visited: Set<RowPairState> = [startState]
        var cursor = 0

        while cursor < queue.count {
            let state = queue[cursor]
            cursor += 1

            if state.tiles[0] == goalTop && state.tiles[1] == goalBottom {
                return reconstructRowPairPath(finalState: state, parents: parents)
            }

            let emptyPos = state.emptyPos
            for neighborPos in adjacency[emptyPos] {
                var nextTiles = state.tiles
                nextTiles.swapAt(emptyPos, neighborPos)
                let nextState = RowPairState(tiles: nextTiles, emptyPos: neighborPos)
                if visited.insert(nextState).inserted {
                    parents[nextState] = (state, regionIndices[neighborPos])
                    queue.append(nextState)
                }
            }
        }

        print("ConstructiveSolver: column pair BFS exhausted. tiles=\(tiles) goalTop=\(goalTop) goalBottom=\(goalBottom)")
        return nil
    }

    private func reconstructRowPairPath(finalState: RowPairState, parents: [RowPairState: (RowPairState, Int)]) -> [Int] {
        var moves: [Int] = []
        var state = finalState
        while let record = parents[state] {
            moves.append(record.1)
            state = record.0
        }
        return moves.reversed()
    }

    private func reconstructTilePath(from state: TileMoveState, parents: [TileMoveState: (TileMoveState, Int)]) -> [Int] {
        var moves: [Int] = []
        var current = state
        while let record = parents[current] {
            moves.append(record.1)
            current = record.0
        }
        return moves.reversed()
    }

    private func applyBlankPath(_ path: [Int]) {
        for destination in path {
            board.swapEmpty(with: destination)
            states.append(board.toPuzzleState())
        }
    }

    private func solveFinalBlock() -> Bool {
        let size = board.size
        let indices = [
            board.index(forRow: size - 2, col: size - 2),
            board.index(forRow: size - 2, col: size - 1),
            board.index(forRow: size - 1, col: size - 2),
            board.index(forRow: size - 1, col: size - 1)
        ]

        if !indices.contains(board.emptyIndex) {
            guard let path = findBlankPath(to: indices.last!, forbidden: locked) else {
                print("ConstructiveSolver: failed to bring blank into final block")
                return false
            }
            applyBlankPath(path)
        }

        guard let sequence = solveBlock(indices: indices) else {
            print("ConstructiveSolver: failed to solve final 2x2 block")
            return false
        }
        applyBlankPath(sequence)
        return true
    }

    private func findBlankPath(to target: Int, forbidden: Set<Int>) -> [Int]? {
        let start = board.emptyIndex
        if start == target { return [] }

        var queue: [Int] = [start]
        var parents: [Int: Int] = [:]
        var visited: Set<Int> = [start]
        var cursor = 0

        while cursor < queue.count {
            let current = queue[cursor]
            cursor += 1

            for neighbor in board.neighbors(of: current) where !forbidden.contains(neighbor) {
                if visited.insert(neighbor).inserted {
                    parents[neighbor] = current
                    if neighbor == target {
                        var path: [Int] = []
                        var node = neighbor
                        while node != start {
                            path.append(node)
                            guard let parent = parents[node] else { break }
                            node = parent
                        }
                        return path.reversed()
                    }
                    queue.append(neighbor)
                }
            }
        }
        return nil
    }

    private func solveBlock(indices: [Int]) -> [Int]? {
        var startTiles: [Int] = []
        startTiles.reserveCapacity(indices.count)
        for index in indices {
            startTiles.append(board.tiles[index])
        }
        guard let startEmpty = indices.firstIndex(of: board.emptyIndex) else { return nil }
        let startState = BlockState(tiles: startTiles, emptyPosition: startEmpty)

        var goalTiles: [Int] = []
        goalTiles.reserveCapacity(indices.count)
        for index in indices {
            goalTiles.append(board.goalValue(for: index))
        }
        guard let goalEmpty = goalTiles.firstIndex(of: 0) else { return nil }
        let goalState = BlockState(tiles: goalTiles, emptyPosition: goalEmpty)

        if startState == goalState { return [] }

        let adjacency: [[Int]] = indices.map { index in
            board.neighbors(of: index).compactMap { neighbor in
                indices.firstIndex(of: neighbor)
            }
        }

        var queue: [BlockState] = [startState]
        var parents: [BlockState: (BlockState, Int)] = [:]
        var visited: Set<BlockState> = [startState]
        var cursor = 0

        while cursor < queue.count {
            let state = queue[cursor]
            cursor += 1

            if state == goalState {
                return reconstructBlockPath(from: state, parents: parents)
            }

            let empty = state.emptyPosition
            for neighbor in adjacency[empty] {
                var nextTiles = state.tiles
                nextTiles.swapAt(empty, neighbor)
                let nextState = BlockState(tiles: nextTiles, emptyPosition: neighbor)
                if visited.insert(nextState).inserted {
                    parents[nextState] = (state, indices[neighbor])
                    queue.append(nextState)
                }
            }
        }
        return nil
    }

    private func reconstructBlockPath(from state: BlockState, parents: [BlockState: (BlockState, Int)]) -> [Int] {
        var moves: [Int] = []
        var current = state
        while let record = parents[current] {
            moves.append(record.1)
            current = record.0
        }
        return moves.reversed()
    }
}

    private final class ConstructiveSolver {

        private struct Board {
            var tiles: [Int]
            let size: Int
            var emptyIndex: Int

            mutating func swapEmpty(with index: Int) {
                tiles.swapAt(emptyIndex, index)
                emptyIndex = index
            }

            func toPuzzleState() -> PuzzleState {
                PuzzleState(board: tiles, size: size, emptyTileIndex: emptyIndex)
            }

            func index(forRow row: Int, col: Int) -> Int {
                row * size + col
            }

            func neighbors(of index: Int) -> [Int] {
                let row = index / size
                let col = index % size
                var result: [Int] = []
                if row > 0 { result.append(index - size) }
                if row < size - 1 { result.append(index + size) }
                if col > 0 { result.append(index - 1) }
                if col < size - 1 { result.append(index + 1) }
                return result
            }

            func goalValue(for index: Int) -> Int {
                index == tiles.count - 1 ? 0 : index + 1
            }

            func isSolved() -> Bool {
                let last = tiles.count - 1
                for i in 0..<last where tiles[i] != i + 1 {
                    return false
                }
                return tiles[last] == 0
            }
        }

        private struct TileMoveState: Hashable {
            let tileIndex: Int
            let emptyIndex: Int
        }

        private let initialState: PuzzleState
        private var board: Board
        private var states: [PuzzleState] = []
        private var locked: Set<Int> = []
        private let columnOrder: [(Int, Int)]
        private let rowOrder: [(Int, Int)]

        init(initialState: PuzzleState) {
            self.initialState = initialState
            board = Board(tiles: initialState.board, size: initialState.size, emptyIndex: initialState.emptyTileIndex)
            columnOrder = ConstructiveSolver.buildColumnTraversal(size: initialState.size)
            rowOrder = ConstructiveSolver.buildRowTraversal(size: initialState.size)
        }

        func solve() -> [PuzzleState]? {
            board = Board(tiles: initialState.board, size: initialState.size, emptyIndex: initialState.emptyTileIndex)
            states = [initialState]

            if constructSolution(), board.isSolved() {
                return states
            }

            let partialState = board.toPuzzleState()
            if let tail = LegacyConstructiveSolver(initialState: partialState).solve() {
                appendStates(from: tail)
                if board.isSolved() {
                    return states
                }
            }

            return LegacyConstructiveSolver(initialState: initialState).solve()
        }

        private func constructSolution() -> Bool {
            if board.isSolved() { return true }

            let maxIterations = max(8, board.size * 6)
            for _ in 0..<maxIterations {
                if board.isSolved() { return true }
                let columnProgress = performPass(order: columnOrder)
                if board.isSolved() { return true }
                let rowProgress = performPass(order: rowOrder)
                if board.isSolved() { return true }
                if !columnProgress && !rowProgress { break }
            }

            if board.isSolved() { return true }
            if board.size <= 4 {
                return finishWithAStar()
            }
            return false
        }

        private func performPass(order: [(Int, Int)]) -> Bool {
            var madeProgress = false
            var progress = true

            while progress {
                progress = false
                locked.removeAll()

                for (row, col) in order {
                    let targetIndex = board.index(forRow: row, col: col)
                    let goalValue = board.goalValue(for: targetIndex)
                    if goalValue == 0 { continue }

                    if ensureTile(value: goalValue, row: row, col: col) {
                        progress = true
                        madeProgress = true
                    }
                }
            }

            locked.removeAll()
            return madeProgress
        }

        private func ensureTile(value: Int, row: Int, col: Int) -> Bool {
            let targetIndex = board.index(forRow: row, col: col)
            if board.tiles[targetIndex] == value {
                locked.insert(targetIndex)
                return false
            }

            guard let path = planPathForTile(value: value, targetIndex: targetIndex) else {
                return false
            }

            applyBlankPath(path)
            locked.insert(targetIndex)
            return true
        }

        private func planPathForTile(value: Int, targetIndex: Int) -> [Int]? {
            guard let startTileIndex = board.tiles.firstIndex(of: value) else { return nil }
            let startState = TileMoveState(tileIndex: startTileIndex, emptyIndex: board.emptyIndex)

            if startState.tileIndex == targetIndex {
                return []
            }

            var queue: [TileMoveState] = [startState]
            var parents: [TileMoveState: (TileMoveState, Int)] = [:]
            var visited: Set<TileMoveState> = [startState]
            var cursor = 0

            while cursor < queue.count {
                let state = queue[cursor]
                cursor += 1

                if state.tileIndex == targetIndex {
                    return reconstructTilePath(from: state, parents: parents)
                }

                for neighbor in board.neighbors(of: state.emptyIndex) {
                    if locked.contains(neighbor) && neighbor != state.tileIndex && neighbor != targetIndex {
                        continue
                    }

                    var nextTileIndex = state.tileIndex
                    if neighbor == state.tileIndex {
                        nextTileIndex = state.emptyIndex
                    }

                    let nextState = TileMoveState(tileIndex: nextTileIndex, emptyIndex: neighbor)
                    if visited.insert(nextState).inserted {
                        parents[nextState] = (state, neighbor)
                        queue.append(nextState)
                    }
                }
            }

            return nil
        }

        private func reconstructTilePath(from state: TileMoveState, parents: [TileMoveState: (TileMoveState, Int)]) -> [Int] {
            var moves: [Int] = []
            var current = state
            while let record = parents[current] {
                moves.append(record.1)
                current = record.0
            }
            return moves.reversed()
        }

        private func applyBlankPath(_ path: [Int]) {
            for destination in path {
                board.swapEmpty(with: destination)
                states.append(board.toPuzzleState())
            }
        }

        private func finishWithAStar() -> Bool {
            var open = PriorityQueue<AStarNode>()
            var closed: Set<PuzzleState> = []

            let startNode = AStarNode(state: board.toPuzzleState(), parent: nil, g: 0)
            open.enqueue(startNode)

            while let current = open.dequeue() {
                if current.state.isGoal() {
                    let path = reconstructAStarPath(from: current)
                    appendStates(from: path)
                    return true
                }

                if !closed.insert(current.state).inserted {
                    continue
                }

                for neighbor in generateNeighbors(for: current.state) {
                    if closed.contains(neighbor) { continue }
                    open.enqueue(AStarNode(state: neighbor, parent: current, g: current.g + 1))
                }
            }

            return false
        }

        private func generateNeighbors(for state: PuzzleState) -> [PuzzleState] {
            let size = state.size
            let empty = state.emptyTileIndex
            let row = empty / size
            let col = empty % size
            var result: [PuzzleState] = []

            if row > 0 {
                let newIndex = empty - size
                var newBoard = state.board
                newBoard.swapAt(empty, newIndex)
                result.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
            }
            if row < size - 1 {
                let newIndex = empty + size
                var newBoard = state.board
                newBoard.swapAt(empty, newIndex)
                result.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
            }
            if col > 0 {
                let newIndex = empty - 1
                var newBoard = state.board
                newBoard.swapAt(empty, newIndex)
                result.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
            }
            if col < size - 1 {
                let newIndex = empty + 1
                var newBoard = state.board
                newBoard.swapAt(empty, newIndex)
                result.append(PuzzleState(board: newBoard, size: size, emptyTileIndex: newIndex))
            }

            return result
        }

        private func reconstructAStarPath(from node: AStarNode) -> [PuzzleState] {
            var path: [PuzzleState] = []
            var cursor: AStarNode? = node
            while let current = cursor {
                path.insert(current.state, at: 0)
                cursor = current.parent
            }
            return path
        }

        private func appendStates(from path: [PuzzleState]) {
            guard path.count > 1 else { return }
            for state in path.dropFirst() {
                board.tiles = state.board
                board.emptyIndex = state.emptyTileIndex
                states.append(state)
            }
        }

        private static func buildColumnTraversal(size: Int) -> [(Int, Int)] {
            var order: [(Int, Int)] = []
            order.reserveCapacity(size * size)
            for col in 0..<size {
                for row in 0..<size {
                    if row == size - 1 && col == size - 1 { continue }
                    order.append((row, col))
                }
            }
            return order
        }

        private static func buildRowTraversal(size: Int) -> [(Int, Int)] {
            var order: [(Int, Int)] = []
            order.reserveCapacity(size * size)
            for row in 0..<size {
                for col in 0..<size {
                    if row == size - 1 && col == size - 1 { continue }
                    order.append((row, col))
                }
            }
            return order
        }
    }
