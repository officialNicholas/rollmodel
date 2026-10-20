import UIKit
import WebKit

/// The player picks upright or wide play when the game first opens, and can change it in Settings. The game posts that choice
/// here as "port", "land" or "" (no preference), and a phone-shaped screen turns to match. A roomy one (iPhone Duo open or closed,
/// an iPad, a resizable window) turns freely instead: either way round suits it, so the game takes whatever shape it's given.
/// The choice is kept, so the next launch opens the way the player plays instead of turning once the game has loaded.
final class OrientBridge: NSObject, WKScriptMessageHandler {

    /// Whether this view turns freely: its window is near square (long side under 1.6 times the short one), or it's an iPad, whose
    /// windows take any shape whichever way it's held. Decided from the space the game has, not the kind of device, and asked again
    /// whenever that changes. (The game's own page makes the same call from the same shape.)
    static func turnsFreely(_ viewController: UIViewController) -> Bool {
        if viewController.traitCollection.userInterfaceIdiom == .pad { return true }
        guard let view = viewController.viewIfLoaded else { return false }
        let size = view.window?.bounds.size ?? view.bounds.size
        let short = min(size.width, size.height), long = max(size.width, size.height)
        return short > 0 && long / short < 1.6
    }

    static let messageName = "orient"
    /// The player's last choice, kept in the app's own settings.
    private static let savedKey = "rollmodel.orient"

    weak var viewController: UIViewController?
    weak var webView: WKWebView?

    /// The way the phone is physically held, told to the game as 'nativeturn' ({ way: "port" | "land" }) once it has been held
    /// still that way for half a second (flat on a table, face up or down, says nothing). The screen itself stays locked to the
    /// player's choice: the game asks whether to switch, on its main menu only. With Rotation Lock on, iOS reports no turns.
    private var lastTurn = ""
    private var pendingTurn: DispatchWorkItem?

    func watchTurns() {
        UIDevice.current.beginGeneratingDeviceOrientationNotifications()
        NotificationCenter.default.addObserver(self, selector: #selector(deviceTurned), name: UIDevice.orientationDidChangeNotification, object: nil)
    }

    @objc private func deviceTurned() {
        let way: String
        switch UIDevice.current.orientation {
        case .portrait: way = "port"
        case .landscapeLeft, .landscapeRight: way = "land"
        default: return
        }
        pendingTurn?.cancel()
        let work = DispatchWorkItem { [weak self] in
            guard let self = self, way != self.lastTurn else { return }
            self.lastTurn = way
            self.webView?.evaluateJavaScript("window.dispatchEvent(new CustomEvent('nativeturn', { detail: { way: '\(way)' } }));", completionHandler: nil)
        }
        pendingTurn = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5, execute: work)
    }

    /// What the iPhone may turn to: the player's last choice, upright until there is one.
    private(set) var mask: UIInterfaceOrientationMask = OrientBridge.allowed(for: UserDefaults.standard.string(forKey: OrientBridge.savedKey) ?? "port")

    private static func allowed(for choice: String) -> UIInterfaceOrientationMask {
        return choice == "land" ? .landscape : (choice == "port" ? .portrait : .allButUpsideDown)
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        let choice = message.body as? String ?? ""
        if UserDefaults.standard.string(forKey: OrientBridge.savedKey) != choice {
            UserDefaults.standard.set(choice, forKey: OrientBridge.savedKey)
        }
        let next = OrientBridge.allowed(for: choice)
        guard next != mask else { return }
        mask = next
        guard let viewController = viewController, !OrientBridge.turnsFreely(viewController) else { return }
        if #available(iOS 16.0, *) {
            viewController.setNeedsUpdateOfSupportedInterfaceOrientations()
            viewController.view.window?.windowScene?.requestGeometryUpdate(.iOS(interfaceOrientations: next)) { _ in
                // Refused (say the player has Rotation Lock on): the game shows its "turn your phone" card instead.
            }
        } else {
            // iOS 15: turn the device's orientation, then let UIKit settle on what the controller now allows.
            if choice == "land" || choice == "port" {
                let target: UIInterfaceOrientation = choice == "land" ? .landscapeRight : .portrait
                UIDevice.current.setValue(target.rawValue, forKey: "orientation")
            }
            UIViewController.attemptRotationToDeviceOrientation()
        }
    }
}
