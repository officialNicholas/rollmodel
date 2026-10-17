import Foundation
import WebKit

/// Serves the bundled game from a private address (rollmodel://localhost), so it runs offline and its saved name,
/// color and best scores stay put between launches. None of the game is ever fetched from the internet (only online play
/// goes out, to the game server and the friends service).
///
/// Files are read off the main thread (the songs and the character pack are several MB, and reading them on the main
/// thread would stall the game), byte ranges are honored (what audio and video elements ask for), and a request the
/// web view has called off is never answered (answering one crashes the app).
final class GameSchemeHandler: NSObject, WKURLSchemeHandler {

    static let scheme = "rollmodel"
    static let startURL = URL(string: "rollmodel://localhost/index.html")!

    private let root: URL? = Bundle.main.url(forResource: "Game", withExtension: nil)
    private let files = DispatchQueue(label: "studio.primeshots.rollmodel.files", qos: .userInitiated, attributes: .concurrent)
    /// Requests still wanted by the web view. Main thread only.
    private var live = Set<ObjectIdentifier>()

    private struct Reply {
        var status: Int
        var mimeType: String
        var data: Data
        var headers: [String: String] = [:]
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(URLError(.badURL))
            return
        }
        let id = ObjectIdentifier(urlSchemeTask)
        live.insert(id)
        let range = urlSchemeTask.request.value(forHTTPHeaderField: "Range")
        files.async { [weak self] in
            guard let self = self else { return }
            let reply = self.reply(for: url, range: range)
            DispatchQueue.main.async {
                // The task is held by this closure, so no new request can share its identity until this runs.
                guard self.live.remove(id) != nil else { return }
                self.send(reply, to: urlSchemeTask, url: url)
            }
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {
        live.remove(ObjectIdentifier(urlSchemeTask))
    }

    private func reply(for url: URL, range: String?) -> Reply {
        var path = url.path
        if path.isEmpty || path == "/" {
            path = "/index.html"
        }
        // The app's copy of the save, put back before the game starts (see SaveBridge).
        if path == SaveBridge.scriptPath {
            return Reply(status: 200, mimeType: "text/javascript; charset=utf-8", data: Data(SaveBridge.restoreScript().utf8))
        }
        guard let root = root else {
            return Reply(status: 404, mimeType: "text/plain; charset=utf-8", data: Data("Not found".utf8))
        }
        let rootPath = root.standardizedFileURL.path
        let fileURL = root.appendingPathComponent(String(path.dropFirst())).standardizedFileURL
        let mimeType = GameSchemeHandler.mimeType(for: fileURL.pathExtension)

        // Only files inside the Game folder are ever served.
        guard fileURL.path.hasPrefix(rootPath + "/"),
              let size = (try? FileManager.default.attributesOfItem(atPath: fileURL.path))?[.size] as? NSNumber else {
            return Reply(status: 404, mimeType: "text/plain; charset=utf-8", data: Data("Not found".utf8))
        }
        let total = size.intValue

        if let range = range, let span = GameSchemeHandler.byteRange(range, total: total) {
            let (start, end) = span
            guard let handle = try? FileHandle(forReadingFrom: fileURL) else {
                return Reply(status: 404, mimeType: "text/plain; charset=utf-8", data: Data("Not found".utf8))
            }
            defer { try? handle.close() }
            do {
                try handle.seek(toOffset: UInt64(start))
            } catch {
                return Reply(status: 416, mimeType: "text/plain; charset=utf-8", data: Data(),
                             headers: ["Content-Range": "bytes */\(total)"])
            }
            // (the throwing read: the old one stops the app on a read error)
            guard let data = try? handle.read(upToCount: end - start + 1), !data.isEmpty else {
                return Reply(status: 416, mimeType: "text/plain; charset=utf-8", data: Data(),
                             headers: ["Content-Range": "bytes */\(total)"])
            }
            return Reply(status: 206, mimeType: mimeType, data: data,
                         headers: ["Content-Range": "bytes \(start)-\(start + data.count - 1)/\(total)"])
        }

        guard let data = try? Data(contentsOf: fileURL, options: .mappedIfSafe) else {
            return Reply(status: 404, mimeType: "text/plain; charset=utf-8", data: Data("Not found".utf8))
        }
        return Reply(status: 200, mimeType: mimeType, data: data)
    }

    /// "bytes=start-end", "bytes=start-" or "bytes=-suffix" (the first range only). Nil when it can't be met.
    private static func byteRange(_ header: String, total: Int) -> (Int, Int)? {
        guard total > 0, header.hasPrefix("bytes=") else { return nil }
        let spec = header.dropFirst("bytes=".count).split(separator: ",").first.map(String.init) ?? ""
        let parts = spec.split(separator: "-", maxSplits: 1, omittingEmptySubsequences: false).map { $0.trimmingCharacters(in: .whitespaces) }
        guard parts.count == 2 else { return nil }
        if parts[0].isEmpty {
            guard let suffix = Int(parts[1]), suffix > 0 else { return nil }
            return (max(0, total - suffix), total - 1)
        }
        guard let start = Int(parts[0]), start < total else { return nil }
        let end = Int(parts[1]).map { min($0, total - 1) } ?? total - 1
        return end >= start ? (start, end) : nil
    }

    private func send(_ reply: Reply, to task: WKURLSchemeTask, url: URL) {
        var headers = reply.headers
        headers["Content-Type"] = reply.mimeType
        headers["Content-Length"] = String(reply.data.count)
        headers["Cache-Control"] = "no-cache"
        headers["Accept-Ranges"] = "bytes"
        guard let response = HTTPURLResponse(url: url, statusCode: reply.status, httpVersion: "HTTP/1.1", headerFields: headers) else {
            task.didFailWithError(URLError(.cannotParseResponse))
            return
        }
        task.didReceive(response)
        task.didReceive(reply.data)
        task.didFinish()
    }

    private static func mimeType(for fileExtension: String) -> String {
        switch fileExtension.lowercased() {
        case "html", "htm":
            return "text/html; charset=utf-8"
        case "js", "mjs":
            return "text/javascript; charset=utf-8"
        case "css":
            return "text/css; charset=utf-8"
        case "json":
            return "application/json"
        case "wasm":
            return "application/wasm"
        case "woff2":
            return "font/woff2"
        case "woff":
            return "font/woff"
        case "ttf":
            return "font/ttf"
        case "otf":
            return "font/otf"
        case "png":
            return "image/png"
        case "webp":
            return "image/webp"
        case "avif":
            return "image/avif"
        case "gif":
            return "image/gif"
        case "jpg", "jpeg":
            return "image/jpeg"
        case "svg":
            return "image/svg+xml"
        case "ico":
            return "image/x-icon"
        case "ktx2":
            return "image/ktx2"
        case "txt":
            return "text/plain; charset=utf-8"
        case "xml":
            return "application/xml"
        case "mp3":
            return "audio/mpeg"
        case "m4a", "aac":
            return "audio/mp4"
        case "wav":
            return "audio/wav"
        case "ogg", "oga":
            return "audio/ogg"
        case "mp4", "m4v":
            return "video/mp4"
        case "webm":
            return "video/webm"
        case "glb":
            return "model/gltf-binary"
        case "gltf":
            return "model/gltf+json"
        default:
            return "application/octet-stream"
        }
    }
}
