//
//  GameScene.swift
//  super 2048
//
//  Created by Senthil Nayagam on 19/10/25.
//

import SpriteKit
import Foundation
import UIKit

enum MoveDirection: CaseIterable {
    case up, right, down, left

    var isVertical: Bool {
        return self == .up || self == .down
    }

    var isReversed: Bool {
        return self == .right || self == .down
    }

    var nodeName: String {
        switch self {
        case .up: return "arrow_up"
        case .right: return "arrow_right"
        case .down: return "arrow_down"
        case .left: return "arrow_left"
        }
    }

    static func from(nodeName: String) -> MoveDirection? {
        return Self.allCases.first { $0.nodeName == nodeName }
    }
}

private enum GameStatus {
    case inProgress
    case won
    case lost
}

private struct SeededGenerator: RandomNumberGenerator {
    private var state: UInt64

    init(seed: UInt64) {
        state = seed == 0 ? 0x9E3779B97F4A7C15 : seed
    }

    mutating func next() -> UInt64 {
        state &+= 0x9E3779B97F4A7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
        z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
        return z ^ (z >> 31)
    }
}

private struct HighScoreEntry: Codable {
    let date: Date
    let score: Int
    let maxTile: Int
    let moves: Int
    let seed: UInt64
    let mode: String
}

private final class HighScoreStore {
    static let shared = HighScoreStore()

    private let storageKey = "super2048.highscores"
    private var cache: [HighScoreEntry] = []

    private init() {
        load()
    }

    var entries: [HighScoreEntry] {
        return cache
    }

    func add(_ entry: HighScoreEntry) {
        cache.append(entry)
        cache.sort { $0.score > $1.score }
        if cache.count > 25 {
            cache = Array(cache.prefix(25))
        }
        save()
    }

    private func load() {
        guard let data = UserDefaults.standard.data(forKey: storageKey) else { return }
        if let decoded = try? JSONDecoder().decode([HighScoreEntry].self, from: data) {
            cache = decoded
        }
    }

    private func save() {
        if let data = try? JSONEncoder().encode(cache) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }
}

private struct GameBoard {
    static let size = 4

    var grid: [[Int]]
    var score: Int
    var moves: Int
    var maxTile: Int
    var status: GameStatus
    var lastSpawnPosition: (row: Int, col: Int)?
    var lastScoreGain: Int

    private var milestones: [Int: Bool]
    private var recentMilestone: Int?
    private var rng: SeededGenerator
    private(set) var seed: UInt64

    init(seed: UInt64) {
        self.seed = seed
        rng = SeededGenerator(seed: seed)
        grid = Array(repeating: Array(repeating: 0, count: Self.size), count: Self.size)
        score = 0
        moves = 0
        maxTile = 2
        status = .inProgress
        lastSpawnPosition = nil
        lastScoreGain = 0
        milestones = [2048: false, 4096: false, 8192: false, 16384: false, 32768: false, 65536: false]
        recentMilestone = nil
        addNewTile()
        addNewTile()
        updateMaxTile()
        refreshStatus()
    }

    mutating func reset(withSeed newSeed: UInt64) {
        seed = newSeed
        rng = SeededGenerator(seed: newSeed)
        grid = Array(repeating: Array(repeating: 0, count: Self.size), count: Self.size)
        score = 0
        moves = 0
        maxTile = 2
        status = .inProgress
        lastSpawnPosition = nil
        lastScoreGain = 0
        milestones = [2048: false, 4096: false, 8192: false, 16384: false, 32768: false, 65536: false]
        recentMilestone = nil
        addNewTile()
        addNewTile()
        updateMaxTile()
        refreshStatus()
    }

    mutating func move(_ direction: MoveDirection, spawnTile: Bool = true) -> Bool {
        let (newGrid, gained, moved) = Self.apply(direction: direction, to: grid)
        guard moved else {
            lastScoreGain = 0
            return false
        }

        grid = newGrid
        score += gained
        lastScoreGain = gained
        moves += 1
        lastSpawnPosition = nil
        updateMaxTile()

        if spawnTile {
            addNewTile()
        }

        updateMaxTile()
        refreshStatus()
        return true
    }

    func availableMoves() -> [MoveDirection] {
        return MoveDirection.allCases.filter { direction in
            Self.apply(direction: direction, to: grid).moved
        }
    }

    func simulatedBoard(for direction: MoveDirection) -> GameBoard? {
        let (newGrid, gained, moved) = Self.apply(direction: direction, to: grid)
        guard moved else { return nil }
        var copy = self
        copy.grid = newGrid
        copy.score += gained
        copy.lastScoreGain = gained
        copy.moves += 1
        copy.lastSpawnPosition = nil
        copy.updateMaxTile()
        copy.refreshStatus()
        return copy
    }

    mutating func clearLastSpawn() {
        lastSpawnPosition = nil
    }

    mutating func consumeMilestone() -> Int? {
        let milestone = recentMilestone
        recentMilestone = nil
        return milestone
    }

    func emptyPositions() -> [(Int, Int)] {
        var positions: [(Int, Int)] = []
        for row in 0..<Self.size {
            for col in 0..<Self.size where grid[row][col] == 0 {
                positions.append((row, col))
            }
        }
        return positions
    }

    func emptyCount() -> Int {
        return emptyPositions().count
    }

    func monotonicityScore() -> Double {
        var score = 0.0
        for row in grid {
            for col in 0..<(Self.size - 1) {
                let current = row[col]
                let next = row[col + 1]
                guard current != 0, next != 0 else { continue }
                let currentLog = log2(Double(current))
                let nextLog = log2(Double(next))
                score += current >= next ? currentLog : -nextLog
            }
        }

        for col in 0..<Self.size {
            for row in 0..<(Self.size - 1) {
                let current = grid[row][col]
                let next = grid[row + 1][col]
                guard current != 0, next != 0 else { continue }
                let currentLog = log2(Double(current))
                let nextLog = log2(Double(next))
                score += current >= next ? currentLog : -nextLog
            }
        }
        return score
    }

    func smoothnessScore() -> Double {
        var score = 0.0
        for row in 0..<Self.size {
            for col in 0..<Self.size {
                let value = grid[row][col]
                guard value != 0 else { continue }
                let base = log2(Double(value))
                if col + 1 < Self.size {
                    let right = grid[row][col + 1]
                    if right != 0 {
                        score -= abs(base - log2(Double(right)))
                    }
                }
                if row + 1 < Self.size {
                    let down = grid[row + 1][col]
                    if down != 0 {
                        score -= abs(base - log2(Double(down)))
                    }
                }
            }
        }
        return score
    }

    func cornerAlignmentScore() -> Double {
        guard maxTile > 0, let position = positionOfMaxTile() else { return 0.0 }
        let (row, col) = position
        let isCorner = (row == 0 || row == Self.size - 1) && (col == 0 || col == Self.size - 1)
        let cornerBonus = isCorner ? 4.0 : 1.0
        let threshold = max(maxTile / 2, 2)
        let alignedRow = grid[row].filter { $0 >= threshold }.count
        let alignedCol = (0..<Self.size).map { grid[$0][col] }.filter { $0 >= threshold }.count
        let magnitude = log2(Double(maxTile))
        return cornerBonus * magnitude + Double(alignedRow + alignedCol)
    }

    private func positionOfMaxTile() -> (Int, Int)? {
        for row in 0..<Self.size {
            for col in 0..<Self.size where grid[row][col] == maxTile {
                return (row, col)
            }
        }
        return nil
    }

