import UIKit
import WebKit

/// Hosts the game full screen. The game itself is the bundled web build in the Game folder, served offline.
final class GameViewController: UIViewController {

    static let backgroundColor = UIColor(red: 18.0 / 255.0, green: 10.0 / 255.0, blue: 36.0 / 255.0, alpha: 1.0)

    private let haptics = HapticsBridge()
    private let device = DeviceBridge()
    private let orient = OrientBridge()
    private let saves = SaveBridge()
    private let ads = AdsBridge()
    private var webView: WKWebView!
    private var lastReload = Date.distantPast
    private var reloadWhenActive = false

    override func loadView() {
        let contentController = WKUserContentController()
        contentController.addUserScript(WKUserScript(source: HapticsBridge.script,
                                                     injectionTime: .atDocumentStart,
                                                     forMainFrameOnly: true))
        contentController.add(haptics, name: HapticsBridge.messageName)
        // The game picks its graphics level from what this phone is (and eases off in Low Power Mode or when it runs hot).
        contentController.addUserScript(WKUserScript(source: DeviceBridge.startScript(),
                                                     injectionTime: .atDocumentStart,
                                                     forMainFrameOnly: true))
        contentController.add(device, name: DeviceBridge.messageName)
        // Upright or wide: the player's choice (asked when the game first opens, changed in Settings) turns the iPhone to match.
        contentController.add(orient, name: OrientBridge.messageName)
        // A copy of the save in the app's own files, put back if the web view's storage loses it.
        contentController.add(saves, name: SaveBridge.messageName)
        // Rewarded ads, only when the player asks for one: Skip on a stroke being crafted plays one (Google AdMob).
        contentController.addUserScript(WKUserScript(source: AdsBridge.startScript,
                                                     injectionTime: .atDocumentStart,
                                                     forMainFrameOnly: true))
        contentController.add(ads, name: AdsBridge.messageName)

        let configuration = WKWebViewConfiguration()
        configuration.userContentController = contentController
        configuration.setURLSchemeHandler(GameSchemeHandler(), forURLScheme: GameSchemeHandler.scheme)
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []
        configuration.websiteDataStore = WKWebsiteDataStore.default()

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.isOpaque = false
        webView.backgroundColor = GameViewController.backgroundColor
        webView.scrollView.backgroundColor = GameViewController.backgroundColor
        webView.scrollView.isScrollEnabled = false
        webView.scrollView.bounces = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.underPageBackgroundColor = GameViewController.backgroundColor
        webView.allowsLinkPreview = false
        webView.allowsBackForwardNavigationGestures = false
        webView.navigationDelegate = self
        #if DEBUG
        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }
        #endif

        self.webView = webView
        device.webView = webView
        device.startObserving()
        orient.viewController = self
        ads.webView = webView
        ads.viewController = self
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        // Typing a name can leave the page pushed up once the keyboard has gone: put it back.
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardDidHide),
                                               name: UIResponder.keyboardDidHideNotification, object: nil)
        loadGame()
    }

    @objc private func keyboardDidHide() {
        webView?.scrollView.setContentOffset(.zero, animated: false)
    }

    /// The phone is short of memory: the game lets go of the songs it isn't playing, so iOS is less likely to close it.
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        webView?.evaluateJavaScript("window.dispatchEvent(new Event('nativememory'));", completionHandler: nil)
    }

    private func loadGame() {
        webView.load(URLRequest(url: GameSchemeHandler.startURL))
    }

    /// The game already pauses itself when its window loses focus, so this just tells it that happened.
    func pauseGame() {
        webView?.evaluateJavaScript("window.dispatchEvent(new Event('blur'));", completionHandler: nil)
    }

    /// The app is in front again: the game's sound may have been cut off while it was away, so it gets a nudge to bring it back.
    /// After the background it starts its sound afresh. If iOS closed the page while the app was away, the game starts again now.
    func resumeGame(afterBackground: Bool) {
        if reloadWhenActive {
            reloadWhenActive = false
            reloadGame()
            return
        }
        sendResume(away: afterBackground)
    }

    /// A call, Siri or an alarm has ended while the app is in front: the game starts its sound afresh.
    func restartSound() {
        sendResume(away: true)
    }

    private func sendResume(away: Bool) {
        let flag = away ? "true" : "false"
        let script = "window.dispatchEvent(new CustomEvent('nativeresume', { detail: { away: \(flag) } }));"
        webView?.evaluateJavaScript(script, completionHandler: nil)
    }

    override var prefersStatusBarHidden: Bool {
        return true
    }

    // The home bar fades out while playing; it comes back with a touch near it.
    override var prefersHomeIndicatorAutoHidden: Bool {
        return true
    }

    // Swipes are part of the controls, so a swipe from the screen edge goes to the game first (a second swipe goes home).
    override var preferredScreenEdgesDeferringSystemGestures: UIRectEdge {
        return [.top, .bottom]
    }

    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return UIDevice.current.userInterfaceIdiom == .pad ? .all : orient.mask
    }
}

extension GameViewController: WKNavigationDelegate {

    func webView(_ webView: WKWebView,
                 decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url, let scheme = url.scheme?.lowercased() else {
            decisionHandler(.cancel)
            return
        }
        if scheme == GameSchemeHandler.scheme || scheme == "about" || scheme == "data" || scheme == "blob" {
            decisionHandler(.allow)
            return
        }
        // Anything pointing outside the game opens in Safari instead of replacing it.
        if scheme == "http" || scheme == "https" || scheme == "mailto" {
            UIApplication.shared.open(url)
        }
        decisionHandler(.cancel)
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // The game is a fixed screen: no pinch zoom.
        webView.scrollView.pinchGestureRecognizer?.isEnabled = false
    }

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        // iOS can reclaim the page's memory while the app sits in the background. Start the game again once the app is in front
        // (a page that loads out of sight can't start its sound), after a short pause if it only just happened, so a struggling
        // device isn't stuck reloading.
        guard UIApplication.shared.applicationState == .active else {
            reloadWhenActive = true
            return
        }
        reloadGame()
    }

    private func reloadGame() {
        let wait = Date().timeIntervalSince(lastReload) < 10 ? 3.0 : 0.0
        lastReload = Date()
        DispatchQueue.main.asyncAfter(deadline: .now() + wait) { [weak self] in
            self?.loadGame()
        }
    }
}
