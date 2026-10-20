import UIKit
import AVFoundation
import UserNotifications

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        GameAudio.configure()
        // A shake mid-game is part of playing: it mustn't bring up "Undo Typing" once a name has been typed.
        application.applicationSupportsShakeToEdit = false
        // Notifications: none over the game while it's open, and a tapped party invite opens the game on it (set before launch
        // finishes, so the tap that opened the app is heard).
        UNUserNotificationCenter.current().delegate = NotifyCenter.shared
        return true
    }

    // This phone's address for notifications (asked for only once the player has said yes to them): the game keeps it with their
    // account, so a friend's party invite reaches them with the game closed.
    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        NotifyBridge.tokenArrived(deviceToken)
    }

    // No address (no network, or the app isn't signed for notifications): invites still reach the game while it's open.
    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
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
/// Turning the audio session on can keep the caller waiting while the phone's audio system is busy, so every change to it is made
/// on the session's own queue, never the main thread (the screen doesn't wait on it); whatever must follow runs on the main thread once it's done.
enum GameAudio {

    /// Called when the game's sound needs a fresh start while the app is in front: a call, Siri or an alarm has ended,
    /// or the phone's audio system restarted.
    static var onRestart: (() -> Void)?
    private static var observers: [NSObjectProtocol] = []
    /// The session's changes, one after another and off the main thread.
    private static let queue = DispatchQueue(label: "rollmodel.audio-session", qos: .userInitiated)

    static func configure() {
        apply()
        let center = NotificationCenter.default
        observers.append(center.addObserver(forName: AVAudioSession.interruptionNotification, object: nil, queue: .main) { note in
            guard let raw = note.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
                  AVAudioSession.InterruptionType(rawValue: raw) == .ended else { return }
            GameAudio.reactivate { GameAudio.restartIfInFront() }
        })
        observers.append(center.addObserver(forName: AVAudioSession.mediaServicesWereResetNotification, object: nil, queue: .main) { _ in
            GameAudio.apply { GameAudio.restartIfInFront() }
        })
    }

    /// Turns the session back on; `done` then runs on the main thread.
    static func reactivate(then done: (() -> Void)? = nil) {
        queue.async {
            try? AVAudioSession.sharedInstance().setActive(true)
            if let done = done { DispatchQueue.main.async(execute: done) }
        }
    }

    // (also after a rewarded ad, which may have changed it: AdsBridge)
    static func apply(then done: (() -> Void)? = nil) {
        queue.async {
            let session = AVAudioSession.sharedInstance()
            do {
                try session.setCategory(.ambient, mode: .default, options: [])
                try session.setActive(true)
            } catch {
                // Sound is a nice-to-have: the game still runs without it.
            }
            if let done = done { DispatchQueue.main.async(execute: done) }
        }
    }

    // In the background the scene takes care of it when the app comes back.
    private static func restartIfInFront() {
        guard UIApplication.shared.applicationState == .active else { return }
        onRestart?()
    }
}
