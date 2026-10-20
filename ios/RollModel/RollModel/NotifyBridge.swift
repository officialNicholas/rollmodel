import UIKit
import UserNotifications
import WebKit

/// Notifications from the app.
///
/// A nudge when something the game is making is done (a stroke being crafted): the game asks the player first, in its own words,
/// and only if they say yes does iOS ask for permission; after that each craft that's long enough schedules one, and it's called off
/// when the craft is finished in the game.
///
/// Party invites while the game is closed (v391): once the player has said yes to notifications (for either), the app registers
/// for remote notifications and hands the game its device token, which the game keeps with the player's account; the game server
/// sends an invite to it through Apple's push service. Tapping an invite opens the game on that invite.
///
/// The game posts here as "notify":
/// - {status: true} for whether notifications are allowed (also: the page is ready, so a tapped invite waiting is handed over);
/// - {ask: true} for iOS's own permission prompt (iOS shows it once at most);
/// - {id, at, title, body} to schedule one for `at` (ms since 1970). A new one with the same id replaces it;
/// - {cancel: id} when it's no longer wanted.
///
/// It hears back through a "nativenotify" window event: {status: "allowed" | "denied" | "ask"} ("ask": not asked yet);
/// {token, env} with this phone's device token (hex) and "development" (an app run from Xcode) or "production";
/// {open: {k: "invite", id}} when the player tapped a party invite.
/// A notification that comes in while the game is open isn't shown (the game shows its own).
final class NotifyBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "notify"
    private static let prefix = "rollmodel."

    /// The bridge of the game on screen, for the app delegate (the device token, a tapped notification).
    static weak var current: NotifyBridge?
    /// A tapped invite that came before the game's page was ready (the app was closed): handed over when it asks for the status.
    private static var pendingOpen: [String: Any]?

    weak var webView: WKWebView? {
        didSet { NotifyBridge.current = self }
    }
    private var pageReady = false
    private var lastToken: String?

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any] else { return }
        if (body["status"] as? Bool) == true { pageReady = true; sendStatus(); flushOpen() }
        if (body["ask"] as? Bool) == true { ask() }
        if let id = body["cancel"] as? String, !id.isEmpty { cancel(id) }
        if let id = body["id"] as? String, !id.isEmpty, let at = (body["at"] as? NSNumber)?.doubleValue {
            schedule(id: id, at: at, title: body["title"] as? String ?? "", text: body["body"] as? String ?? "")
        }
    }

    /// The page started over (a reload): it asks for the status again before anything is handed to it.
    func pageWillLoad() { pageReady = false }

    private func ask() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { [weak self] _, _ in
            DispatchQueue.main.async { self?.sendStatus() }
        }
    }

    private func sendStatus() {
        UNUserNotificationCenter.current().getNotificationSettings { [weak self] settings in
            let status: String
            switch settings.authorizationStatus {
            case .authorized, .provisional, .ephemeral:
                status = "allowed"
            case .denied:
                status = "denied"
            default:
                status = "ask"
            }
            DispatchQueue.main.async {
                self?.send(["status": status])
                // only once the player has said yes: the device token comes back to the app delegate, then to the game
                if status == "allowed" { UIApplication.shared.registerForRemoteNotifications() }
            }
        }
    }

    // ---- remote notifications (called on the main thread by the app delegate)

    /// This phone's address for notifications, for the game to keep with the player's account.
    static func tokenArrived(_ deviceToken: Data) {
        let hex = deviceToken.map { String(format: "%02x", $0) }.joined()
        #if DEBUG
        let env = "development"
        #else
        let env = "production"
        #endif
        guard let bridge = current else { return }
        bridge.lastToken = hex
        bridge.send(["token": hex, "env": env])
    }

    /// A tapped party invite: the game opens on it (now, or once its page is ready).
    static func openInvite(_ id: String) {
        guard !id.isEmpty, id.count <= 64 else { return }
        pendingOpen = ["k": "invite", "id": id]
        current?.flushOpen()
    }

    private func flushOpen() {
        guard pageReady, let open = NotifyBridge.pendingOpen else { return }
        NotifyBridge.pendingOpen = nil
        send(["open": open])
    }

    // ---- local nudges

    private func schedule(id: String, at: Double, title: String, text: String) {
        guard at.isFinite, !text.isEmpty else { return }
        let seconds = at / 1000 - Date().timeIntervalSince1970
        guard seconds > 5, seconds < 7 * 24 * 3600 else { return }
        let content = UNMutableNotificationContent()
        content.title = String(title.prefix(80))
        content.body = String(text.prefix(200))
        content.sound = .default
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: seconds, repeats: false)
        let request = UNNotificationRequest(identifier: NotifyBridge.prefix + id, content: content, trigger: trigger)
        UNUserNotificationCenter.current().add(request, withCompletionHandler: nil)
    }

    private func cancel(_ id: String) {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: [NotifyBridge.prefix + id])
        center.removeDeliveredNotifications(withIdentifiers: [NotifyBridge.prefix + id])
    }

    private func send(_ detail: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: detail), let text = String(data: data, encoding: .utf8) else { return }
        webView?.evaluateJavaScript("window.dispatchEvent(new CustomEvent('nativenotify', { detail: \(text) }));", completionHandler: nil)
    }
}

/// What the app does with notifications as they come and when they're tapped (set as the notification center's delegate at launch,
/// so a tap that opens the app is heard too).
final class NotifyCenter: NSObject, UNUserNotificationCenterDelegate {

    static let shared = NotifyCenter()

    // In front: none is shown over the game (an invite shows as the game's own card; a craft's nudge is said in the game).
    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([])
    }

    // Tapped: a party invite opens the game on it.
    func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        let info = response.notification.request.content.userInfo
        if let rm = info["rm"] as? [String: Any], (rm["k"] as? String) == "invite", let id = rm["id"] as? String {
            DispatchQueue.main.async { NotifyBridge.openInvite(id) }
        }
        completionHandler()
    }
}
