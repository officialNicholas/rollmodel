import UIKit
import WebKit

/// Hosts the game full screen. The game itself is the bundled web build in the Game folder, served offline.
final class GameViewController: UIViewController {

    static let backgroundColor = UIColor(red: 18.0 / 255.0, green: 10.0 / 255.0, blue: 36.0 / 255.0, alpha: 1.0)

    private let haptics = HapticsBridge()
    private let device = DeviceBridge()
    private let orient = OrientBridge()
    private var webView: WKWebView!
    private var lastReload = Date.distantPast

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
        // The way up the player picked: the game sends it, and the window follows it.
        orient.controller = self
        contentController.add(orient, name: OrientBridge.messageName)

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
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        loadGame()
    }

    private func loadGame() {
        webView.load(URLRequest(url: GameSchemeHandler.startURL))
    }

    /// The game already pauses itself when its window loses focus, so this just tells it that happened.
    func pauseGame() {
        webView?.evaluateJavaScript("window.dispatchEvent(new Event('blur'));", completionHandler: nil)
    }

    /// The app is in front again: the game's sound may have been cut off while it was away, so it gets a nudge to bring it back.
    func resumeGame() {
        webView?.evaluateJavaScript("window.dispatchEvent(new Event('nativeresume'));", completionHandler: nil)
    }

    override var prefersStatusBarHidden: Bool {
        return true
    }

    // Swipes are part of the controls, so a swipe from the screen edge goes to the game first (a second swipe goes home).
    override var preferredScreenEdgesDeferringSystemGestures: UIRectEdge {
        return [.top, .bottom]
    }

    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return OrientBridge.mask
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

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        // iOS can reclaim the page's memory while the app sits in the background. Start the game again,
        // after a short pause if it only just happened, so a struggling device isn't stuck reloading.
        let wait = Date().timeIntervalSince(lastReload) < 10 ? 3.0 : 0.0
        lastReload = Date()
        DispatchQueue.main.asyncAfter(deadline: .now() + wait) { [weak self] in
            self?.loadGame()
        }
    }
}