    private mutating func addNewTile() {
        let empty = emptyPositions()
        guard !empty.isEmpty else { return }
        let index = Int.random(in: 0..<empty.count, using: &rng)
        let (row, col) = empty[index]
        let roll = Double.random(in: 0..<1, using: &rng)
        grid[row][col] = roll < 0.9 ? 2 : 4
        lastSpawnPosition = (row, col)
    }

    mutating func updateMaxTile() {
        let previousMax = maxTile
        maxTile = grid.flatMap { $0 }.max() ?? 0
        guard maxTile > previousMax else { return }
        for milestone in milestones.keys.sorted() {
            if maxTile >= milestone && milestones[milestone] == false {
                milestones[milestone] = true
                recentMilestone = milestone
            }
        }
    }

    private mutating func refreshStatus() {
        if maxTile >= 65536 {
            status = .won
        } else if !canMove() {
            status = .lost
        } else {
            status = .inProgress
        }
    }

    private func canMove() -> Bool {
        if !emptyPositions().isEmpty {
            return true
        }
        for row in 0..<Self.size {
            for col in 0..<Self.size {
                let value = grid[row][col]
                if col + 1 < Self.size && grid[row][col + 1] == value {
                    return true
                }
                if row + 1 < Self.size && grid[row + 1][col] == value {
                    return true
                }
            }
        }
        return false
    }

    private static func apply(direction: MoveDirection, to grid: [[Int]]) -> (grid: [[Int]], score: Int, moved: Bool) {
        var working = grid
        if direction.isVertical {
            working = transpose(working)
        }
        if direction.isReversed {
            working = reverseRows(working)
        }

        compressRows(&working)
        let scored = mergeRows(&working)
        compressRows(&working)

        if direction.isReversed {
            working = reverseRows(working)
        }
        if direction.isVertical {
            working = transpose(working)
        }

        let moved = working != grid
        return (working, scored, moved)
    }

    private static func transpose(_ grid: [[Int]]) -> [[Int]] {
        var result = grid
        for i in 0..<Self.size {
            for j in 0..<Self.size {
                result[i][j] = grid[j][i]
            }
        }
        return result
    }

    private static func reverseRows(_ grid: [[Int]]) -> [[Int]] {
        return grid.map { Array($0.reversed()) }
    }

    private static func compressRows(_ grid: inout [[Int]]) {
        for row in 0..<Self.size {
            var filtered = grid[row].filter { $0 != 0 }
            if filtered.count < Self.size {
                filtered.append(contentsOf: Array(repeating: 0, count: Self.size - filtered.count))
            }
            grid[row] = filtered
        }
    }

    private static func mergeRows(_ grid: inout [[Int]]) -> Int {
        var score = 0
        for row in 0..<Self.size {
            var column = 0
            while column < Self.size - 1 {
                if grid[row][column] != 0 && grid[row][column] == grid[row][column + 1] {
                    grid[row][column] *= 2
                    score += grid[row][column]
                    grid[row][column + 1] = 0
                    column += 1
                }
                column += 1
            }
        }
        return score
    }
}

private protocol SolverStrategy {
    var name: String { get }
    func nextMove(for board: GameBoard) -> MoveDirection?
}

private struct CornerTrapSolver: SolverStrategy {
    let name = "Corner Trap"

    func nextMove(for board: GameBoard) -> MoveDirection? {
        let options = MoveDirection.allCases.compactMap { direction -> (MoveDirection, Double)? in
            guard let candidate = board.simulatedBoard(for: direction) else { return nil }
            let empties = Double(candidate.emptyCount())
            let alignment = candidate.cornerAlignmentScore()
            let monotonicity = candidate.monotonicityScore()
            let benefit = Double(candidate.score - board.score)
            let value = alignment * 2.0 + monotonicity * 1.2 + empties * 1.5 + benefit * 0.1
            return (direction, value)
        }
        return options.max(by: { $0.1 < $1.1 })?.0
    }
}

private struct SmoothnessSolver: SolverStrategy {
    let name = "Smooth Heuristic"

    func nextMove(for board: GameBoard) -> MoveDirection? {
        let options = MoveDirection.allCases.compactMap { direction -> (MoveDirection, Double)? in
            guard let candidate = board.simulatedBoard(for: direction) else { return nil }
            let smooth = candidate.smoothnessScore()
            let monotonic = candidate.monotonicityScore()
            let empties = Double(candidate.emptyCount())
            let alignment = candidate.cornerAlignmentScore()
            let value = smooth * 1.4 + monotonic * 1.6 + empties * 2.0 + alignment
            return (direction, value)
        }
        return options.max(by: { $0.1 < $1.1 })?.0
    }
}

private struct RandomSolver: SolverStrategy {
    let name = "Random"

    func nextMove(for board: GameBoard) -> MoveDirection? {
        return board.availableMoves().randomElement()
    }
}

private final class GrokSolver: SolverStrategy {
    let name = "Grok Solver"
    
    // Weight matrices
    private let cornerWeights: [[Double]] = [
        [2048, 1024, 512, 256],
        [16, 32, 64, 128],
        [8, 4, 2, 4],
        [0, 0, 0, 0]
    ]
    
    private let snakeWeights: [[Double]] = [
        [pow(2, 15), pow(2, 14), pow(2, 13), pow(2, 12)],
        [pow(2, 8), pow(2, 9), pow(2, 10), pow(2, 11)],
        [pow(2, 7), pow(2, 6), pow(2, 5), pow(2, 4)],
        [pow(2, 0), pow(2, 1), pow(2, 2), pow(2, 3)]
    ]
    
    private let baseDepth = 3
    private static var transpositionTable: [String: Double] = [:]
    private static var moveHistory: [MoveDirection: Int] = [.up: 0, .right: 0, .down: 0, .left: 0]
    
    func nextMove(for board: GameBoard) -> MoveDirection? {
        Self.pruneTranspositionTable()
        let depth = getDynamicDepth(for: board)
        var alpha = -Double.infinity
        let (_, bestMove) = expectimax(board: board, depth: depth, isMax: true, alpha: &alpha)
        
        if let move = bestMove {
            Self.moveHistory[move, default: 0] += 1
        } else {
            // Fallback: try moves sorted by history
            for direction in MoveDirection.allCases.sorted(by: { (Self.moveHistory[$0, default: 0]) > (Self.moveHistory[$1, default: 0]) }) {
                if board.simulatedBoard(for: direction) != nil {
                    Self.moveHistory[direction, default: 0] += 1
                    return direction
                }
            }
        }
        
        // Decay history
        for key in Self.moveHistory.keys {
            Self.moveHistory[key] = Int(Double(Self.moveHistory[key] ?? 0) * 0.9)
        }
        
        return bestMove ?? board.availableMoves().first
    }
    
