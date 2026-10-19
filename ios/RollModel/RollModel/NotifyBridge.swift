import UIKit
import UserNotifications
import WebKit

/// A nudge when something the game is making is done (a stroke being crafted), as a notification from the app. The game asks
/// the player first, in its own words, and only if they say yes does iOS ask for permission; after that each craft that's long
/// enough schedules one, and it's called off when the craft is finished in the game.
///
/// The game posts here as "notify":
/// - {status: true} for whether notifications are allowed;
/// - {ask: true} for iOS's own permission prompt (iOS shows it once at most);
/// - {id, at, title, body} to schedule one for `at` (ms since 1970). A new one with the same id replaces it;
/// - {cancel: id} when it's no longer wanted.
///
/// It hears back through a "nativenotify" window event: {status: "allowed" | "denied" | "ask"} ("ask": not asked yet).
/// A nudge that comes due while the game is open isn't shown (the game says so itself).
final class NotifyBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "notify"
    private static let prefix = "rollmodel."

    weak var webView: WKWebView?

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any] else { return }
        if (body["status"] as? Bool) == true { sendStatus() }
        if (body["ask"] as? Bool) == true { ask() }
        if let id = body["cancel"] as? String, !id.isEmpty { cancel(id) }
        if let id = body["id"] as? String, !id.isEmpty, let at = (body["at"] as? NSNumber)?.doubleValue {
            schedule(id: id, at: at, title: body["title"] as? String ?? "", text: body["body"] as? String ?? "")
        }
    }

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
            DispatchQueue.main.async { self?.send(["status": status]) }
        }
    }

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
