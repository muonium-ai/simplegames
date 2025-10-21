import SpriteKit

class GameScene: SKScene {
    
    private var boardSize = 3
    private var tileSize: CGFloat = 0
    private var tiles: [SKSpriteNode?] = []
    private var emptyTileIndex: Int = 0
    private var gameWon = false

    override func didMove(to view: SKView) {
        setupGame()
    }

    func setupGame() {
        gameWon = false
        tileSize = size.width / CGFloat(boardSize)
        let totalTiles = boardSize * boardSize
        tiles = Array(repeating: nil, count: totalTiles)

        for i in 0..<(totalTiles - 1) {
            let tile = SKSpriteNode(color: .gray, size: CGSize(width: tileSize - 2, height: tileSize - 2))
            tile.name = "tile\(i+1)"
            
            let numberLabel = SKLabelNode(fontNamed: "Arial")
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
        let row = CGFloat(index / boardSize)
        let col = CGFloat(index % boardSize)
        let x = col * tileSize + tileSize / 2 - size.width / 2
        let y = size.height / 2 - (row * tileSize + tileSize / 2)
        return CGPoint(x: x, y: y)
    }

    func shuffle() {
        var lastMove: Int? = nil
        for _ in 0..<100 {
            let validMoves = getValidMoves()
            var randomMove: Int
            repeat {
                randomMove = validMoves.randomElement()!
            } while lastMove != nil && randomMove == lastMove!
            
            moveTile(at: randomMove)
            lastMove = emptyTileIndex
        }
    }

    func getValidMoves() -> [Int] {
        var moves: [Int] = []
        let emptyRow = emptyTileIndex / boardSize
        let emptyCol = emptyTileIndex % boardSize

        if emptyRow > 0 { moves.append(emptyTileIndex - boardSize) } // Up
        if emptyRow < boardSize - 1 { moves.append(emptyTileIndex + boardSize) } // Down
        if emptyCol > 0 { moves.append(emptyTileIndex - 1) } // Left
        if emptyCol < boardSize - 1 { moves.append(emptyTileIndex + 1) } // Right
        
        return moves
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard !gameWon, let touch = touches.first else { return }
        let location = touch.location(in: self)
        
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
            tile.run(SKAction.move(to: emptyPosition, duration: 0.1))
            
            tiles[emptyTileIndex] = tile
            tiles[index] = nil
            emptyTileIndex = index
        }
    }

    func checkForWin() {
        for i in 0..<(tiles.count - 1) {
            if tiles[i] == nil || tiles[i]!.name != "tile\(i+1)" {
                return
            }
        }
        
        gameWon = true
        let winLabel = SKLabelNode(fontNamed: "Arial")
        winLabel.text = "You Win!"
        winLabel.fontSize = 60
        winLabel.fontColor = .green
        winLabel.position = CGPoint(x: 0, y: 0)
        addChild(winLabel)
    }
}
