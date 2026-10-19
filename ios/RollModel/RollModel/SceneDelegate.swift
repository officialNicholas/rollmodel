import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?
    private var wasInBackground = false

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        window.backgroundColor = GameViewController.backgroundColor
        window.rootViewController = GameViewController()
        window.makeKeyAndVisible()
        self.window = window
        GameAudio.onRestart = { [weak self] in self?.gameController?.restartSound() }
    }

    func sceneWillResignActive(_ scene: UIScene) {
        // A call, Control Center or the app switcher: pause the match so nothing happens while the player is away.
        gameController?.pauseGame()
    }

    func sceneDidEnterBackground(_ scene: UIScene) {
        wasInBackground = true
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
        // Back from the home screen, a call or the app switcher: turn the audio session back on, then tell the game, which restarts its sound
        // (from the background on a fresh start, since iOS can hand the page its old sound back stuck).
        let away = wasInBackground
        wasInBackground = false
        GameAudio.reactivate { [weak self] in
            self?.gameController?.resumeGame(afterBackground: away)
        }
    }

    private var gameController: GameViewController? {
        window?.rootViewController as? GameViewController
    }
}
