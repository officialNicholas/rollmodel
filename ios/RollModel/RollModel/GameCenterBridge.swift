import GameKit
import UIKit
import WebKit

/// Game Center: the player signed in from the lobby (the game picks the moment: never mid-match, never in the first lesson),
/// each Time trial's score on that canvas's Game Center leaderboard, and Game Center's own view of a leaderboard when the
/// player asks for it on the game's Time trial board.
///
/// It needs the Game Center capability on the app (Xcode: Signing & Capabilities) and the leaderboards made in App Store Connect,
/// one per canvas, named "rm.trial." and the canvas's id (see the iOS README). Until then sign-in fails quietly and the game shows
/// nothing of it.
///
/// The game posts here as "gamecenter":
/// - {start: true} once it's in the lobby (once a launch);
/// - {board, score} to put a score on a leaderboard;
/// - {show: board} to open Game Center on that leaderboard.
///
/// It hears back through a "nativegc" window event: {signedIn, boards} (the leaderboards made for the game, by id).
final class GameCenterBridge: NSObject, WKScriptMessageHandler, GKGameCenterControllerDelegate {

    static let messageName = "gamecenter"

    weak var webView: WKWebView?
    weak var viewController: UIViewController?
    private var started = false

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any] else { return }
        if (body["start"] as? Bool) == true { start() }
        if let board = body["board"] as? String, !board.isEmpty, let score = (body["score"] as? NSNumber)?.intValue {
            submit(score, to: board)
        }
        if let board = body["show"] as? String, !board.isEmpty { show(board) }
    }

    /// Signs the player in. Not signed in to Game Center on this phone: Game Center's own sign-in comes up over the lobby, once.
    private func start() {
        guard !started else { return }
        started = true
        GKLocalPlayer.local.authenticateHandler = { [weak self] signIn, _ in
            DispatchQueue.main.async {
                guard let self = self else { return }
                if let signIn = signIn {
                    self.topController()?.present(signIn, animated: true)
                    return
                }
                self.sendState()
            }
        }
    }

    /// Whether the player is signed in, and which leaderboards the game has (so it only offers one that's there).
    private func sendState() {
        guard GKLocalPlayer.local.isAuthenticated else {
            send(["signedIn": false, "boards": [String]()])
            return
        }
        GKLeaderboard.loadLeaderboards(IDs: nil) { [weak self] boards, _ in
            let ids = (boards ?? []).map { $0.baseLeaderboardID }
            DispatchQueue.main.async { self?.send(["signedIn": true, "boards": ids]) }
        }
    }

    private func submit(_ score: Int, to board: String) {
        guard GKLocalPlayer.local.isAuthenticated, score >= 0 else { return }
        GKLeaderboard.submitScore(score, context: 0, player: GKLocalPlayer.local, leaderboardIDs: [board]) { _ in }
    }

    private func show(_ board: String) {
        guard GKLocalPlayer.local.isAuthenticated, let host = topController() else { return }
        if host is GKGameCenterViewController { return } // (one open at a time)
        let view = GKGameCenterViewController(leaderboardID: board, playerScope: .global, timeScope: .allTime)
        view.gameCenterDelegate = self
        host.present(view, animated: true)
    }

    func gameCenterViewControllerDidFinish(_ gameCenterViewController: GKGameCenterViewController) {
        gameCenterViewController.dismiss(animated: true)
    }

    /// The controller on top (the game, or whatever it has up), to present Game Center's screens from.
    private func topController() -> UIViewController? {
        guard var top = viewController ?? webView?.window?.rootViewController else { return nil }
        while let shown = top.presentedViewController, !shown.isBeingDismissed { top = shown }
        return top
    }

    private func send(_ detail: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: detail), let text = String(data: data, encoding: .utf8) else { return }
        webView?.evaluateJavaScript("window.dispatchEvent(new CustomEvent('nativegc', { detail: \(text) }));", completionHandler: nil)
    }
}
