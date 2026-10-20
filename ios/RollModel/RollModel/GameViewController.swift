import UIKit
import WebKit

/// Hosts the game full screen. The game itself is the bundled web build in the Game folder, served offline.
final class GameViewController: UIViewController {

    /// The launch screen's color (LaunchBackground in the asset catalog), so the app never flashes another color as the game loads.
    static let backgroundColor = UIColor(named: "LaunchBackground") ?? UIColor(red: 18.0 / 255.0, green: 10.0 / 255.0, blue: 36.0 / 255.0, alpha: 1.0)

    private let haptics = HapticsBridge()
    private let device = DeviceBridge()
    private let orient = OrientBridge()
    private let saves = SaveBridge()
    private let ads = AdsBridge()
    private let notify = NotifyBridge()
    private let gameCenter = GameCenterBridge()
    private let purchases = PurchaseBridge()
    private let contentController = WKUserContentController()
    private var webView: WKWebView!
    private var lastReload = Date.distantPast
    private var reloadWhenActive = false
    private var restarts: [Date] = []    // (when the game's page was started over, this last minute)
    private var restartCard: UIView?

    override func loadView() {
        contentController.add(haptics, name: HapticsBridge.messageName)
        // The game picks its graphics level from what this phone is (and eases off in Low Power Mode or when it runs hot).
        contentController.add(device, name: DeviceBridge.messageName)
        // Upright or wide: the player's choice (asked when the game first opens, changed in Settings) turns the iPhone to match.
        contentController.add(orient, name: OrientBridge.messageName)
        // A copy of the save in the app's own files, put back if the web view's storage loses it.
        contentController.add(saves, name: SaveBridge.messageName)
        // Ads (Google AdMob): a rewarded one when the player asks (Skip on a stroke being crafted), and now and then a short one after
        // Play, never for a player who has bought dabs.
        contentController.add(ads, name: AdsBridge.messageName)
        // A nudge when a craft is done, once the player has said yes to one.
        contentController.add(notify, name: NotifyBridge.messageName)
        // Game Center: signed in from the lobby, and a leaderboard for each canvas's Time trial.
        contentController.add(gameCenter, name: GameCenterBridge.messageName)
        // Dab packs, bought with Apple's in-app purchase (any one also turns the ads off).
        contentController.add(purchases, name: PurchaseBridge.messageName)

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
        // The keyboard comes up over the game and the page stays where it is (WebKit would push the whole page up to show the field
        // being typed in): the game lifts just that field above the keyboard, told how tall the keyboard is (see keyboardWillChange).
        webView.scrollView.delegate = self
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
        // iPhone Duo partly folded: the game hears where the fold runs, and keeps its boxes and words to one side of it.
        device.watchFold()
        orient.viewController = self
        ads.webView = webView
        ads.viewController = self
        notify.webView = webView
        gameCenter.webView = webView
        gameCenter.viewController = self
        purchases.webView = webView
        view = webView
    }

    /// The scripts that run before the game's own. They go in afresh before every load, so a page started over has this
    /// moment's description of the phone (Low Power Mode, how warm it is), not the one from when the app opened.
    private func installScripts() {
        contentController.removeAllUserScripts()
        contentController.addUserScript(WKUserScript(source: HapticsBridge.script,
                                                     injectionTime: .atDocumentStart,
                                                     forMainFrameOnly: true))
        // (the screen's scale and refresh rate from the view and its window's screen, not the main screen: on iPhone Duo the game moves
        // between two screens)
        let screen = view.window?.windowScene?.screen
        contentController.addUserScript(WKUserScript(source: DeviceBridge.startScript(scale: traitCollection.displayScale,
                                                                                      maxFPS: screen?.maximumFramesPerSecond ?? 0),
                                                     injectionTime: .atDocumentStart,
                                                     forMainFrameOnly: true))
        contentController.addUserScript(WKUserScript(source: AdsBridge.startScript,
                                                     injectionTime: .atDocumentStart,
                                                     forMainFrameOnly: true))
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        // Typing a name can leave the page pushed up once the keyboard has gone: put it back.
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardDidHide),
                                               name: UIResponder.keyboardDidHideNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillChange(_:)),
                                               name: UIResponder.keyboardWillChangeFrameNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillChange(_:)),
                                               name: UIResponder.keyboardWillHideNotification, object: nil)
        loadGame()
    }

    // A new size or shape (iPhone Duo folded, opened or turned): where the fold runs may have changed with it.
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        device.pushFold()
    }

    @objc private func keyboardDidHide() {
        webView?.scrollView.setContentOffset(.zero, animated: false)
    }

    /// The keyboard is coming up, going, or changing size: the game hears how much of the bottom of the screen it will cover (0 when
    /// it's going, or floating free of the bottom edge on an iPad) and how long it takes to get there, so it can lift the field being
    /// typed in above it in step.
    @objc private func keyboardWillChange(_ note: Notification) {
        guard let webView = webView, webView.window != nil else { return }
        let info = note.userInfo ?? [:]
        let seconds = (info[UIResponder.keyboardAnimationDurationUserInfoKey] as? Double) ?? 0.25
        var height: CGFloat = 0
        if note.name != UIResponder.keyboardWillHideNotification,
           let end = (info[UIResponder.keyboardFrameEndUserInfoKey] as? NSValue)?.cgRectValue {
            // (the keyboard's frame is in the screen's coordinates; the game's view may not fill the screen, on an iPad)
            let space: UICoordinateSpace = webView.window?.windowScene?.screen.coordinateSpace ?? UIScreen.main.coordinateSpace
            let frame = webView.convert(end, from: space), bounds = webView.bounds
            if frame.maxY >= bounds.maxY - 1 && frame.minY < bounds.maxY { height = bounds.maxY - max(frame.minY, bounds.minY) }
        }
        let h = Int(height.rounded()), ms = Int((seconds * 1000).rounded())
        webView.evaluateJavaScript("window.__NATIVE = window.__NATIVE || {}; window.__NATIVE.kb = \(h); "
                                   + "window.dispatchEvent(new CustomEvent('nativekeyboard', { detail: { h: \(h), ms: \(ms) } }));",
                                   completionHandler: nil)
    }

    /// The phone is short of memory: the game lets go of the songs it isn't playing, so iOS is less likely to close it.
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        webView?.evaluateJavaScript("window.dispatchEvent(new Event('nativememory'));", completionHandler: nil)
    }

    private func loadGame() {
        installScripts()
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

    // A phone-shaped screen keeps the way the player plays; a roomy one (iPhone Duo open or closed, an iPad) turns freely.
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return OrientBridge.turnsFreely(self) ? .all : orient.mask
    }

    // iPhone Duo folding or unfolding (or any window resized) changes the game's shape mid-session: the page sees the new size itself,
    // and the turns allowed are worked out again from it.
    override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
        super.viewWillTransition(to: size, with: coordinator)
        coordinator.animate(alongsideTransition: nil) { [weak self] _ in
            guard let self = self else { return }
            if #available(iOS 16.0, *) {
                self.setNeedsUpdateOfSupportedInterfaceOrientations()
            }
        }
    }
}

