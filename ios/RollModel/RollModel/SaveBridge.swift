import Foundation
import WebKit

/// Keeps a copy of the game's save in the app's own files, outside the web view's storage. iOS can clear website data, and the
/// web view can lose its last second of writes if the app is closed straight away, so progress lives in both places.
///
/// The game posts { t, save } to window.webkit.messageHandlers.save (t: when it saved, in ms; save: the save as JSON). Before the
/// game's own script runs, the page loads native/save.js, which puts this copy back if the web view's copy is missing or older.
/// The copy sits in Application Support, so it goes into the phone's backups along with the rest of the app.
final class SaveBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "save"
    static let scriptPath = "/native/save.js"
    /// The game's own storage key (see `KEY` in the game). Its save time is kept under the same key plus ".t".
    private static let storageKey = "paint-world-red.v1"
    private static let queue = DispatchQueue(label: "studio.primeshots.rollmodel.save", qos: .utility)
    private static var lastTime: Double = 0 // only touched on `queue`

    private static var fileURL: URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        return base.appendingPathComponent("RollModel", isDirectory: true).appendingPathComponent("save.json")
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any],
              let save = body["save"] as? String, !save.isEmpty, save.utf8.count < 4_000_000,
              let time = (body["t"] as? NSNumber)?.doubleValue, SaveBridge.sane(time) else { return }
        SaveBridge.queue.async {
            // Saves arrive in order, but never let an older one replace a newer one.
            guard time >= SaveBridge.lastTime,
                  let data = try? JSONSerialization.data(withJSONObject: ["t": time, "save": save]) else { return }
            let url = SaveBridge.fileURL
            do {
                try FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
                try data.write(to: url, options: .atomic)
                SaveBridge.lastTime = time
            } catch {
                // The web view's own copy is still there.
            }
        }
    }

    /// The page's native/save.js: puts the app's copy back when the web view's copy is missing or older. Empty when there's no copy yet.
    static func restoreScript() -> String {
        let stored: Data? = queue.sync { try? Data(contentsOf: fileURL) }
        guard let data = stored,
              let object = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any],
              let save = object["save"] as? String,
              let time = (object["t"] as? NSNumber)?.doubleValue, sane(time),
              let parsed = try? JSONSerialization.jsonObject(with: Data(save.utf8)), parsed is [String: Any],
              let literal = jsString(save) else {
            return "/* no saved copy in the app yet */\n"
        }
        return """
        (function () { try {
          var k = '\(storageKey)', T = \(Int64(time)), lt = +(localStorage.getItem(k + '.t') || 0);
          if (!localStorage.getItem(k) || lt < T) { localStorage.setItem(k, \(literal)); localStorage.setItem(k + '.t', String(T)); }
        } catch (e) {} })();

        """
    }

    /// A save time the app can hold: a real number of milliseconds since 1970, not a broken one (that would stop the app at launch).
    private static func sane(_ time: Double) -> Bool {
        return time.isFinite && time >= 0 && time < 1e15
    }

    /// A string as a JavaScript string literal (JSON's quoting is valid JavaScript).
    private static func jsString(_ value: String) -> String? {
        guard let data = try? JSONSerialization.data(withJSONObject: [value]),
              let array = String(data: data, encoding: .utf8), array.count >= 2 else { return nil }
        return String(array.dropFirst().dropLast())
    }
}
