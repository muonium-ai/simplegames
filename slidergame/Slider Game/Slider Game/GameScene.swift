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
    private var shuffleButton: SKLabelNode!

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

        // Shuffle button
        shuffleButton = SKLabelNode(fontNamed: "Arial-BoldMT")
        shuffleButton.text = "Shuffle"
        shuffleButton.fontSize = 30
        shuffleButton.fontColor = .white
        shuffleButton.position = CGPoint(x: 0, y: -size.height/2 + 50)
        shuffleButton.name = "shuffle"
        addChild(shuffleButton)
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
            tile.texture = SKTexture(imageNamed: "tile_bg") // Using a texture for better visuals
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

        shuffle()
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

    func shuffle() {
        // Using Random-Walk Scramble from PRD
        var lastMove: Int? = nil
        for _ in 0..<100 {
            let validMoves = getValidMoves()
            var movableTiles = validMoves.map { $0 }
            
            // Avoid immediate backtracks to increase variety
            if let last = lastMove, let backTrackIndex = movableTiles.firstIndex(of: last) {
                movableTiles.remove(at: backTrackIndex)
            }
            
            guard let randomTileIndex = movableTiles.randomElement() else { continue }
            
            // We are moving the tile *into* the empty space.
            // The index of the tile to move is `randomTileIndex`.
            // The empty space is at `emptyTileIndex`.
            let tileToMove = tiles[randomTileIndex]
            tiles[emptyTileIndex] = tileToMove
            tiles[randomTileIndex] = nil
            
            lastMove = emptyTileIndex // The new empty spot is where the tile was
            emptyTileIndex = randomTileIndex
        }
        
        // After shuffling, update visual positions without animation
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
        let touchedNode = atPoint(location)

        if touchedNode.name == "shuffle" {
            setupGame()
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
            
            tiles[emptyTileIndex] = tile
            tiles[index] = nil
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
}
