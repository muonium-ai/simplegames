//
//  GameViewController.swift
//  super 2048
//
//  Created by Senthil Nayagam on 19/10/25.
//

import UIKit
import SpriteKit

final class GameViewController: UIViewController {

    private weak var gameScene: GameScene?
    private let keyCommandMapping: [(direction: MoveDirection, input: String, title: String)] = [
        (direction: .up, input: UIKeyCommand.inputUpArrow, title: "Move Up"),
        (direction: .right, input: UIKeyCommand.inputRightArrow, title: "Move Right"),
        (direction: .down, input: UIKeyCommand.inputDownArrow, title: "Move Down"),
        (direction: .left, input: UIKeyCommand.inputLeftArrow, title: "Move Left")
    ]

    override func viewDidLoad() {
        super.viewDidLoad()
        presentScene()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        becomeFirstResponder()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        resignFirstResponder()
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        if let skView = view as? SKView, let scene = skView.scene {
            scene.size = skView.bounds.size
        }
    }

    private func presentScene() {
        guard let skView = view as? SKView else { return }
        let scene = GameScene(size: skView.bounds.size)
        scene.scaleMode = .resizeFill
        skView.presentScene(scene)
        skView.ignoresSiblingOrder = true
        gameScene = scene
    }

    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        if UIDevice.current.userInterfaceIdiom == .phone {
            return .allButUpsideDown
        } else {
            return .all
        }
    }

    override var prefersStatusBarHidden: Bool {
        return true
    }

    override var canBecomeFirstResponder: Bool {
        return true
    }

    override var keyCommands: [UIKeyCommand]? {
        return keyCommandMapping.map { mapping in
            let command = UIKeyCommand(input: mapping.input, modifierFlags: [], action: #selector(handleArrowKeyCommand(_:)))
            command.discoverabilityTitle = mapping.title
            return command
        }
    }

    @objc private func handleArrowKeyCommand(_ sender: UIKeyCommand) {
        guard let input = sender.input,
              let mapping = keyCommandMapping.first(where: { $0.input == input }) else {
            return
        }
        gameScene?.handleExternalInput(mapping.direction)
    }
}
