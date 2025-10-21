import SpriteKit
import UIKit

class GameScene: SKScene {
    
    private var boardSize = 3
    private var tileSize: CGFloat = 0
    private var tiles: [SKSpriteNode?] = []
    private var emptyTileIndex: Int = 0
    private var gameWon = false
    
    private var moves = 0
    private var movesLabel: SKLabelNode!
    private var shuffleButton: SKNode!
    private var settingsButton: SKNode!
    private var solveButton: SKNode!
    
    private var settingsPanel: SKShapeNode!

    override func didMove(to view: SKView) {
        anchorPoint = CGPoint(x: 0.5, y: 0.5)
        setupUI()
        setupGame()
    }

    func setupUI() {
        // Moves label
        movesLabel = SKLabelNode(fontNamed: "Arial-BoldMT")
        movesLabel.text = "Moves: 0"
        movesLabel.fontSize = 30
        movesLabel.fontColor = .white
        movesLabel.position = CGPoint(x: 0, y: size.height/2 - 80)
        addChild(movesLabel)

        // Bottom buttons container
        let bottomButtonY = -size.height/2 + 60
        let buttonSpacing: CGFloat = 140
        
        // Create buttons
        shuffleButton = createButton(text: "Shuffle", name: "shuffle")
        shuffleButton.position = CGPoint(x: -buttonSpacing, y: bottomButtonY)
        addChild(shuffleButton)
        
        solveButton = createButton(text: "Solve", name: "solve")
        solveButton.position = CGPoint(x: 0, y: bottomButtonY)
        addChild(solveButton)
        
        settingsButton = createButton(text: "Settings", name: "settings")
        settingsButton.position = CGPoint(x: buttonSpacing, y: bottomButtonY)
        addChild(settingsButton)
        
        createSettingsPanel()
    }
    
    func createButton(text: String, name: String) -> SKNode {
        let buttonNode = SKNode()
        buttonNode.name = name
        
        let buttonWidth: CGFloat = 120
        let buttonHeight: CGFloat = 40
        
        let background = SKShapeNode(rectOf: CGSize(width: buttonWidth, height: buttonHeight), cornerRadius: 10)
        background.fillColor = SKColor(white: 0.2, alpha: 1)
        background.strokeColor = .white
        background.lineWidth = 2
        buttonNode.addChild(background)
        
        let label = SKLabelNode(fontNamed: "Arial-BoldMT")
        label.text = text
        label.fontSize = 20
        label.fontColor = .white
        label.verticalAlignmentMode = .center
        buttonNode.addChild(label)
        
        return buttonNode
    }

    func createSettingsPanel() {
        settingsPanel = SKShapeNode(rectOf: CGSize(width: size.width * 0.8, height: size.height * 0.6), cornerRadius: 15)
        settingsPanel.fillColor = SKColor(white: 0, alpha: 0.8)
        settingsPanel.strokeColor = .white
        settingsPanel.lineWidth = 2
        settingsPanel.position = CGPoint(x: 0, y: 0)
        settingsPanel.zPosition = 200
        
        // Title
        let title = SKLabelNode(fontNamed: "Arial-BoldMT")
        title.text = "Settings"
        title.fontSize = 40
        title.fontColor = .white
        title.position = CGPoint(x: 0, y: settingsPanel.frame.height/2 - 60)
        settingsPanel.addChild(title)
        
        // Board Size Section
        let sizeLabel = SKLabelNode(fontNamed: "Arial")
        sizeLabel.text = "Board Size:"
        sizeLabel.fontSize = 24
        sizeLabel.fontColor = .white
        sizeLabel.position = CGPoint(x: 0, y: 100)
        settingsPanel.addChild(sizeLabel)
        
        for (i, size) in [3, 4, 5].enumerated() {
            let sizeButton = SKLabelNode(fontNamed: "Arial-BoldMT")
            sizeButton.text = "\(size)x\(size)"
            sizeButton.fontSize = 28
            sizeButton.fontColor = self.boardSize == size ? .green : .white
            sizeButton.name = "size_\(size)"
            sizeButton.position = CGPoint(x: -100 + (i * 100), y: 50)
            settingsPanel.addChild(sizeButton)
        }
        
        // Background Color Section
        let bgLabel = SKLabelNode(fontNamed: "Arial")
        bgLabel.text = "Background Color:"
        bgLabel.fontSize = 24
        bgLabel.fontColor = .white
        bgLabel.position = CGPoint(x: 0, y: -20)
        settingsPanel.addChild(bgLabel)
        
        let colors: [String: SKColor] = ["Black": .black, "Blue": .blue, "Gray": .darkGray]
        for (i, (colorName, color)) in colors.enumerated() {
            let colorButton = SKShapeNode(rectOf: CGSize(width: 50, height: 50), cornerRadius: 10)
            colorButton.fillColor = color
            colorButton.strokeColor = self.backgroundColor == color ? .green : .white
            colorButton.lineWidth = 3
            colorButton.name = "color_\(colorName)"
            colorButton.position = CGPoint(x: -80 + (i * 80), y: -70)
            settingsPanel.addChild(colorButton)
        }
        
        // Back Button
        let backButton = SKLabelNode(fontNamed: "Arial-BoldMT")
        backButton.text = "Back"
        backButton.fontSize = 30
        backButton.fontColor = .white
        backButton.name = "back"
        backButton.position = CGPoint(x: 0, y: -settingsPanel.frame.height/2 + 40)
        settingsPanel.addChild(backButton)
        
        settingsPanel.isHidden = true
        addChild(settingsPanel)
    }
    
