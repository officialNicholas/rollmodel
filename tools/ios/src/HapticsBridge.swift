import UIKit
import WebKit

/// iOS web views have no navigator.vibrate, so this adds one: the game's buzzes become Taptic Engine taps.
/// A pattern is [on, off, on, ...] in milliseconds, like the web API; longer pulses tap harder.
final class HapticsBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "haptic"

    static let script = """
    (function () {
      var bridge = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.haptic;
      if (!bridge) { return; }
      var vibrate = function (pattern) {
        var list = Array.isArray(pattern) ? pattern : [pattern];
        try { bridge.postMessage(list.map(function (v) { return Number(v) || 0; })); } catch (e) {}
        return true;
      };
      try {
        Object.defineProperty(Navigator.prototype, 'vibrate', { value: vibrate, configurable: true, writable: true });
      } catch (e) {
        try { navigator.vibrate = vibrate; } catch (e2) {}
      }
    })();
    """

    private let light = UIImpactFeedbackGenerator(style: .light)
    private let medium = UIImpactFeedbackGenerator(style: .medium)
    private let heavy = UIImpactFeedbackGenerator(style: .heavy)
    private var patternID = 0

    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard let values = message.body as? [Any] else { return }
        let pattern = values.compactMap { ($0 as? NSNumber)?.doubleValue }
        play(pattern)
    }

    private func play(_ pattern: [Double]) {
        // A new pattern replaces one still playing, the same as navigator.vibrate.
        patternID += 1
        let id = patternID
        var startMs = 0.0
        for (index, value) in pattern.prefix(16).enumerated() {
            let ms = max(0, value)
            if index % 2 == 0 && ms > 0 {
                let generator = ms >= 35 ? heavy : (ms >= 18 ? medium : light)
                generator.prepare()
                if startMs <= 0 {
                    generator.impactOccurred()
                } else {
                    DispatchQueue.main.asyncAfter(deadline: .now() + startMs / 1000.0) { [weak self] in
                        guard let self = self, self.patternID == id else { return }
                        generator.impactOccurred()
                    }
                }
            }
            startMs += ms
        }
    }
}
