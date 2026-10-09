import UIKit
import WebKit

/// Tells the game what it is running on, so it can pick its graphics level on its own: the chip generation, the memory,
/// Low Power Mode and how warm the phone is running. It keeps the game told when those change, and lets the game keep
/// the screen awake during a match.
///
/// The game reads this as window.__NATIVE (set before its own script runs) and listens for a "nativechange" event.
/// Any other shell (an Android one later) only has to provide the same two things.
final class DeviceBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "device"

    weak var webView: WKWebView?
    private var observers: [NSObjectProtocol] = []

    /// Runs at document start, before the game's script.
    static func startScript() -> String {
        return "window.__NATIVE = \(json(snapshot()));"
    }

    static func snapshot() -> [String: Any] {
        let info = ProcessInfo.processInfo
        let model = modelIdentifier()
        return [
            "platform": "ios",
            "model": model,
            "tier": tier(for: model, memory: info.physicalMemory),
            "memGB": (Double(info.physicalMemory) / 1_073_741_824.0 * 10).rounded() / 10,
            "lowPower": info.isLowPowerModeEnabled,
            "thermal": info.thermalState.rawValue,
            "maxFPS": UIScreen.main.maximumFramesPerSecond,
            "scale": Double(UIScreen.main.scale)
        ]
    }

    /// The hardware model, like "iPhone16,1". In the Simulator, the model being simulated.
    static func modelIdentifier() -> String {
        if let simulated = ProcessInfo.processInfo.environment["SIMULATOR_MODEL_IDENTIFIER"] {
            return simulated
        }
        var system = utsname()
        uname(&system)
        let bytes = Mirror(reflecting: system.machine).children.compactMap { $0.value as? Int8 }.filter { $0 != 0 }
        return String(decoding: bytes.map { UInt8(bitPattern: $0) }, as: UTF8.self)
    }

    /// 3: iPhone 14 Pro and newer (A16 on) or an M-series iPad. 2: iPhone 12 to 14 and SE (3rd gen) (A14, A15).
    /// 1: iPhone XS to 11 and SE (2nd gen) (A12, A13). 0: older. Under 3.5 GB of memory caps it at 1.
    static func tier(for model: String, memory: UInt64) -> Int {
        let digits = model.split(whereSeparator: { !$0.isNumber })
        let major = Int(digits.first ?? "") ?? 0
        var tier: Int
        if model.hasPrefix("iPhone") {
            tier = major >= 15 ? 3 : major >= 13 ? 2 : major >= 11 ? 1 : 0
        } else if model.hasPrefix("iPad") {
            tier = major >= 13 ? 3 : major >= 11 ? 2 : major >= 8 ? 1 : 0
        } else {
            tier = 3 // a Mac running the iPhone app, or hardware newer than this list
        }
        if memory < 3_500_000_000 {
            tier = min(tier, 1)
        }
        return tier
    }

    func startObserving() {
        let center = NotificationCenter.default
        let push: (Notification) -> Void = { [weak self] _ in self?.pushState() }
        observers.append(center.addObserver(forName: Notification.Name.NSProcessInfoPowerStateDidChange, object: nil, queue: .main, using: push))
        observers.append(center.addObserver(forName: ProcessInfo.thermalStateDidChangeNotification, object: nil, queue: .main, using: push))
    }

    deinit {
        observers.forEach { NotificationCenter.default.removeObserver($0) }
    }

    /// Low Power Mode or the phone's temperature changed: tell the game, so it can ease off (or come back up).
    private func pushState() {
        let info = ProcessInfo.processInfo
        let update = json(["lowPower": info.isLowPowerModeEnabled, "thermal": info.thermalState.rawValue])
        let script = "if (window.__NATIVE) { Object.assign(window.__NATIVE, \(update)); } window.dispatchEvent(new CustomEvent('nativechange'));"
        webView?.evaluateJavaScript(script, completionHandler: nil)
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any] else { return }
        if let awake = body["keepAwake"] as? Bool {
            // The screen stays on while a match is being played, and sleeps as usual everywhere else.
            UIApplication.shared.isIdleTimerDisabled = awake
        }
    }
}

private func json(_ value: [String: Any]) -> String {
    guard let data = try? JSONSerialization.data(withJSONObject: value), let text = String(data: data, encoding: .utf8) else {
        return "{}"
    }
    return text
}
