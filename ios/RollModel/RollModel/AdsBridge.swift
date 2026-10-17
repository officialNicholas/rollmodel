import UIKit
import WebKit
#if canImport(GoogleMobileAds)
import GoogleMobileAds
#endif
#if canImport(UserMessagingPlatform)
import UserMessagingPlatform
#endif

/// Rewarded ads, and only when the player asks for one. On the Strokes page, Skip on a stroke being crafted plays a rewarded ad
/// (Google AdMob), and the craft finishes once the ad says it was watched. Which ads play is up to the ad unit in AdMob: since the
/// player chose to watch, it can allow longer videos and playable (interactive) ads.
///
/// The game posts here as "ads":
/// - {init, kid} once the player can craft: Google's consent check (once a session), and whether the player is under 13.
/// - {warm} when an ad may be wanted soon (a stroke on the bench): one is loaded ahead, so it plays the moment Skip is tapped.
/// - {show: place} when the player taps to watch.
/// - {cancel} when the player stops waiting for one (the game's Cancel): it won't pop up later; one still loading is kept for next time.
/// - {privacy} from the game's Privacy Policy page: Google's privacy choices form.
///
/// It hears back through a "nativead" window event: {e: "open"}, {e: "reward"} (and again just before the close), {e: "close",
/// earned}, {e: "fail", why} and {e: "state", privacy} (whether the Privacy Policy page needs its "Ad privacy choices" button).
///
/// Every ad is capped at the parental guidance rating. A player the game knows is under 13 gets child treatment: only ads fit for
/// children, none of them personalised, and no consent message. In the EEA, the UK and Switzerland, Google's consent message (made in
/// AdMob under Privacy & messaging) shows the first time a player asks for an ad, before it plays.
final class AdsBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "ads"

    /// Google's sample rewarded ad unit: test ads only, never paid.
    static let testUnitID = "ca-app-pub-3940256099942544/1712485313"

    /// The rewarded ad unit: RollModelRewardedAdUnitID in Info.plist (with the app's own ID, GADApplicationIdentifier, next to it), in
    /// the App Store build. A build run from Xcode or installed from TestFlight uses Google's test unit instead: its ads are marked
    /// "Test mode", are safe to tap, and always come, so trying the game never counts against the AdMob account.
    static var unitID: String {
        #if DEBUG
        return testUnitID
        #else
        if isTestFlight { return testUnitID }
        let id = (Bundle.main.object(forInfoDictionaryKey: "RollModelRewardedAdUnitID") as? String ?? "").trimmingCharacters(in: .whitespaces)
        return id.isEmpty ? testUnitID : id
        #endif
    }

    /// Installed from TestFlight: its App Store receipt is a sandbox one ("sandboxReceipt"; an App Store install has "receipt").
    static var isTestFlight: Bool {
        return Bundle.main.appStoreReceiptURL?.lastPathComponent == "sandboxReceipt"
    }

    /// Runs at document start: whether this build has the ads SDK in it (without it, the game keeps Skip free).
    static var startScript: String {
        #if canImport(GoogleMobileAds)
        return "window.__ADS = { sdk: true };"
        #else
        return "window.__ADS = { sdk: false };"
        #endif
    }

    weak var webView: WKWebView?
    weak var viewController: UIViewController?

    private enum Check { case idle, running, done }

    private var kid = false
    private var check = Check.idle
    private var afterCheck: [() -> Void] = []
    private var started = false
    #if canImport(GoogleMobileAds)
    private var ready: RewardedAd?       // loaded, waiting to be shown
    private var onScreen: RewardedAd?    // (held until it's closed)
    #endif
    private var loadedAt = Date.distantPast
    private var loading = false
    private var loadGen = 0              // (bumped when the player turns out to be a child: a load already on its way is dropped)
    private var waiting: String?         // the player tapped for an ad and is waiting for one to load
    private var waitingSince = Date.distantPast
    private var waitID = 0               // (which wait the 12-second limit belongs to)
    private var showing: String?         // the ad on screen now was for this
    private var earned = false

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any] else { return }
        if let young = body["kid"] as? Bool { setKid(young) }
        let warm = (body["warm"] as? Bool) == true
        if warm {
            prepare(asking: false) { [weak self] ok in
                guard ok else { return }
                self?.load()
            }
        } else if (body["init"] as? Bool) == true {
            checkConsent { [weak self] in self?.sendState() } // (a page started over hears whether it needs Ad privacy choices too)
        }
        if let place = body["show"] as? String, !place.isEmpty { show(place) }
        if (body["cancel"] as? Bool) == true { cancelWait() }
        if (body["privacy"] as? Bool) == true { privacyChoices() }
    }

    // MARK: Consent and start

    /// Whether ads may be requested: Google's consent message has been answered where one's needed (or none is), or the player is a
    /// child, whose ads are child-directed and not personalised.
    private var mayRequest: Bool {
        #if canImport(UserMessagingPlatform)
        return kid || ConsentInformation.shared.canRequestAds
        #else
        return true
        #endif
    }

    /// The consent check, then (when the player is asking for an ad right now) Google's consent message if one is needed, then the SDK
    /// started. Done with whether ads may be requested.
    private func prepare(asking: Bool, _ done: @escaping (Bool) -> Void) {
        #if canImport(GoogleMobileAds)
        checkConsent { [weak self] in
            guard let self = self else { return }
            if self.mayRequest {
                self.startSDK()
                done(true)
                return
            }
            guard asking else {
                done(false)
                return
            }
            self.askConsent { [weak self] in
                guard let self = self else { return }
                if self.mayRequest { self.startSDK() }
                done(self.mayRequest)
            }
        }
        #else
        done(false)
        #endif
    }

    /// Asks Google whether this player needs a consent message (once a session; again later if it couldn't reach Google).
    private func checkConsent(_ then: @escaping () -> Void) {
        #if canImport(UserMessagingPlatform)
        if kid || check == .done {
            then()
            return
        }
        afterCheck.append(then)
        guard check == .idle else { return }
        check = .running
        ConsentInformation.shared.requestConsentInfoUpdate(with: RequestParameters()) { [weak self] error in
            onMain {
                guard let self = self else { return }
                self.check = error == nil ? .done : .idle
                self.sendState()
                let queued = self.afterCheck
                self.afterCheck = []
                queued.forEach { $0() }
            }
        }
        #else
        then()
        #endif
    }

    /// Google's consent message, if this player needs one before ads can be requested.
    private func askConsent(_ then: @escaping () -> Void) {
        #if canImport(UserMessagingPlatform)
        guard let host = topController() else {
            then()
            return
        }
        ConsentForm.loadAndPresentIfRequired(from: host) { [weak self] _ in
            onMain {
                self?.sendState()
                then()
            }
        }
        #else
        then()
        #endif
    }

    private func startSDK() {
        #if canImport(GoogleMobileAds)
        guard !started else { return }
        started = true
        configure()
        MobileAds.shared.start(completionHandler: nil)
        #endif
    }

    /// Set before the SDK starts, and again if the game learns the player is under 13.
    private func configure() {
        #if canImport(GoogleMobileAds)
        let configuration = MobileAds.shared.requestConfiguration
        if kid {
            configuration.ageRestrictedTreatment = .child
            configuration.maxAdContentRating = .general
        } else {
            configuration.ageRestrictedTreatment = .unspecified
            configuration.maxAdContentRating = .parentalGuidance
        }
        #endif
    }

    private func setKid(_ young: Bool) {
        guard young != kid else { return }
        kid = young
        guard started else { return }
        configure()
        #if canImport(GoogleMobileAds)
        ready = nil // (one loaded before isn't shown to a child, nor one still on its way)
        loadGen += 1
        #endif
    }

    // MARK: Loading and showing

    /// Rewarded ads last an hour once loaded: one older than 50 minutes is loaded again.
    private var fresh: Bool {
        #if canImport(GoogleMobileAds)
        return ready != nil && Date().timeIntervalSince(loadedAt) < 50 * 60
        #else
        return false
        #endif
    }

    private func load() {
        #if canImport(GoogleMobileAds)
        guard started, !loading, !fresh else { return }
        ready = nil
        loading = true
        let gen = loadGen
        RewardedAd.load(with: AdsBridge.unitID, request: GoogleMobileAds.Request()) { [weak self] loaded, error in
            onMain {
                guard let self = self else { return }
                self.loading = false
                guard gen == self.loadGen else {
                    // Asked for before the game said this player is a child: dropped, and asked for again if the player's waiting.
                    if self.waiting != nil { self.load() }
                    return
                }
                guard let loaded = loaded else {
                    if let place = self.waiting {
                        self.stopWaiting()
                        self.send(["e": "fail", "p": place, "why": AdsBridge.why(error)])
                    }
                    return
                }
                loaded.fullScreenContentDelegate = self
                self.ready = loaded
                self.loadedAt = Date()
                if let place = self.waiting { self.present(place) }
            }
        }
        #endif
    }

    /// The player tapped to watch: the ad plays now if one is loaded, or as soon as one loads (up to 12 seconds).
    private func show(_ place: String) {
        #if canImport(GoogleMobileAds)
        let stale = waiting != nil && Date().timeIntervalSince(waitingSince) > 60
        guard waiting == nil || stale, showing == nil else {
            send(["e": "fail", "p": place, "why": "busy"])
            return
        }
        if stale { stopWaiting() }
        waiting = place
        waitingSince = Date()
        let id = waitID // (this wait's own: an answer for one given up on isn't taken for this one)
        prepare(asking: true) { [weak self] ok in
            guard let self = self, self.waitID == id, self.waiting == place else { return }
            guard ok else {
                self.stopWaiting()
                self.send(["e": "fail", "p": place, "why": "noads"])
                return
            }
            if self.fresh {
                self.present(place)
                return
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 12) { [weak self] in
                guard let self = self, self.waitID == id, self.waiting == place else { return }
                self.stopWaiting()
                self.send(["e": "fail", "p": place, "why": "slow"]) // (if it loads later, it's kept for next time)
            }
            self.load()
        }
        #else
        send(["e": "fail", "p": place, "why": "noads"])
        #endif
    }

    private func stopWaiting() {
        waitID += 1
        waiting = nil
    }

    /// The player gave up waiting (the game's Cancel): the ad won't be shown for that wait. One still loading is kept, ready for next time.
    private func cancelWait() {
        guard waiting != nil else { return }
        stopWaiting()
    }

    private func present(_ place: String) {
        #if canImport(GoogleMobileAds)
        stopWaiting()
        // The player left the app (the home screen, a call, the app switcher) while it loaded: no ad pops up while they're away.
        // It stays loaded, so it plays as soon as they ask again.
        guard UIApplication.shared.applicationState == .active else {
            send(["e": "fail", "p": place, "why": "slow"])
            return
        }
        guard let next = ready, let host = topController() else {
            send(["e": "fail", "p": place, "why": "noads"])
            return
        }
        ready = nil // (each ad plays once)
        onScreen = next
        showing = place
        earned = false
        next.present(from: host) { [weak self] in
            onMain {
                guard let self = self else { return }
                self.earned = true
                self.send(["e": "reward", "p": place])
            }
        }
        #endif
    }

    // MARK: Privacy choices

    /// Google's privacy choices form, from the button on the game's Privacy Policy page.
    private func privacyChoices() {
        #if canImport(UserMessagingPlatform)
        guard let host = topController() else { return }
        ConsentForm.presentPrivacyOptionsForm(from: host) { [weak self] _ in
            onMain { self?.sendState() }
        }
        #endif
    }

    /// Tells the game whether it needs to offer the privacy choices form (Google says so for some players in the EEA, the UK and
    /// Switzerland).
    private func sendState() {
        var privacy = false
        #if canImport(UserMessagingPlatform)
        privacy = !kid && ConsentInformation.shared.privacyOptionsRequirementStatus == .required
        #endif
        send(["e": "state", "privacy": privacy])
    }

    // MARK: Helpers

    private func send(_ detail: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: detail), let text = String(data: data, encoding: .utf8) else { return }
        webView?.evaluateJavaScript("window.dispatchEvent(new CustomEvent('nativead', { detail: \(text) }));", completionHandler: nil)
    }

    /// The controller on top (the game, or whatever it has up), to present the ad and Google's forms from.
    private func topController() -> UIViewController? {
        guard var top = viewController ?? webView?.window?.rootViewController else { return nil }
        while let shown = top.presentedViewController, !shown.isBeingDismissed { top = shown }
        return top
    }

    /// Why an ad didn't load, in the game's words: offline, slow, or none to show.
    private static func why(_ error: Error?) -> String {
        guard let error = error else { return "noads" }
        let code = (error as NSError).code
        if (error as NSError).domain == NSURLErrorDomain { return "offline" }
        return code == 2 ? "offline" : code == 5 ? "slow" : "noads" // (the SDK's network error and timeout codes; no fill and the rest)
    }
}