    private func expectimax(board: GameBoard, depth: Int, isMax: Bool, alpha: inout Double) -> (Double, MoveDirection?) {
        if depth == 0 {
            return (evaluatePosition(board, remainingDepth: depth), nil)
        }
        
        if isMax {
            var maxScore = -Double.infinity
            var bestMove: MoveDirection? = nil
            
            let moves = orderMoves(for: board)
            
            for direction in moves {
                guard let newBoard = board.simulatedBoard(for: direction) else { continue }
                let (score, _) = expectimax(board: newBoard, depth: depth - 1, isMax: false, alpha: &alpha)
                if score > maxScore {
                    maxScore = score
                    bestMove = direction
                    alpha = max(alpha, score)
                }
                
                // Early cutoff for clearly worse moves
                if score < alpha / 2 {
                    continue
                }
            }
            
            return (maxScore, bestMove)
        } else {
            // Chance node for tile spawns
            let emptyPositions = board.emptyPositions()
            guard !emptyPositions.isEmpty else {
                return (evaluatePosition(board, remainingDepth: depth), nil)
            }
            
            var avgScore = 0.0
            var totalWeight = 0.0
            
            for (row, col) in emptyPositions {
                for (value, prob) in [(2, 0.9), (4, 0.1)] {
                    var newBoard = board
                    newBoard.grid[row][col] = value
                    newBoard.updateMaxTile()
                    let (score, _) = expectimax(board: newBoard, depth: depth - 1, isMax: true, alpha: &alpha)
                    avgScore += score * prob
                    totalWeight += prob
                }
            }
            
            return (avgScore / totalWeight, nil)
        }
    }
    
    private func evaluatePosition(_ board: GameBoard, remainingDepth: Int) -> Double {
        let stage = getStage(for: board)
        let cacheKey = "\(board.grid.map { $0.map { String($0) }.joined() }.joined(separator: ","))_\(remainingDepth)_\(stage)"
        
        if let cached = Self.transpositionTable[cacheKey] {
            return cached
        }
        
        let emptyCells = Double(board.emptyCount())
        let maxTile = Double(board.maxTile)
        
        let cornerScore = calculateCornerScore(board)
        let snakeScore = calculateSnakeScore(board)
        let gradientScore = calculateGradientScore(board)
        let mergeChains = calculateMergeChains(board)
        let monotonicity = calculateMonotonicity(board)
        let smoothness = calculateSmoothness(board)
        let alignment = maxCornerAlignment(board)
        
        let weights = getStageWeights(stage)
        
        let score = cornerScore * weights["corner"]! +
                   snakeScore * weights["snake"]! +
                   gradientScore * weights["gradient"]! +
                   mergeChains * weights["merge"]! +
                   emptyCells * weights["empty"]! +
                   maxTile * weights["maxTile"]! +
                   Double(remainingDepth) * weights["depth"]! +
                   monotonicity * weights["monotonicity"]! +
                   smoothness * weights["smoothness"]! +
                   alignment * weights["alignment"]!
        
        Self.transpositionTable[cacheKey] = score
        return score
    }
    
    private func getStageWeights(_ stage: String) -> [String: Double] {
        switch stage {
        case "early":
            return [
                "corner": 2.0, "snake": 1.0, "gradient": 1.5,
                "merge": 1.0, "empty": 2.5, "maxTile": 1.0,
                "depth": 0.1, "monotonicity": 1.5, "smoothness": 1.0,
                "alignment": 1.0
            ]
        case "mid":
            return [
                "corner": 2.5, "snake": 2.0, "gradient": 2.0,
                "merge": 1.5, "empty": 2.0, "maxTile": 1.5,
                "depth": 0.2, "monotonicity": 2.0, "smoothness": 1.5,
                "alignment": 1.5
            ]
        default: // late
            return [
                "corner": 3.0, "snake": 2.5, "gradient": 2.5,
                "merge": 2.0, "empty": 1.5, "maxTile": 2.0,
                "depth": 0.3, "monotonicity": 2.5, "smoothness": 2.0,
                "alignment": 2.5
            ]
        }
    }
    
    private func calculateCornerScore(_ board: GameBoard) -> Double {
        var score = 0.0
        for i in 0..<4 {
            for j in 0..<4 {
                score += Double(board.grid[i][j]) * cornerWeights[i][j]
            }
        }
        return score
    }
    
    private func calculateSnakeScore(_ board: GameBoard) -> Double {
        var score = 0.0
        for i in 0..<4 {
            for j in 0..<4 {
                score += Double(board.grid[i][j]) * snakeWeights[i][j]
            }
        }
        return score
    }
    
    private func calculateGradientScore(_ board: GameBoard) -> Double {
        var score = 0.0
        for i in 0..<3 {
            for j in 0..<3 {
                if board.grid[i][j] != 0 {
                    // Horizontal gradient
                    if board.grid[i][j] >= board.grid[i][j+1] {
                        score += log2(Double(board.grid[i][j]))
                    }
                    // Vertical gradient
                    if board.grid[i][j] >= board.grid[i+1][j] {
                        score += log2(Double(board.grid[i][j]))
                    }
                }
            }
        }
        return score
    }
    
    private func calculateMergeChains(_ board: GameBoard) -> Double {
        var score = 0.0
        
        // Horizontal chains - look for potential merge opportunities
        for i in 0..<4 {
            for j in 0..<3 {
                let current = board.grid[i][j]
                let next = board.grid[i][j + 1]
                if current != 0 && next != 0 {
                    if current == next {
                        // Immediate merge opportunity
                        score += 2.0 * log2(Double(current))
                    } else if abs(log2(Double(current)) - log2(Double(next))) <= 1 {
                        // Potential merge after one step
                        score += 0.5 * log2(Double(min(current, next)))
                    }
                }
            }
        }
        
        // Vertical chains
        for j in 0..<4 {
            for i in 0..<3 {
                let current = board.grid[i][j]
                let next = board.grid[i + 1][j]
                if current != 0 && next != 0 {
                    if current == next {
                        // Immediate merge opportunity
                        score += 2.0 * log2(Double(current))
                    } else if abs(log2(Double(current)) - log2(Double(next))) <= 1 {
                        // Potential merge after one step
                        score += 0.5 * log2(Double(min(current, next)))
                    }
                }
            }
        }
        return score
    }
    
    private func calculateMonotonicity(_ board: GameBoard) -> Double {
        var score = 0.0
        
        // Rows
        for row in board.grid {
            for i in 0..<3 {
                let current = row[i]
                let next = row[i + 1]
                if current != 0 && next != 0 {
                    let currentLog = log2(Double(current))
                    let nextLog = log2(Double(next))
                    score += current >= next ? currentLog : -nextLog
                }
            }
        }
        
        // Columns
        for col in 0..<4 {
            for i in 0..<3 {
                let current = board.grid[i][col]
                let next = board.grid[i + 1][col]
                if current != 0 && next != 0 {
                    let currentLog = log2(Double(current))
                    let nextLog = log2(Double(next))
                    score += current >= next ? currentLog : -nextLog
                }
            }
        }
        return score
    }
    
    private func calculateSmoothness(_ board: GameBoard) -> Double {
        var score = 0.0
        for i in 0..<4 {
            for j in 0..<4 {
                if board.grid[i][j] == 0 { continue }
                let valueLog = log2(Double(board.grid[i][j]))
                
                // Right neighbor
                if j < 3 && board.grid[i][j + 1] != 0 {
                    score -= abs(valueLog - log2(Double(board.grid[i][j + 1])))
                }
                // Down neighbor
                if i < 3 && board.grid[i + 1][j] != 0 {
                    score -= abs(valueLog - log2(Double(board.grid[i + 1][j])))
                }
            }
        }
        return score
    }
    
