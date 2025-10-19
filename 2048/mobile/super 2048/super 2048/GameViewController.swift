//
//  GameViewController.swift
//  super 2048
//
//  Created by Senthil Nayagam on 19/10/25.
//

import UIKit
import SpriteKit

final class GameViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        presentScene()
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
#if DEBUG
        skView.showsFPS = true
        skView.showsNodeCount = true
#endif
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
}
