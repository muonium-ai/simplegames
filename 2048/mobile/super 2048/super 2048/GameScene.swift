//
//  GameScene.swift
//  super 2048
//
//  Created by Senthil Nayagam on 19/10/25.
//

import SpriteKit
import Foundation

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

    init() {
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
        refreshStatus()
    }

    mutating func reset() {
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
        let index = Int.random(in: 0..<empty.count)
        let (row, col) = empty[index]
        grid[row][col] = Double.random(in: 0..<1) < 0.9 ? 2 : 4
        lastSpawnPosition = (row, col)
    }

    private mutating func updateMaxTile() {
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

final class GameScene: SKScene {

    private var board = GameBoard()
    private let boardContainer = SKNode()
    private let boardBackground = SKShapeNode()
    private var tileNodes: [[TileNode]] = []

    private var scoreLabel = SKLabelNode(fontNamed: "AvenirNext-Bold")
    private var movesLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
    private var statusLabel = SKLabelNode(fontNamed: "AvenirNext-Medium")
    private var solverLabel = SKLabelNode(fontNamed: "AvenirNext-DemiBold")
    private var newGameLabel = SKLabelNode(fontNamed: "AvenirNext-DemiBold")

    private var touchStartPoint: CGPoint?
    private let swipeThreshold: CGFloat = 32.0

    private var lastUpdateTimestamp: TimeInterval = 0
    private var solverAccumulator: TimeInterval = 0
    private let solverInterval: TimeInterval = 0.18

    private let solvers: [SolverStrategy] = [CornerTrapSolver(), SmoothnessSolver(), RandomSolver()]
    private var solverIndex: Int = 0 {
        didSet { updateSolverLabel() }
    }

    private var activeSolver: SolverStrategy? {
        return solverIndex == 0 ? nil : solvers[solverIndex - 1]
    }

    private let tileSpacing: CGFloat = 12.0
    private var tileSize: CGFloat = 64.0
    private var arrowButtons: [MoveDirection: SKShapeNode] = [:]
    private let arrowContainer = SKNode()
    private let arrowButtonSize: CGFloat = 54.0
    private let arrowButtonSpacing: CGFloat = 12.0

    override func didMove(to view: SKView) {
        backgroundColor = SKColor(red: 0.18, green: 0.17, blue: 0.16, alpha: 1.0)
        setupHUD()
        setupBoard()
        setupControls()
        layoutScene()
        startNewGame()
    }

    override func didChangeSize(_ oldSize: CGSize) {
        super.didChangeSize(oldSize)
        layoutScene()
    }

    private func setupHUD() {
        scoreLabel.fontSize = 32
        scoreLabel.fontColor = SKColor.white
        addChild(scoreLabel)

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

        newGameLabel.fontSize = 18
        newGameLabel.fontColor = SKColor(red: 0.96, green: 0.73, blue: 0.28, alpha: 1.0)
        newGameLabel.horizontalAlignmentMode = .left
        newGameLabel.name = "newGameButton"
        newGameLabel.text = "New Game"
        addChild(newGameLabel)
    }

    private func setupBoard() {
        boardBackground.fillColor = SKColor(red: 0.25, green: 0.24, blue: 0.23, alpha: 1.0)
        boardBackground.strokeColor = SKColor.clear
        boardBackground.lineWidth = 0
        boardContainer.addChild(boardBackground)
        addChild(boardContainer)

        tileNodes = []
        for row in 0..<GameBoard.size {
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
        arrowShape.fillColor = SKColor.white
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

        scoreLabel.position = CGPoint(x: size.width / 2, y: size.height - 80)
        movesLabel.position = CGPoint(x: size.width / 2, y: size.height - 118)
        statusLabel.position = CGPoint(x: size.width / 2, y: 80)
        solverLabel.position = CGPoint(x: size.width / 2, y: 40)
        newGameLabel.position = CGPoint(x: 24, y: size.height - 44)
        arrowContainer.position = CGPoint(x: size.width / 2, y: 72)
        layoutArrowButtons()
    }

    private func startNewGame() {
        board.reset()
        solverAccumulator = 0
        updateHUD()
        updateTiles(animated: false)
    }

    private func attemptMove(_ direction: MoveDirection) {
        guard board.status == .inProgress else { return }
        if board.move(direction) {
            solverAccumulator = 0
            updateHUD()
            updateTiles(animated: true)
        }
    }

    private func updateHUD() {
        scoreLabel.text = "Score: \(board.score)"
        movesLabel.text = "Moves: \(board.moves)  Max: \(board.maxTile)"

        var statusMessage: String
        if let milestone = board.consumeMilestone() {
            statusMessage = "Achievement unlocked: \(milestone)!"
        } else {
            switch board.status {
            case .inProgress:
                statusMessage = board.lastScoreGain > 0 ? "Last merge +\(board.lastScoreGain)" : "Swipe or tap solver to play"
            case .won:
                statusMessage = "Victory! 65536 achieved"
            case .lost:
                statusMessage = "No moves left. Tap New Game."
            }
        }
        statusLabel.text = statusMessage
        updateSolverLabel()
    }

    private func updateSolverLabel() {
        let solverName = solverIndex == 0 ? "Manual" : activeSolver?.name ?? "Unknown"
        let extra = solverIndex == 0 ? "(tap to cycle solvers)" : "(auto-playing)"
        solverLabel.text = "Solver: \(solverName) \(extra)"
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

    private func cycleSolver() {
        solverIndex = (solverIndex + 1) % (solvers.count + 1)
        solverAccumulator = 0
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        touchStartPoint = touches.first?.location(in: self)
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        // No-op; movement handled in touchesEnded.
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
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

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        touchStartPoint = nil
    }

    private func handleTap(at location: CGPoint) {
        let nodes = self.nodes(at: location)
        if nodes.contains(where: { $0.name == "newGameButton" }) {
            startNewGame()
            return
        }
        if nodes.contains(where: { $0.name == "solverButton" }) {
            cycleSolver()
            return
        }
        if let direction = nodes.compactMap({ directionForNodeName($0.name) }).first {
            attemptMove(direction)
            if solverIndex != 0 {
                solverIndex = 0
            }
            return
        }
    }

    private func directionForNodeName(_ name: String?) -> MoveDirection? {
        guard let name = name else { return nil }
        return MoveDirection.from(nodeName: name)
    }

    private func handleSwipe(dx: CGFloat, dy: CGFloat) {
        if abs(dx) > abs(dy) {
            attemptMove(dx > 0 ? .right : .left)
        } else {
            attemptMove(dy > 0 ? .up : .down)
        }
        if solverIndex != 0 {
            solverIndex = 0
        }
    }

    func handleExternalInput(_ direction: MoveDirection) {
        attemptMove(direction)
        if solverIndex != 0 {
            solverIndex = 0
        }
    }

    override func update(_ currentTime: TimeInterval) {
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
            updateHUD()
            updateTiles(animated: true)
        }
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