    private func maxCornerAlignment(_ board: GameBoard) -> Double {
        let maxTile = board.maxTile
        let maxPositions = board.grid.enumerated().flatMap { (i, row) in
            row.enumerated().compactMap { (j, value) in
                value == maxTile ? (i, j) : nil
            }
        }
        
        guard let (i, j) = maxPositions.first else { return 0.0 }
        
        let isCorner = (i == 0 || i == 3) && (j == 0 || j == 3)
        let cornerBonus = isCorner ? 4.0 : 1.0
        
        let threshold = max(maxTile / 2, 2)
        let alignedRow = board.grid[i].filter { $0 >= threshold }.count
        let alignedCol = (0..<4).map { board.grid[$0][j] }.filter { $0 >= threshold }.count
        
        return cornerBonus * log2(Double(maxTile)) + Double(alignedRow + alignedCol)
    }
    
    private func getDynamicDepth(for board: GameBoard) -> Int {
        let emptyCells = board.emptyCount()
        let maxTile = board.maxTile
        
        if maxTile >= 1024 || emptyCells <= 4 {
            return baseDepth + 2
        } else if maxTile >= 512 || emptyCells <= 6 {
            return baseDepth + 1
        }
        return baseDepth
    }
    
    private func orderMoves(for board: GameBoard) -> [MoveDirection] {
        let moveScores = MoveDirection.allCases.compactMap { direction -> (MoveDirection, Double)? in
            guard let candidate = board.simulatedBoard(for: direction) else { return nil }
            let empties = Double(candidate.emptyCount())
            let _ = Double(candidate.maxTile)
            let alignment = maxCornerAlignment(candidate)
            let immediateScore = Double(candidate.score - board.score) + empties * 1.5 + alignment + calculateMonotonicity(candidate)
            let heuristic = immediateScore + Double(Self.moveHistory[direction, default: 0])
            return (direction, heuristic)
        }
        
        return moveScores.sorted { $0.1 > $1.1 }.map { $0.0 }
    }
    
    private static func pruneTranspositionTable() {
        let maxEntries = 5000
        if Self.transpositionTable.count <= maxEntries { return }
        
        // Remove oldest entries (Python-style pruning)
        let sortedKeys = Self.transpositionTable.keys.sorted()
        let keysToRemove = sortedKeys.prefix(Self.transpositionTable.count - maxEntries)
        for key in keysToRemove {
            Self.transpositionTable.removeValue(forKey: key)
        }
    }
    
    private func getStage(for board: GameBoard) -> String {
        let maxTile = board.maxTile
        let emptyCount = board.emptyCount()
        
        if maxTile < 512 && emptyCount > 8 {
            return "early"
        } else if maxTile < 1024 && emptyCount > 4 {
            return "mid"
        } else {
            return "late"
        }
    }
}

public final class GameScene: SKScene {

