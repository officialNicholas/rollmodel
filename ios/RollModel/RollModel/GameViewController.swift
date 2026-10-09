import UIKit
import WebKit

/// The game runs in a full-screen web view from the bundled `www` folder. Two message handlers come back from the page:
/// `orient` (upright, wide or free) and `device` (keep the screen awake during a match).
final class GameViewController: UIViewController, WKScriptMessageHandler, WKNavigationDelegate {
    private var webView: WKWebView!

    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { OrientBridge.shared.mask }
    override var preferredScreenEdgesDeferringSystemGestures: UIRectEdge { .all }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black

        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        config.preferences.javaScriptCanOpenWindowsAutomatically = false
        if #available(iOS 14.0, *) { config.defaultWebpagePreferences.allowsContentJavaScript = true }

        // The page reads window.__NATIVE to pick its graphics tier and to know it is in the app.
        let native = WKUserScript(source: "window.__NATIVE = { ios: true, tier: 3, lowPower: false };", injectionTime: .atDocumentStart, forMainFrameOnly: true)
        config.userContentController.addUserScript(native)
        config.userContentController.add(self, name: "orient")
        config.userContentController.add(self, name: "device")

        webView = WKWebView(frame: view.bounds, configuration: config)
        webView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        webView.navigationDelegate = self
        webView.isOpaque = false
        webView.backgroundColor = .black
        webView.scrollView.isScrollEnabled = false
        webView.scrollView.bounces = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        if #available(iOS 16.4, *) { webView.isInspectable = true }
        view.addSubview(webView)

        guard let index = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "www") else {
            assertionFailure("www/index.html is missing from the bundle: run tools/ios_pack.py to copy the game in")
            return
        }
        webView.loadFileURL(index, allowingReadAccessTo: index.deletingLastPathComponent())
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        switch message.name {
        case "orient":
            OrientBridge.shared.apply((message.body as? String) ?? "", from: self)
        case "device":
            if let body = message.body as? [String: Any], let awake = body["keepAwake"] as? Bool {
                UIApplication.shared.isIdleTimerDisabled = awake
            }
        default: break
        }
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        // Outside links (if any) go to Safari; the game itself stays in the app.
        if let url = navigationAction.request.url, url.scheme == "http" || url.scheme == "https" {
            UIApplication.shared.open(url)
            decisionHandler(.cancel); return
        }
        decisionHandler(.allow)
    }
}
