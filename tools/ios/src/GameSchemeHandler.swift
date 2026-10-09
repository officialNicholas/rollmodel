import Foundation
import WebKit

/// Serves the bundled game from a private address (rollmodel://localhost), so it runs offline and its saved name,
/// color and best scores stay put between launches.
final class GameSchemeHandler: NSObject, WKURLSchemeHandler {

    static let scheme = "rollmodel"
    static let startURL = URL(string: "rollmodel://localhost/index.html")!

    private let root: URL? = Bundle.main.url(forResource: "Game", withExtension: nil)

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(URLError(.badURL))
            return
        }
        guard let root = root else {
            urlSchemeTask.didFailWithError(URLError(.fileDoesNotExist))
            return
        }

        var path = url.path
        if path.isEmpty || path == "/" {
            path = "/index.html"
        }
        let rootPath = root.standardizedFileURL.path
        let fileURL = root.appendingPathComponent(String(path.dropFirst())).standardizedFileURL

        // Only files inside the Game folder are ever served.
        guard fileURL.path.hasPrefix(rootPath + "/"), let data = try? Data(contentsOf: fileURL) else {
            respond(to: urlSchemeTask, url: url, status: 404, mimeType: "text/plain; charset=utf-8", data: Data("Not found".utf8))
            return
        }
        respond(to: urlSchemeTask, url: url, status: 200, mimeType: GameSchemeHandler.mimeType(for: fileURL.pathExtension), data: data)
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {
        // Every response is sent in full inside start, so there is nothing left to cancel.
    }

    private func respond(to task: WKURLSchemeTask, url: URL, status: Int, mimeType: String, data: Data) {
        let headers = [
            "Content-Type": mimeType,
            "Content-Length": String(data.count),
            "Cache-Control": "no-cache"
        ]
        guard let response = HTTPURLResponse(url: url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: headers) else {
            task.didFailWithError(URLError(.cannotParseResponse))
            return
        }
        task.didReceive(response)
        task.didReceive(data)
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
        case "woff2":
            return "font/woff2"
        case "woff":
            return "font/woff"
        case "png":
            return "image/png"
        case "jpg", "jpeg":
            return "image/jpeg"
        case "svg":
            return "image/svg+xml"
        case "txt":
            return "text/plain; charset=utf-8"
        case "mp3":
            return "audio/mpeg"
        default:
            return "application/octet-stream"
        }
    }
}