    private static let highScoreDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d, yyyy HH:mm"
        return formatter
    }()

    private static func generateRandomSeed() -> UInt64 {
        var generator = SystemRandomNumberGenerator()
        return generator.next()
    }

    private var activeSeed: UInt64 = GameScene.generateRandomSeed()
    private var pendingSeed: UInt64?
    private lazy var board = GameBoard(seed: activeSeed)
    private let boardContainer = SKNode()
    private let boardBackground = SKShapeNode()
    private var tileNodes: [[TileNode]] = []

    private var scoreLabel = SKLabelNode(fontNamed: "AvenirNext-Bold")
    private var maxScoreLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
    private var movesLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
    private var statusLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
    private var solverLabel = SKLabelNode(fontNamed: "AvenirNext-DemiBold")
    private let solverDropdownIcon = SKShapeNode()
    private var startLabel = SKLabelNode(fontNamed: "AvenirNext-DemiBold")
    private var newGameLabel = SKLabelNode(fontNamed: "AvenirNext-DemiBold")
    private var dynamicIslandButton = SKLabelNode(fontNamed: "AvenirNext-DemiBold")
    private let seedContainer = SKNode()
    private let seedBackground = SKShapeNode()
    private var seedTitleLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
    private var seedValueLabel = SKLabelNode(fontNamed: "AvenirNext-DemiBold")

    private var touchStartPoint: CGPoint?
    private let swipeThreshold: CGFloat = 32.0

    private var lastUpdateTimestamp: TimeInterval = 0
    private var solverAccumulator: TimeInterval = 0
    private let solverInterval: TimeInterval = 0.18

    private let solvers: [SolverStrategy] = [CornerTrapSolver(), SmoothnessSolver(), RandomSolver(), GrokSolver()]
    private var solverIndex: Int = 0 {
        didSet {
            isAutoplayActive = false
            updateSolverLabel()
            updateStartLabel()
            updateHUD()
        }
    }

    private var isAutoplayActive = false {
        didSet {
            solverAccumulator = 0
            if !isAutoplayActive && oldValue {
                resetArrowHighlights()
            }
            updateSolverLabel()
            updateStartLabel()
        }
    }

    private var activeSolver: SolverStrategy? {
        guard solverIndex > 0, isAutoplayActive else { return nil }
        return solvers[solverIndex - 1]
    }

    private let solverMenuContainer = SKNode()
    private let solverMenuBackground = SKShapeNode()
    private var solverOptionLabels: [SKLabelNode] = []
    private var isSolverMenuVisible = false

    private let tileSpacing: CGFloat = 12.0
    private var tileSize: CGFloat = 64.0
    private var arrowButtons: [MoveDirection: SKShapeNode] = [:]
    private let arrowContainer = SKNode()
    private let arrowButtonSize: CGFloat = 54.0
    private let arrowButtonSpacing: CGFloat = 12.0
    private let arrowDefaultColor = SKColor.white
    private let manualArrowHighlightColor = SKColor(red: 0.46, green: 0.78, blue: 0.94, alpha: 1.0)
    private let solverArrowHighlightColor = SKColor(red: 0.97, green: 0.52, blue: 0.32, alpha: 1.0)

    private let highScoreStore = HighScoreStore.shared
    private var hasRecordedOutcome = false
    private var didUseAutoplayThisGame = false
    private var lastAutoplaySolverName: String?
    private var isPresentingSeedPrompt = false

    public override func didMove(to view: SKView) {
        backgroundColor = SKColor(red: 0.18, green: 0.17, blue: 0.16, alpha: 1.0)
        setupHUD()
        setupBoard()
        setupControls()
        layoutScene()
        startNewGame()
    }

    public override func didChangeSize(_ oldSize: CGSize) {
        super.didChangeSize(oldSize)
        layoutScene()
    }

    private func setupHUD() {
        // Dynamic Island Buttons
        dynamicIslandButton.text = "Menu"
        dynamicIslandButton.fontSize = 20
        dynamicIslandButton.fontColor = SKColor(red: 0.46, green: 0.78, blue: 0.94, alpha: 1.0)
        dynamicIslandButton.name = "dynamicIslandButton"
        dynamicIslandButton.horizontalAlignmentMode = .left
        dynamicIslandButton.verticalAlignmentMode = .center
        // addChild(dynamicIslandButton)  // Hidden for now to avoid overlap with New Game button

    scoreLabel.fontSize = 32
    scoreLabel.fontColor = SKColor.white
    addChild(scoreLabel)

    maxScoreLabel.fontSize = 20
    maxScoreLabel.fontColor = SKColor(white: 0.9, alpha: 1.0)
    addChild(maxScoreLabel)

    movesLabel.fontSize = 20
    movesLabel.fontColor = SKColor(white: 0.9, alpha: 1.0)
    addChild(movesLabel)

        statusLabel.fontSize = 18
        statusLabel.fontColor = SKColor(white: 0.85, alpha: 1.0)
        statusLabel.horizontalAlignmentMode = .center
        addChild(statusLabel)

        solverLabel.fontSize = 18
        solverLabel.fontColor = SKColor(red: 0.67, green: 0.85, blue: 0.42, alpha: 1.0)
        solverLabel.name = "solverButton"
        addChild(solverLabel)

    let dropdownSize: CGFloat = 10
    let dropdownPath = CGMutablePath()
    dropdownPath.move(to: CGPoint(x: -dropdownSize / 2, y: dropdownSize * 0.2))
    dropdownPath.addLine(to: CGPoint(x: dropdownSize / 2, y: dropdownSize * 0.2))
    dropdownPath.addLine(to: CGPoint(x: 0, y: -dropdownSize * 0.3))
    dropdownPath.closeSubpath()
    solverDropdownIcon.path = dropdownPath
    solverDropdownIcon.fillColor = solverLabel.fontColor ?? SKColor.white
    solverDropdownIcon.strokeColor = SKColor.clear
    solverDropdownIcon.isAntialiased = true
    solverDropdownIcon.zPosition = solverLabel.zPosition
    solverDropdownIcon.name = "solverButton"
    addChild(solverDropdownIcon)

        startLabel.fontSize = 18
        startLabel.fontColor = SKColor(red: 0.46, green: 0.78, blue: 0.94, alpha: 1.0)
        startLabel.name = "startButton"
        startLabel.horizontalAlignmentMode = .left
        startLabel.verticalAlignmentMode = .center
        addChild(startLabel)

        setupSolverMenu()
        setupSeedField()

        newGameLabel.fontSize = 18
        newGameLabel.fontColor = SKColor(red: 0.96, green: 0.73, blue: 0.28, alpha: 1.0)
        newGameLabel.horizontalAlignmentMode = .left
        newGameLabel.name = "newGameButton"
        newGameLabel.text = "New Game"
        addChild(newGameLabel)

        updateStartLabel()
        updateSolverDropdownIcon()
    }

    private func setupSeedField() {
        if seedContainer.parent == nil {
            seedContainer.zPosition = 12
            seedContainer.name = "seedField"
            addChild(seedContainer)
        }

        seedContainer.removeAllChildren()

        seedBackground.fillColor = SKColor(red: 0.22, green: 0.21, blue: 0.20, alpha: 1.0)
        seedBackground.strokeColor = SKColor(white: 1.0, alpha: 0.12)
        seedBackground.lineWidth = 2
        seedBackground.name = "seedField"
        seedContainer.addChild(seedBackground)

        seedTitleLabel.fontSize = 14
        seedTitleLabel.fontColor = SKColor(white: 0.82, alpha: 1.0)
        seedTitleLabel.text = "Seed"
        seedTitleLabel.verticalAlignmentMode = .center
        seedTitleLabel.horizontalAlignmentMode = .center
        seedTitleLabel.position = CGPoint(x: 0, y: 12)
        seedTitleLabel.name = "seedField"
        seedContainer.addChild(seedTitleLabel)

        seedValueLabel.fontSize = 18
        seedValueLabel.fontColor = SKColor(red: 0.96, green: 0.73, blue: 0.28, alpha: 1.0)
        seedValueLabel.verticalAlignmentMode = .center
        seedValueLabel.horizontalAlignmentMode = .center
        seedValueLabel.position = CGPoint(x: 0, y: -10)
        seedValueLabel.name = "seedField"
        seedContainer.addChild(seedValueLabel)

        seedValueLabel.text = "\(activeSeed)"
    }

    private func presentSeedEntry() {
        guard !isPresentingSeedPrompt else { return }
        guard let view = view else { return }

        let displaySeed = pendingSeed ?? activeSeed
        let alert = UIAlertController(title: "Set Seed", message: "Enter a seed to replay specific games.", preferredStyle: .alert)
        alert.addTextField { textField in
            textField.keyboardType = .numberPad
            textField.placeholder = "Seed"
            textField.text = "\(displaySeed)"
        }

        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel) { [weak self] _ in
            self?.isPresentingSeedPrompt = false
        })

        alert.addAction(UIAlertAction(title: "Apply", style: .default) { [weak self] _ in
            guard let self else { return }
            defer { self.isPresentingSeedPrompt = false }
            guard let text = alert.textFields?.first?.text?.trimmingCharacters(in: .whitespacesAndNewlines), !text.isEmpty else {
                self.pendingSeed = nil
                self.seedValueLabel.text = "\(self.activeSeed)"
                return
            }
            if let value = UInt64(text) {
                self.pendingSeed = value
            }
            self.seedValueLabel.text = "\(self.pendingSeed ?? self.activeSeed)"
        })

        guard let controller = topViewController(for: view.window?.rootViewController) else { return }
        isPresentingSeedPrompt = true
        controller.present(alert, animated: true)
    }

    private func topViewController(for root: UIViewController?) -> UIViewController? {
        guard let root = root else { return nil }
        if let presented = root.presentedViewController {
            return topViewController(for: presented)
        }
        if let navigation = root as? UINavigationController {
            return topViewController(for: navigation.visibleViewController)
        }
        if let tab = root as? UITabBarController {
            return topViewController(for: tab.selectedViewController)
        }
        return root
    }

    private func setupSolverMenu() {
        if solverMenuContainer.parent == nil {
            solverMenuContainer.zPosition = 20
            addChild(solverMenuContainer)
        }

        solverMenuContainer.removeAllChildren()
        solverOptionLabels.removeAll()

        solverMenuBackground.fillColor = SKColor(red: 0.16, green: 0.15, blue: 0.14, alpha: 0.95)
        solverMenuBackground.strokeColor = SKColor(white: 1.0, alpha: 0.08)
        solverMenuBackground.lineWidth = 2
        solverMenuBackground.name = "solverMenuBackground"
        solverMenuBackground.isAntialiased = true
        solverMenuContainer.addChild(solverMenuBackground)

        let options = solverOptions()
        let itemHeight: CGFloat = 34
        let padding: CGFloat = 14
        let width: CGFloat = 220
        let height = padding * 2 + itemHeight * CGFloat(options.count)
        let backgroundRect = CGRect(x: -width / 2, y: -height, width: width, height: height)
        solverMenuBackground.path = CGPath(roundedRect: backgroundRect, cornerWidth: 16, cornerHeight: 16, transform: nil)

        var yPosition = -padding - itemHeight / 2
        for (index, title) in options.enumerated() {
            let optionLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
            optionLabel.fontSize = 18
            optionLabel.fontColor = SKColor(white: 0.9, alpha: 1.0)
            optionLabel.text = title
            optionLabel.verticalAlignmentMode = .center
            optionLabel.horizontalAlignmentMode = .center
            optionLabel.position = CGPoint(x: 0, y: yPosition)
            optionLabel.name = "solverOption_\(index)"
            solverMenuContainer.addChild(optionLabel)
            solverOptionLabels.append(optionLabel)
            yPosition -= itemHeight
        }

        solverMenuContainer.alpha = 0
        solverMenuContainer.isHidden = true
        isSolverMenuVisible = false
        updateSolverOptionHighlight()
    }

    private func solverOptions() -> [String] {
        var options = ["Manual"]
        options.append(contentsOf: solvers.map { $0.name })
        return options
    }

    private func updateSolverOptionHighlight() {
        guard !solverOptionLabels.isEmpty else { return }
        let selectedColor = SKColor(red: 0.96, green: 0.73, blue: 0.28, alpha: 1.0)
        let normalColor = SKColor(white: 0.9, alpha: 1.0)
        for (index, label) in solverOptionLabels.enumerated() {
            label.fontColor = index == solverIndex ? selectedColor : normalColor
            label.fontName = index == solverIndex ? "AvenirNext-DemiBold" : "AvenirNext-Medium"
        }
    }

    private func setupBoard() {
        boardBackground.fillColor = SKColor(red: 0.25, green: 0.24, blue: 0.23, alpha: 1.0)
        boardBackground.strokeColor = SKColor.clear
        boardBackground.lineWidth = 0
        boardContainer.addChild(boardBackground)
        addChild(boardContainer)

        tileNodes = []
        for _ in 0..<GameBoard.size {
            var rowNodes: [TileNode] = []
            for _ in 0..<GameBoard.size {
                let tile = TileNode()
                boardContainer.addChild(tile)
                rowNodes.append(tile)
            }
            tileNodes.append(rowNodes)
        }
    }

    private func setupControls() {
        if arrowContainer.parent == nil {
            arrowContainer.zPosition = 5
            addChild(arrowContainer)
        }
        arrowContainer.removeAllChildren()
        arrowButtons.removeAll()

        for direction in MoveDirection.allCases {
            let button = createArrowButton(for: direction)
            arrowButtons[direction] = button
            arrowContainer.addChild(button)
        }
    }

    private func createArrowButton(for direction: MoveDirection) -> SKShapeNode {
        let button = SKShapeNode(rectOf: CGSize(width: arrowButtonSize, height: arrowButtonSize), cornerRadius: 12)
        button.fillColor = SKColor(red: 0.32, green: 0.31, blue: 0.30, alpha: 1.0)
        button.strokeColor = SKColor.clear
        button.name = direction.nodeName

        let arrowPath = CGMutablePath()
        let tipHeight = arrowButtonSize * 0.26
        let baseWidth = arrowButtonSize * 0.26
        arrowPath.move(to: CGPoint(x: 0, y: tipHeight / 2))
        arrowPath.addLine(to: CGPoint(x: baseWidth / 2, y: -tipHeight / 2))
        arrowPath.addLine(to: CGPoint(x: -baseWidth / 2, y: -tipHeight / 2))
        arrowPath.closeSubpath()

        let arrowShape = SKShapeNode(path: arrowPath)
    arrowShape.fillColor = arrowDefaultColor
        arrowShape.strokeColor = SKColor.clear
        arrowShape.zPosition = 1
        arrowShape.name = direction.nodeName

        switch direction {
        case .up:
            arrowShape.zRotation = 0
        case .right:
            arrowShape.zRotation = -.pi / 2
        case .down:
            arrowShape.zRotation = .pi
        case .left:
            arrowShape.zRotation = .pi / 2
        }

        button.addChild(arrowShape)
        return button
    }

    private func layoutArrowButtons() {
        guard !arrowButtons.isEmpty else { return }
        let offset = (arrowButtonSize + arrowButtonSpacing) * 0.8
        arrowButtons[.up]?.position = CGPoint(x: 0, y: offset)
        arrowButtons[.down]?.position = CGPoint(x: 0, y: -offset)
        arrowButtons[.left]?.position = CGPoint(x: -offset, y: 0)
        arrowButtons[.right]?.position = CGPoint(x: offset, y: 0)
    }

    private func layoutScene() {
        guard tileNodes.count == GameBoard.size,
              tileNodes.allSatisfy({ $0.count == GameBoard.size }) else {
            return
        }

        let boardSide = min(size.width - 48, size.height - 220)
        let adjustedSide = max(boardSide, 220)
        tileSize = (adjustedSide - tileSpacing * CGFloat(GameBoard.size + 1)) / CGFloat(GameBoard.size)

        boardContainer.position = CGPoint(x: size.width / 2, y: size.height / 2 - 20)
        let backgroundRect = CGRect(x: -adjustedSide / 2, y: -adjustedSide / 2, width: adjustedSide, height: adjustedSide)
        boardBackground.path = CGPath(roundedRect: backgroundRect, cornerWidth: 20, cornerHeight: 20, transform: nil)

        let startX = -adjustedSide / 2 + tileSpacing + tileSize / 2
        let startY = adjustedSide / 2 - tileSpacing - tileSize / 2

        for row in 0..<GameBoard.size {
            for col in 0..<GameBoard.size {
                let tile = tileNodes[row][col]
                let posX = startX + CGFloat(col) * (tileSize + tileSpacing)
                let posY = startY - CGFloat(row) * (tileSize + tileSpacing)
                tile.position = CGPoint(x: posX, y: posY)
                tile.updateGeometry(size: CGSize(width: tileSize, height: tileSize), cornerRadius: 14)
            }
        }

        let boardTop = boardContainer.position.y + adjustedSide / 2
        let boardBottom = boardContainer.position.y - adjustedSide / 2

    let topPadding = max(size.height * 0.035, 42)
    let hudSpacing: CGFloat = 34
    let hudTop = size.height - topPadding

    // Dynamic Island bar
    let dynamicIslandY = hudTop
    let islandMargin: CGFloat = 32
    dynamicIslandButton.position = CGPoint(x: islandMargin, y: dynamicIslandY)

    // Score and Max on first line (left and right)
    scoreLabel.position = CGPoint(x: size.width / 4, y: dynamicIslandY - hudSpacing)
    maxScoreLabel.position = CGPoint(x: 3 * size.width / 4, y: dynamicIslandY - hudSpacing)

    // Seed and Moves on second line (left and right)
    let seedWidth = min(CGFloat(240), max(size.width * CGFloat(0.45), CGFloat(180)))
    let seedHeight: CGFloat = 52
    let seedRect = CGRect(x: -seedWidth / 2, y: -seedHeight / 2, width: seedWidth, height: seedHeight)
    seedBackground.path = CGPath(roundedRect: seedRect, cornerWidth: 16, cornerHeight: 16, transform: nil)
    let seedY = scoreLabel.position.y - hudSpacing * 1.2
    let seedX = size.width / 4
    seedContainer.position = CGPoint(x: seedX, y: seedY)

    // Moves label on the right side of second line
    movesLabel.position = CGPoint(x: 3 * size.width / 4, y: seedY)

    newGameLabel.position = CGPoint(x: 28, y: hudTop)

    // Solver and Start above board
    let solverY = boardTop + 60
    solverLabel.position = CGPoint(x: size.width / 2 - 80, y: solverY)
    startLabel.position = CGPoint(x: size.width / 2 + 80, y: solverY)
    updateSolverDropdownIcon()

        let menuHeight = solverMenuBackground.frame.height
        var menuTopY = solverLabel.position.y - 28
        let maxMenuTop = size.height - 72
        if menuTopY > maxMenuTop {
            menuTopY = maxMenuTop
        }
        if menuHeight > 0 {
            let minMenuTop = solverLabel.position.y - 32
            if menuTopY > minMenuTop {
                menuTopY = minMenuTop
            }
        }
        solverMenuContainer.position = CGPoint(x: solverLabel.position.x, y: menuTopY)

        let arrowYOffset = arrowButtonSize + arrowButtonSpacing
        arrowContainer.position = CGPoint(x: size.width / 2, y: boardBottom - arrowYOffset)
        let minArrowY = arrowButtonSize * 0.5 + 52
        if arrowContainer.position.y < minArrowY {
            arrowContainer.position.y = minArrowY
        }

        layoutArrowButtons()

    let statusBottomPadding = max(size.height * 0.025, 32)
    statusLabel.position = CGPoint(x: size.width / 2, y: statusBottomPadding)
    }

    private func startNewGame() {
        hideSolverMenu()
        let seedToUse: UInt64
        if let override = pendingSeed {
            seedToUse = override
            pendingSeed = nil
        } else {
            seedToUse = GameScene.generateRandomSeed()
        }

        activeSeed = seedToUse
        board.reset(withSeed: seedToUse)
        solverAccumulator = 0
        isAutoplayActive = false
        hasRecordedOutcome = false
        didUseAutoplayThisGame = false
        lastAutoplaySolverName = nil
        updateHUD()
        updateTiles(animated: false)
        resetArrowHighlights()
    }

    private func attemptMove(_ direction: MoveDirection) {
        guard board.status == .inProgress else { return }
        if board.move(direction) {
            solverAccumulator = 0
            updateHUD()
            updateTiles(animated: true)
            highlightArrow(direction)
        }
    }

    private func highlightArrow(_ direction: MoveDirection, isSolverMove: Bool = false) {
        for (dir, button) in arrowButtons {
            guard let arrowShape = button.children.first(where: { $0.name == dir.nodeName }) as? SKShapeNode else { continue }
            arrowShape.removeAction(forKey: "arrowPulse")
            arrowShape.setScale(1.0)

            if dir == direction {
                let color = isSolverMove ? solverArrowHighlightColor : manualArrowHighlightColor
                arrowShape.fillColor = color

                if isSolverMove {
                    let pulseUp = SKAction.scale(to: 1.15, duration: 0.08)
                    let pulseDown = SKAction.scale(to: 1.0, duration: 0.12)
                    arrowShape.run(SKAction.sequence([pulseUp, pulseDown]), withKey: "arrowPulse")
                } else {
                    let wait = SKAction.wait(forDuration: 0.25)
                    let reset = SKAction.run { [weak self, weak arrowShape] in
                        guard let self = self else { return }
                        arrowShape?.fillColor = self.arrowDefaultColor
                    }
                    arrowShape.run(SKAction.sequence([wait, reset]), withKey: "arrowPulse")
                }
            } else {
                arrowShape.fillColor = arrowDefaultColor
            }
        }
    }

    private func resetArrowHighlights() {
        for (dir, button) in arrowButtons {
            guard let arrowShape = button.children.first(where: { $0.name == dir.nodeName }) as? SKShapeNode else { continue }
            arrowShape.removeAction(forKey: "arrowPulse")
            arrowShape.fillColor = arrowDefaultColor
            arrowShape.setScale(1.0)
        }
    }

    private func updateHUD() {
        scoreLabel.text = "Score: \(board.score)"
        maxScoreLabel.text = board.maxTile > 2 ? "Max: \(board.maxTile)" : ""
        movesLabel.text = "Moves: \(board.moves)"

        var statusMessage: String
        if let milestone = board.consumeMilestone() {
            statusMessage = "Achievement unlocked: \(milestone)!"
        } else {
            switch board.status {
            case .inProgress:
                if isAutoplayActive {
                    statusMessage = "Solver running..."
                } else if solverIndex > 0 {
                    statusMessage = "Tap Start to run the solver"
                } else {
                    statusMessage = board.lastScoreGain > 0 ? "Last merge +\(board.lastScoreGain)" : "Swipe to play manually"
                }
            case .won:
                statusMessage = "Victory! 65536 achieved"
            case .lost:
                statusMessage = "No moves left. Tap New Game."
            }
        }

        if board.status != .inProgress {
            if !hasRecordedOutcome {
                recordHighScore()
            }
            isAutoplayActive = false
        }

        statusLabel.text = statusMessage
        updateSolverLabel()
    }

    private func updateSolverLabel() {
        let options = solverOptions()
        let clampedIndex = min(max(solverIndex, 0), options.count - 1)
        solverLabel.text = options[clampedIndex]
        updateSolverDropdownIcon()
        updateSolverOptionHighlight()
        updateStartLabel()
    }

    private func updateSolverDropdownIcon() {
        guard solverDropdownIcon.parent != nil else { return }
        solverDropdownIcon.fillColor = solverLabel.fontColor ?? SKColor.white
        let labelFrame = solverLabel.calculateAccumulatedFrame()
        let width = max(labelFrame.width, 1)
        let height = labelFrame.height
        let offsetX = width / 2 + 12
        let offsetY = height > 0 ? -height * 0.25 : -2
        solverDropdownIcon.position = CGPoint(x: solverLabel.position.x + offsetX,
                                              y: solverLabel.position.y + offsetY)
    }

    private func updateStartLabel() {
        if solverIndex == 0 {
            startLabel.isHidden = true
        } else {
            startLabel.isHidden = false
            startLabel.text = isAutoplayActive ? "Stop" : "Start"
        }
    }

    private func updateTiles(animated: Bool) {
        for row in 0..<GameBoard.size {
            for col in 0..<GameBoard.size {
                let value = board.grid[row][col]
                let tile = tileNodes[row][col]
                configure(tile: tile, with: value)
            }
        }

        if let spawn = board.lastSpawnPosition, animated {
            let tile = tileNodes[spawn.row][spawn.col]
            tile.setScale(0.1)
            tile.run(SKAction.sequence([
                SKAction.scale(to: 1.1, duration: 0.1),
                SKAction.scale(to: 1.0, duration: 0.08)
            ]))
        }
        board.clearLastSpawn()
    }

    private func configure(tile: TileNode, with value: Int) {
        tile.fillColor = color(for: value)
        if value == 0 {
            tile.valueLabel.text = ""
        } else {
            tile.valueLabel.text = "\(value)"
            tile.valueLabel.fontColor = value <= 4 ? SKColor(red: 0.47, green: 0.43, blue: 0.39, alpha: 1.0) : SKColor.white
            tile.valueLabel.fontSize = fontSize(for: value)
        }
    }

    private func color(for value: Int) -> SKColor {
        switch value {
        case 2: return SKColor(red: 0.93, green: 0.89, blue: 0.86, alpha: 1.0)
        case 4: return SKColor(red: 0.93, green: 0.88, blue: 0.78, alpha: 1.0)
        case 8: return SKColor(red: 0.95, green: 0.69, blue: 0.48, alpha: 1.0)
        case 16: return SKColor(red: 0.96, green: 0.58, blue: 0.39, alpha: 1.0)
        case 32: return SKColor(red: 0.96, green: 0.49, blue: 0.37, alpha: 1.0)
        case 64: return SKColor(red: 0.96, green: 0.37, blue: 0.23, alpha: 1.0)
        case 128: return SKColor(red: 0.93, green: 0.81, blue: 0.45, alpha: 1.0)
        case 256: return SKColor(red: 0.93, green: 0.80, blue: 0.38, alpha: 1.0)
        case 512: return SKColor(red: 0.93, green: 0.78, blue: 0.31, alpha: 1.0)
        case 1024: return SKColor(red: 0.93, green: 0.77, blue: 0.25, alpha: 1.0)
        case 2048: return SKColor(red: 0.93, green: 0.76, blue: 0.18, alpha: 1.0)
        case 4096: return SKColor(red: 0.93, green: 0.74, blue: 0.12, alpha: 1.0)
        case 8192: return SKColor(red: 0.93, green: 0.72, blue: 0.08, alpha: 1.0)
        case 16384: return SKColor(red: 0.93, green: 0.70, blue: 0.06, alpha: 1.0)
        case 32768: return SKColor(red: 0.93, green: 0.68, blue: 0.04, alpha: 1.0)
        case 65536: return SKColor(red: 0.93, green: 0.67, blue: 0.02, alpha: 1.0)
        default: return value > 0 ? SKColor(red: 0.94, green: 0.65, blue: 0.01, alpha: 1.0) : SKColor(red: 0.80, green: 0.74, blue: 0.69, alpha: 1.0)
        }
    }

    private func fontSize(for value: Int) -> CGFloat {
        switch value {
        case 0: return 0
        case 1...4: return 36
        case 5...512: return 30
        case 513...16384: return 24
        default: return 20
        }
    }

    private func toggleSolverMenu() {
        if isSolverMenuVisible {
            hideSolverMenu()
        } else {
            showSolverMenu()
        }
    }

    private func showSolverMenu() {
        guard !isSolverMenuVisible else { return }
        isSolverMenuVisible = true
        solverMenuContainer.removeAllActions()
        solverMenuContainer.isHidden = false
        solverMenuContainer.alpha = 0
        updateSolverOptionHighlight()
        solverMenuContainer.run(SKAction.fadeIn(withDuration: 0.18))
    }

    private func hideSolverMenu() {
        guard isSolverMenuVisible else { return }
        isSolverMenuVisible = false
        solverMenuContainer.removeAllActions()
        let fadeOut = SKAction.fadeOut(withDuration: 0.14)
        let hideAction = SKAction.run { [weak self] in
            self?.solverMenuContainer.isHidden = true
            self?.solverMenuContainer.alpha = 0
        }
        solverMenuContainer.run(SKAction.sequence([fadeOut, hideAction]))
    }

    public override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        let location = touches.first?.location(in: self)
        touchStartPoint = location

        // Dynamic Island button
        if let loc = location {
            if dynamicIslandButton.contains(loc) {
                // TODO: Implement menu/modal logic
                print("Dynamic Island button tapped")
            }
        }
    }

    public override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        // No-op; movement handled in touchesEnded.
    }

    public override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let endPoint = touch.location(in: self)

        if let startPoint = touchStartPoint {
            let dx = endPoint.x - startPoint.x
            let dy = endPoint.y - startPoint.y
            let distance = hypot(dx, dy)

            if distance < swipeThreshold {
                handleTap(at: endPoint)
            } else {
                handleSwipe(dx: dx, dy: dy)
            }
        }

        touchStartPoint = nil
    }

    public override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        touchStartPoint = nil
    }

    private func handleTap(at location: CGPoint) {
        let nodes = self.nodes(at: location)
        if nodes.contains(where: { $0.name == "newGameButton" }) {
            startNewGame()
            return
        }
        if nodes.contains(where: { $0.name == "solverButton" }) {
            toggleSolverMenu()
            return
        }
        if nodes.contains(where: { $0.name == "startButton" }) {
            handleStartTapped()
            return
        }
        if nodes.contains(where: { $0.name == "seedField" }) {
            hideSolverMenu()
            presentSeedEntry()
            return
        }
        if let optionNode = nodes.first(where: { $0.name?.hasPrefix("solverOption_") == true }),
           let name = optionNode.name,
           let indexString = name.split(separator: "_").last,
           let selectedIndex = Int(indexString) {
            solverIndex = min(max(selectedIndex, 0), solvers.count)
            solverAccumulator = 0
            hideSolverMenu()
            updateHUD()
            return
        }
        if let direction = nodes.compactMap({ directionForNodeName($0.name) }).first {
            attemptMove(direction)
            if solverIndex != 0 {
                solverIndex = 0
            }
            isAutoplayActive = false
            hideSolverMenu()
            updateHUD()
            return
        }

        if isSolverMenuVisible {
            let pointInMenu = convert(location, to: solverMenuContainer)
            if solverMenuBackground.contains(pointInMenu) {
                return
            }
            hideSolverMenu()
        }
    }

    private func directionForNodeName(_ name: String?) -> MoveDirection? {
        guard let name = name else { return nil }
        return MoveDirection.from(nodeName: name)
    }

    private func handleSwipe(dx: CGFloat, dy: CGFloat) {
        hideSolverMenu()
        if abs(dx) > abs(dy) {
            attemptMove(dx > 0 ? .right : .left)
        } else {
            attemptMove(dy > 0 ? .up : .down)
        }
        if solverIndex != 0 {
            solverIndex = 0
        }
        isAutoplayActive = false
        updateHUD()
    }

    func handleExternalInput(_ direction: MoveDirection) {
        hideSolverMenu()
        attemptMove(direction)
        if solverIndex != 0 {
            solverIndex = 0
        }
        isAutoplayActive = false
        updateHUD()
    }

    public override func update(_ currentTime: TimeInterval) {
        if lastUpdateTimestamp == 0 {
            lastUpdateTimestamp = currentTime
        }
        let delta = currentTime - lastUpdateTimestamp
        lastUpdateTimestamp = currentTime
        runSolverIfNeeded(deltaTime: delta)
    }

    private func runSolverIfNeeded(deltaTime: TimeInterval) {
        guard let solver = activeSolver, board.status == .inProgress else { return }
        solverAccumulator += deltaTime
        if solverAccumulator < solverInterval {
            return
        }
        solverAccumulator = 0

        let move = solver.nextMove(for: board) ?? board.availableMoves().randomElement()
        guard let direction = move else { return }
        if board.move(direction) {
            highlightArrow(direction, isSolverMove: true)
            updateHUD()
            updateTiles(animated: true)
        }
    }

    private func recordHighScore() {
        hasRecordedOutcome = true
        let mode: String
        if didUseAutoplayThisGame, let solverName = lastAutoplaySolverName {
            mode = "Solver: \(solverName)"
        } else {
            mode = "Manual"
        }
        let entry = HighScoreEntry(date: Date(), score: board.score, maxTile: board.maxTile, moves: board.moves, seed: activeSeed, mode: mode)
        highScoreStore.add(entry)
    }

    private func handleStartTapped() {
        hideSolverMenu()
        if solverIndex == 0 {
            isAutoplayActive = false
            updateHUD()
            return
        }

        let shouldActivate = !isAutoplayActive
        isAutoplayActive = shouldActivate
        if shouldActivate {
            solverAccumulator = 0
            didUseAutoplayThisGame = true
            if solverIndex > 0 {
                lastAutoplaySolverName = solvers[solverIndex - 1].name
            }
        }
        updateHUD()
    }
}

private final class TileNode: SKShapeNode {
    let valueLabel: SKLabelNode

    override init() {
        valueLabel = SKLabelNode(fontNamed: "AvenirNext-Bold")
        super.init()
        valueLabel.fontSize = 32
        valueLabel.fontColor = SKColor.white
        valueLabel.verticalAlignmentMode = .center
        valueLabel.horizontalAlignmentMode = .center
        addChild(valueLabel)

        fillColor = SKColor(red: 0.80, green: 0.74, blue: 0.69, alpha: 1.0)
        strokeColor = SKColor.clear
        lineWidth = 0
    }

    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func updateGeometry(size: CGSize, cornerRadius: CGFloat) {
        let rect = CGRect(x: -size.width / 2, y: -size.height / 2, width: size.width, height: size.height)
        path = CGPath(roundedRect: rect, cornerWidth: cornerRadius, cornerHeight: cornerRadius, transform: nil)
    }
}
