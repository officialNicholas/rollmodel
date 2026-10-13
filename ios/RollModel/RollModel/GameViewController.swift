import UIKit
import WebKit

/// The game runs in a full-screen web view from the bundled `www` folder, served as rollmodel://localhost/... by `BundleSchemeHandler`
/// (WebKit's fetch() can't read file:// URLs, and the page fetches its music, sounds and character pack). Two message handlers come
/// back from the page: `orient` (upright, wide or free) and `device` (keep the screen awake during a match).
final class GameViewController: UIViewController, WKScriptMessageHandler, WKNavigationDelegate {
    private var webView: WKWebView!
    private var schemeHandler: BundleSchemeHandler?

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

        guard let index = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "www") else {
            assertionFailure("www/index.html is missing from the bundle: run tools/ios_pack.py to copy the game in")
            return
        }
        let handler = BundleSchemeHandler(root: index.deletingLastPathComponent())
        schemeHandler = handler
        config.setURLSchemeHandler(handler, forURLScheme: BundleSchemeHandler.scheme)

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

        if let url = URL(string: BundleSchemeHandler.scheme + "://localhost/index.html") { webView.load(URLRequest(url: url)) }
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

/// Serves the bundled `www` folder to the web view (rollmodel://localhost/<path>), so the page's fetch() calls work as they do on the
/// web. Files are read off the main thread; a task WebKit has stopped is not answered.
final class BundleSchemeHandler: NSObject, WKURLSchemeHandler {
    static let scheme = "rollmodel"
    private let root: URL
    private var stopped = Set<ObjectIdentifier>()
    private let queue = DispatchQueue(label: "rollmodel.www", qos: .userInitiated)

    init(root: URL) {
        self.root = root.standardizedFileURL
        super.init()
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(URLError(.badURL))
            return
        }
        var path = url.path.removingPercentEncoding ?? url.path
        if path.isEmpty || path == "/" { path = "/index.html" }
        let file = root.appendingPathComponent(String(path.drop(while: { $0 == "/" }))).standardizedFileURL
        let rootPath = root.path
        let id = ObjectIdentifier(urlSchemeTask as AnyObject)
        queue.async {
            let inside = file.path.hasPrefix(rootPath + "/")
            let data: Data? = inside ? (try? Data(contentsOf: file, options: .mappedIfSafe)) : nil
            DispatchQueue.main.async {
                if self.stopped.remove(id) != nil { return }
                if let data = data {
                    let headers = ["Content-Type": BundleSchemeHandler.mime(file.pathExtension), "Content-Length": String(data.count), "Access-Control-Allow-Origin": "*"]
                    if let response = HTTPURLResponse(url: url, statusCode: 200, httpVersion: "HTTP/1.1", headerFields: headers) { urlSchemeTask.didReceive(response) }
                    urlSchemeTask.didReceive(data)
                } else if let response = HTTPURLResponse(url: url, statusCode: 404, httpVersion: "HTTP/1.1", headerFields: ["Content-Type": "text/plain"]) {
                    urlSchemeTask.didReceive(response)
                    urlSchemeTask.didReceive(Data())
                }
                urlSchemeTask.didFinish()
            }
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {
        stopped.insert(ObjectIdentifier(urlSchemeTask as AnyObject))
    }

    static func mime(_ ext: String) -> String {
        switch ext.lowercased() {
        case "html", "htm": return "text/html; charset=utf-8"
        case "js", "mjs": return "text/javascript; charset=utf-8"
        case "css": return "text/css; charset=utf-8"
        case "json": return "application/json"
        case "txt": return "text/plain; charset=utf-8"
        case "webp": return "image/webp"
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "gif": return "image/gif"
        case "svg": return "image/svg+xml"
        case "mp3": return "audio/mpeg"
        case "m4a", "mp4", "aac": return "audio/mp4"
        case "wav": return "audio/wav"
        case "ogg", "oga": return "audio/ogg"
        case "woff2": return "font/woff2"
        case "woff": return "font/woff"
        case "ttf": return "font/ttf"
        default: return "application/octet-stream"
        }
    }
}
