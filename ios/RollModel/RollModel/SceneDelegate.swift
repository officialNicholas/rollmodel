import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        window.backgroundColor = GameViewController.backgroundColor
        window.rootViewController = GameViewController()
        window.makeKeyAndVisible()
        self.window = window
    }

    func sceneWillResignActive(_ scene: UIScene) {
        // A call, Control Center or the app switcher: pause the match so nothing happens while the player is away.
        gameController?.pauseGame()
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
        // Back from the home screen, a call or the app switcher: turn the audio session back on, then tell the game, which restarts its sound.
        GameAudio.reactivate()
        gameController?.resumeGame()
    }

    private var gameController: GameViewController? {
        window?.rootViewController as? GameViewController
    }
}