    func toggleSettingsPanel(show: Bool) {
        settingsPanel.isHidden = !show
    }

    func setupGame() {
        gameWon = false
        moves = 0
        movesLabel.text = "Moves: 0"
        
        // Remove old tiles and win label
        children.filter { $0.name?.starts(with: "tile") ?? false }.forEach { $0.removeFromParent() }
        childNode(withName: "winLabel")?.removeFromParent()

        tileSize = (size.width * 0.9) / CGFloat(boardSize)
        let totalTiles = boardSize * boardSize
        tiles = Array(repeating: nil, count: totalTiles)

        for i in 0..<(totalTiles - 1) {
            let tile = SKSpriteNode(color: .darkGray, size: CGSize(width: tileSize - 4, height: tileSize - 4))
            // Safely load texture
            if let tileTexture = SKTexture(imageNamed: "tile_bg") as SKTexture? {
                tile.texture = tileTexture
            }
            tile.name = "tile\(i+1)"
            
            let numberLabel = SKLabelNode(fontNamed: "Arial-BoldMT")
            numberLabel.text = "\(i+1)"
            numberLabel.fontSize = 40
            numberLabel.fontColor = .white
            numberLabel.verticalAlignmentMode = .center
            tile.addChild(numberLabel)
            
            tiles[i] = tile
            tile.position = position(for: i)
            addChild(tile)
        }
        
        emptyTileIndex = totalTiles - 1
        tiles[emptyTileIndex] = nil

        shuffleBoard()
    }

    func position(for index: Int) -> CGPoint {
        let boardWidth = tileSize * CGFloat(boardSize)
        let boardHeight = tileSize * CGFloat(boardSize)
        
        let row = CGFloat(index / boardSize)
        let col = CGFloat(index % boardSize)
        
        let x = col * tileSize + tileSize / 2 - boardWidth / 2
        let y = boardHeight / 2 - (row * tileSize + tileSize / 2)
        return CGPoint(x: x, y: y)
    }

    func shuffleBoard() {
        // Using Random-Walk Scramble from PRD
        var lastMove: Int? = nil
        // A higher number of steps for a better shuffle
        for _ in 0..<200 {
            let validMoves = getValidMoves()
            var movableTiles = validMoves
            
            // Avoid immediate backtracks to increase variety
            if let last = lastMove, let backTrackIndex = movableTiles.firstIndex(of: last) {
                movableTiles.remove(at: backTrackIndex)
            }
            
            guard let randomTileIndex = movableTiles.randomElement() else { continue }
            
            // In a random walk, we simulate moving a tile into the empty space.
            // The tile at `randomTileIndex` moves into the `emptyTileIndex`.
            tiles.swapAt(randomTileIndex, emptyTileIndex)
            
            // The new empty spot is where the tile *was*.
            lastMove = emptyTileIndex
            emptyTileIndex = randomTileIndex
        }
        
        // After shuffling the model, update the visual positions of all tiles.
        for (index, tile) in tiles.enumerated() {
            tile?.position = position(for: index)
        }
    }

