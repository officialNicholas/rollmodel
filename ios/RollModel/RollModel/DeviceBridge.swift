import StoreKit
import UIKit
import WebKit

/// Tells the game what it is running on, so it can pick its graphics level on its own: the chip generation, the memory,
/// Low Power Mode and how warm the phone is running. It keeps the game told when those change, lets the game keep
/// the screen awake during a match, opens the share sheet for the game (a friend code), and puts up the App Store's
/// rating prompt when the game asks.
///
/// The game reads this as window.__NATIVE (set before its own script runs) and listens for a "nativechange" event.
/// Any other shell (an Android one later) only has to provide the same two things.
final class DeviceBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "device"

    weak var webView: WKWebView?
    private var observers: [NSObjectProtocol] = []

    /// Runs at document start, before the game's script. (An iPad turns freely and its windows can take any shape, so there the
    /// game never asks for the device to be turned; anywhere else the game decides that from its own shape.) The scale and refresh
    /// rate come from the game's view and its screen (0 when not known yet), never the main screen: on iPhone Duo there are two.
    static func startScript(scale: CGFloat, maxFPS: Int) -> String {
        let pad = UIDevice.current.userInterfaceIdiom == .pad ? " window.__noRotate = true;" : ""
        return "window.__NATIVE = \(json(snapshot(scale: scale, maxFPS: maxFPS)));" + pad
    }

    static func snapshot(scale: CGFloat, maxFPS: Int) -> [String: Any] {
        let info = ProcessInfo.processInfo
        let model = modelIdentifier()
        return [
            "platform": "ios",
            "model": model,
            "tier": tier(for: model, memory: info.physicalMemory),
            "memGB": (Double(info.physicalMemory) / 1_073_741_824.0 * 10).rounded() / 10,
            "lowPower": info.isLowPowerModeEnabled,
            "thermal": info.thermalState.rawValue,
            "maxFPS": maxFPS,
            "scale": Double(scale),
            "share": true,
            "kb": 0,    // (how much of the screen the keyboard covers: the game view keeps this told, with a "nativekeyboard" event)
            "tester": isDebugBuild,
            "appVersion": (Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String) ?? ""
        ]
    }

    /// Run from Xcode (a debug build): the game keeps its test unlocks. A TestFlight or App Store build has none, since App Review
    /// installs look just like TestFlight ones and the reviewers must see the game as players will.
    static var isDebugBuild: Bool {
        #if DEBUG
        return true
        #else
        return false
        #endif
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
        foldTimer?.invalidate()
    }

    // MARK: iPhone Duo's fold

    private var foldTimer: Timer?
    private var sentFold: String?

    /// Whether this iOS can say where a fold runs (UIView's reserved regions, iOS 27.1 on).
    static var canReadFold: Bool {
        return UIView.instancesRespond(to: NSSelectorFromString("reservedRegionsOfKind:options:"))
            && NSClassFromString("UIViewReservedRegionKind") != nil
    }

    /// Where the fold runs across the game while iPhone Duo is partly folded, in the page's own units (points), so the game keeps its
    /// boxes and words to one side of it: {"axis": "v" (down the screen) or "h" (across it), "a" and "b" (where the strip starts and
    /// ends along that axis, its margins for touch included), "w", "h" (the game's size)}. "null" when there's no fold to keep clear of:
    /// open flat, closed, or any other phone. Read through the Objective-C runtime, so the app still builds with an SDK without it.
    static func foldJSON(in view: UIView) -> String {
        guard canReadFold, let kinds = NSClassFromString("UIViewReservedRegionKind"),
              let division = (kinds as AnyObject).duoDivisionKind as AnyObject?,
              let regions = (view as AnyObject).duoReservedRegions?(ofKind: division, options: 0) else { return "null" }
        let size = view.bounds.size
        for region in regions {
            guard let item = region as? NSObject,
                  (item.value(forKey: "active") as? Bool) == true,
                  let frame = (item.value(forKey: "frame") as? NSValue)?.cgRectValue else { continue }
            let rect = frame.intersection(view.bounds)
            guard !rect.isNull, rect.width > 0 || rect.height > 0 else { continue }
            let down = rect.height >= rect.width
            return json(["axis": down ? "v" : "h",
                         "a": Double(down ? rect.minX : rect.minY), "b": Double(down ? rect.maxX : rect.maxY),
                         "w": Double(size.width), "h": Double(size.height)])
        }
        return "null"
    }

    /// Keeps the game told where the fold is: checked twice a second (nothing says when the phone's bent), sent only when it changes.
    func watchFold() {
        guard foldTimer == nil, DeviceBridge.canReadFold else { return }
        let timer = Timer(timeInterval: 0.5, repeats: true) { [weak self] _ in self?.pushFold() }
        timer.tolerance = 0.2
        RunLoop.main.add(timer, forMode: .common)
        foldTimer = timer
    }

    /// Tells the game where the fold is now, if that's changed (or always, for a page that has just loaded).
    func pushFold(force: Bool = false) {
        guard DeviceBridge.canReadFold, let view = webView, view.window != nil else { return }
        let fold = DeviceBridge.foldJSON(in: view)
        if !force && fold == sentFold { return }
        sentFold = fold
        let script = "window.__NATIVE = window.__NATIVE || {}; window.__NATIVE.fold = \(fold); window.dispatchEvent(new CustomEvent('nativefold'));"
        view.evaluateJavaScript(script, completionHandler: nil)
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
        if let text = body["share"] as? String, !text.isEmpty, text.count <= 300 {
            share(text)
        }
        if (body["review"] as? Bool) == true {
            requestReview()
        }
    }

    /// The App Store's rating prompt, which the game asks for back in the lobby after a win. iOS decides whether it shows (at
    /// most three times a year, and never in a TestFlight build).
    private func requestReview() {
        Task { @MainActor [weak self] in
            guard let scene = self?.webView?.window?.windowScene, scene.activationState == .foregroundActive else { return }
            if #available(iOS 16.0, *) {
                AppStore.requestReview(in: scene)
            } else {
                SKStoreReviewController.requestReview(in: scene)
            }
        }
    }

    /// The system share sheet (Messages, AirDrop, Copy...) for a line of text from the game: your friend code.
    private func share(_ text: String) {
        guard let view = webView, let root = view.window?.rootViewController else { return }
        var host = root
        while let shown = host.presentedViewController, !shown.isBeingDismissed { host = shown }
        if host is UIActivityViewController { return } // (one open at a time)
        let sheet = UIActivityViewController(activityItems: [text], applicationActivities: nil)
        if let pop = sheet.popoverPresentationController { // (an iPad shows it as a popover, from the middle of the screen)
            pop.sourceView = view
            pop.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.midY, width: 1, height: 1)
            pop.permittedArrowDirections = []
        }
        host.present(sheet, animated: true)
    }
}

private func json(_ value: [String: Any]) -> String {
    guard let data = try? JSONSerialization.data(withJSONObject: value), let text = String(data: data, encoding: .utf8) else {
        return "{}"
    }
    return text
}

/// iOS 27.1's reserved regions as Objective-C knows them (UIView's reservedRegionsOfKind:options: and UIViewReservedRegionKind's
/// divisionRegionKind), called by name so the app builds with any SDK; they're only called where the phone has them.
@objc private protocol DuoReservedRegions {
    @objc(reservedRegionsOfKind:options:) func duoReservedRegions(ofKind kind: AnyObject, options: UInt) -> [AnyObject]
    @objc(divisionRegionKind) var duoDivisionKind: AnyObject { get }
}
