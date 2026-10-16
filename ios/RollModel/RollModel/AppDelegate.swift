import UIKit
import AVFoundation

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        GameAudio.configure()
        return true
    }

    func application(_ application: UIApplication,
                     configurationForConnecting connectingSceneSession: UISceneSession,
                     options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        let configuration = UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
        configuration.delegateClass = SceneDelegate.self
        return configuration
    }
}

/// Game sound mixes with whatever the player is listening to and follows the ring/silent switch, like most casual games.
enum GameAudio {

    /// Called when the game's sound needs a fresh start while the app is in front: a call, Siri or an alarm has ended,
    /// or the phone's audio system restarted.
    static var onRestart: (() -> Void)?
    private static var observers: [NSObjectProtocol] = []

    static func configure() {
        apply()
        let center = NotificationCenter.default
        observers.append(center.addObserver(forName: AVAudioSession.interruptionNotification, object: nil, queue: .main) { note in
            guard let raw = note.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
                  AVAudioSession.InterruptionType(rawValue: raw) == .ended else { return }
            GameAudio.reactivate()
            GameAudio.restartIfInFront()
        })
        observers.append(center.addObserver(forName: AVAudioSession.mediaServicesWereResetNotification, object: nil, queue: .main) { _ in
            GameAudio.apply()
            GameAudio.restartIfInFront()
        })
    }

    static func reactivate() {
        try? AVAudioSession.sharedInstance().setActive(true)
    }

    // (also after a rewarded ad, which may have changed it: AdsBridge)
    static func apply() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.ambient, mode: .default, options: [])
            try session.setActive(true)
        } catch {
            // Sound is a nice-to-have: the game still runs without it.
        }
    }

    // In the background the scene takes care of it when the app comes back.
    private static func restartIfInFront() {
        guard UIApplication.shared.applicationState == .active else { return }
        onRestart?()
    }
}