    func getValidMoves() -> [Int] {
        var moves: [Int] = []
        let emptyRow = emptyTileIndex / boardSize
        let emptyCol = emptyTileIndex % boardSize

        // These are the indices of tiles that can move *into* the empty space
        if emptyRow > 0 { moves.append(emptyTileIndex - boardSize) } // Tile above empty
        if emptyRow < boardSize - 1 { moves.append(emptyTileIndex + boardSize) } // Tile below empty
        if emptyCol > 0 { moves.append(emptyTileIndex - 1) } // Tile left of empty
        if emptyCol < boardSize - 1 { moves.append(emptyTileIndex + 1) } // Tile right of empty
        
        return moves
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let location = touch.location(in: self)
        
        // Handle settings panel touches first if it's visible
        if !settingsPanel.isHidden {
            let panelLocation = touch.location(in: settingsPanel)
            let touchedNodeInPanel = settingsPanel.atPoint(panelLocation)
            
            if let nodeName = touchedNodeInPanel.name {
                if nodeName.starts(with: "size_") {
                    let newSize = Int(nodeName.components(separatedBy: "_")[1])!
                    if boardSize != newSize {
                        boardSize = newSize
                        // Re-create panel to update selection state
                        settingsPanel.removeFromParent()
                        createSettingsPanel()
                        setupGame()
                    }
                } else if nodeName.starts(with: "color_") {
                    let colorName = nodeName.components(separatedBy: "_")[1]
                    let colors: [String: SKColor] = ["Black": .black, "Blue": .blue, "Gray": .darkGray]
                    self.backgroundColor = colors[colorName] ?? .black
                    // Re-create panel to update selection state
                    settingsPanel.removeFromParent()
                    createSettingsPanel()
                } else if nodeName == "back" {
                    toggleSettingsPanel(show: false)
                }
            }
            return // Absorb touches while settings are open
        }

        let touchedNode = atPoint(location)
        let parentNode = touchedNode.parent

        let nodeName = parentNode?.name ?? touchedNode.name

        if nodeName == "shuffle" {
            setupGame()
            return
        } else if nodeName == "settings" {
            toggleSettingsPanel(show: true)
            return
        } else if nodeName == "solve" {
            solvePuzzle()
            return
        }

        if gameWon { return }
        
        for i in 0..<tiles.count {
            if let tile = tiles[i], tile.contains(location) {
                if getValidMoves().contains(i) {
                    moveTile(at: i)
                    checkForWin()
                }
                break
            }
        }
    }

    func moveTile(at index: Int) {
        if let tile = tiles[index] {
            let emptyPosition = position(for: emptyTileIndex)
            tile.run(SKAction.move(to: emptyPosition, duration: 0.15))
            
            // Correctly swap the tiles in the model
            tiles.swapAt(index, emptyTileIndex)
            emptyTileIndex = index
            
            moves += 1
            movesLabel.text = "Moves: \(moves)"
        }
    }

    func checkForWin() {
        for i in 0..<(tiles.count - 1) {
            guard let tile = tiles[i], tile.name == "tile\(i+1)" else {
                return
            }
        }
        
        gameWon = true
        let winLabel = SKLabelNode(fontNamed: "Arial-BoldMT")
        winLabel.text = "You Win!"
        winLabel.name = "winLabel"
        winLabel.fontSize = 60
        winLabel.fontColor = .green
        winLabel.position = CGPoint(x: 0, y: 0)
        winLabel.zPosition = 100
        addChild(winLabel)
    }
    
    func solvePuzzle() {
        guard !gameWon else { return }
        
        // Disable user interaction during solve
        self.isUserInteractionEnabled = false
        
        // Create the initial state from the current board
        var boardArray: [Int] = []
        for tile in tiles {
            if let tileName = tile?.name, let number = Int(tileName.replacingOccurrences(of: "tile", with: "")) {
                boardArray.append(number)
            } else {
                boardArray.append(0) // 0 represents the empty space
            }
        }
        
        let initialState = PuzzleState(board: boardArray, size: boardSize, emptyTileIndex: emptyTileIndex)
        
        // Run solver on a background thread
        DispatchQueue.global(qos: .userInitiated).async {
            let solver = PuzzleSolver()
            if let solutionPath = solver.solve(initialState: initialState) {
                // Animate the solution on the main thread
                DispatchQueue.main.async {
                    self.animateSolution(path: solutionPath)
                }
            } else {
                // Re-enable interaction if no solution found
                DispatchQueue.main.async {
                    self.isUserInteractionEnabled = true
                    print("No solution found.")
                }
            }
        }
    }
    
    func animateSolution(path: [PuzzleState]) {
        var actions: [SKAction] = []
        
        for i in 1..<path.count {
            let previousState = path[i-1]
            let currentState = path[i]
            
            // Find which tile moved
            let movedTileIndex = currentState.emptyTileIndex
            let movedTileValue = previousState.board[movedTileIndex]
            
            // Find the SKNode for that tile
            if self.children.contains(where: { $0.name == "tile\(movedTileValue)" }) {
                let action = SKAction.run {
                    // Find the index of the tile to move in our `tiles` array
                    if let indexToMove = self.tiles.firstIndex(where: { $0?.name == "tile\(movedTileValue)" }) {
                        self.moveTile(at: indexToMove)
                    }
                }
                actions.append(action)
                actions.append(SKAction.wait(forDuration: 0.2)) // Wait between moves
            }
        }
        
        // Add a final action to re-enable user interaction
        let finalAction = SKAction.run {
            self.isUserInteractionEnabled = true
            self.checkForWin() // Check for win at the end
        }
        actions.append(finalAction)
        
        self.run(SKAction.sequence(actions))
    }
}