extension GameViewController: UIScrollViewDelegate {

    /// The page never scrolls (the game is one fixed screen). When the keyboard comes up WebKit scrolls it to show the field being typed
    /// in, which pushed the whole game up out of sight: it's put straight back, and the game lifts the field itself.
    func scrollViewDidScroll(_ scrollView: UIScrollView) {
        if scrollView.contentOffset != .zero { scrollView.contentOffset = .zero }
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
        // Anything pointing outside the game opens in Safari instead of replacing it (only from the game itself, never from
        // a frame inside it).
        if scheme == "http" || scheme == "https" || scheme == "mailto", navigationAction.targetFrame?.isMainFrame != false {
            UIApplication.shared.open(url)
        }
        decisionHandler(.cancel)
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // The game is a fixed screen: no pinch zoom.
        webView.scrollView.pinchGestureRecognizer?.isEnabled = false
        // A page that has just loaded hears where the fold is (if iPhone Duo is partly folded), even if that hasn't changed.
        device.pushFold(force: true)
    }

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        // The page that kept the screen on for a match is gone: the screen may sleep again until a match asks.
        UIApplication.shared.isIdleTimerDisabled = false
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
        // A fourth time in a minute: something keeps closing the page (most likely the phone is short of memory). Rather than go
        // round again, the player gets a card to start the game when they're ready.
        let now = Date()
        restarts = restarts.filter { now.timeIntervalSince($0) < 60 } + [now]
        guard restarts.count <= 3 else {
            showRestartCard()
            return
        }
        let wait = now.timeIntervalSince(lastReload) < 10 ? 3.0 : 0.0
        lastReload = now
        DispatchQueue.main.asyncAfter(deadline: .now() + wait) { [weak self] in
            self?.loadGame()
        }
    }

    /// Over the game, in the launch screen's color: what happened, that progress is kept, and a button to start again.
    private func showRestartCard() {
        guard restartCard == nil else { return }
        let card = UIView(frame: view.bounds)
        card.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        card.backgroundColor = GameViewController.backgroundColor

        let title = UILabel()
        title.text = "Roll Model stopped"
        title.font = .systemFont(ofSize: 24, weight: .heavy)
        title.textColor = .white
        title.textAlignment = .center
        title.numberOfLines = 0

        let note = UILabel()
        note.text = "Your progress is saved. Closing other apps can help it run."
        note.font = .systemFont(ofSize: 16, weight: .semibold)
        note.textColor = UIColor(white: 1, alpha: 0.72)
        note.textAlignment = .center
        note.numberOfLines = 0

        var look = UIButton.Configuration.filled()
        look.title = "Start again"
        look.baseBackgroundColor = UIColor(red: 1.0, green: 232.0 / 255.0, blue: 150.0 / 255.0, alpha: 1.0)
        look.baseForegroundColor = UIColor(red: 23.0 / 255.0, green: 19.0 / 255.0, blue: 32.0 / 255.0, alpha: 1.0)
        look.cornerStyle = .large
        look.contentInsets = NSDirectionalEdgeInsets(top: 14, leading: 30, bottom: 14, trailing: 30)
        look.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { incoming in
            var outgoing = incoming
            outgoing.font = UIFont.systemFont(ofSize: 18, weight: .heavy)
            return outgoing
        }
        let button = UIButton(configuration: look, primaryAction: UIAction { [weak self] _ in
            self?.startAgain()
        })

        let stack = UIStackView(arrangedSubviews: [title, note, button])
        stack.axis = .vertical
        stack.alignment = .center
        stack.spacing = 14
        stack.setCustomSpacing(26, after: note)
        stack.translatesAutoresizingMaskIntoConstraints = false
        card.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.centerXAnchor.constraint(equalTo: card.centerXAnchor),
            stack.centerYAnchor.constraint(equalTo: card.centerYAnchor),
            stack.leadingAnchor.constraint(greaterThanOrEqualTo: card.leadingAnchor, constant: 32),
            stack.trailingAnchor.constraint(lessThanOrEqualTo: card.trailingAnchor, constant: -32)
        ])
        view.addSubview(card)
        restartCard = card
    }

    private func startAgain() {
        restartCard?.removeFromSuperview()
        restartCard = nil
        restarts = []
        lastReload = Date()
        loadGame()
    }
}