#if canImport(GoogleMobileAds)
extension AdsBridge: FullScreenContentDelegate {

    func adWillPresentFullScreenContent(_ ad: FullScreenPresentingAd) {
        send(["e": "open", "p": showing ?? ""])
    }

    func ad(_ ad: FullScreenPresentingAd, didFailToPresentFullScreenContentWithError error: Error) {
        let place = showing ?? ""
        showing = nil
        onScreen = nil
        send(["e": "fail", "p": place, "why": "noads"])
    }

    func adDidDismissFullScreenContent(_ ad: FullScreenPresentingAd) {
        let place = showing ?? ""
        showing = nil
        onScreen = nil
        // The ad may have changed the app's sound (its unmute button plays even with the ring switch on silent): the game's own sound
        // settings come back, then the game starts its sound afresh, as after a call.
        GameAudio.apply()
        // (the reward again: if iOS had to start the game's page over while the ad was up, the first one went to the page it closed)
        if earned { send(["e": "reward", "p": place]) }
        send(["e": "close", "p": place, "earned": earned])
        webView?.evaluateJavaScript("window.dispatchEvent(new CustomEvent('nativeresume', { detail: { away: true } }));", completionHandler: nil)
        // (and again just after, in case the SDK sets its own back once this callback is done)
        DispatchQueue.main.async { GameAudio.apply() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { GameAudio.apply() }
    }
}
#endif

/// Runs it on the main thread: at once if already there (so the ad's callbacks keep their order), otherwise next.
private func onMain(_ work: @escaping () -> Void) {
    if Thread.isMainThread {
        work()
    } else {
        DispatchQueue.main.async(execute: work)
    }
}
