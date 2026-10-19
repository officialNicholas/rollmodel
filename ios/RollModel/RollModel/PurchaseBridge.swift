import Foundation
import StoreKit
import WebKit

/// Dab packs, bought with Apple's in-app purchase (StoreKit 2). Each pack is a consumable in App Store Connect; any one bought also
/// makes the game ad-free (the game keeps that in its save, and in the player's cloud save when signed in).
///
/// The game posts here as "iap":
/// - {ready} once its page is up: the packs' prices are fetched, and any purchase not yet handed to the game (one bought just before the
///   app closed, one approved later by a parent with Ask to Buy) is handed over now.
/// - {buy: id} when the player taps a pack.
/// - {finish: tx} once the game has added a purchase's dabs and saved: only then is the transaction finished with Apple, so a purchase
///   is never lost between the payment and the save.
///
/// It hears back through a "nativeiap" window event: {e: "products", list: [{id, price, n}]}, {e: "bought", id, tx},
/// {e: "fail", id, why} (why: "cancel", "pending" (waiting for a parent or for payment to clear), "unverified", "unavailable", "error").
final class PurchaseBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "iap"

    /// The four packs and how many dabs each gives (the game keeps the same table; App Store Connect has these product IDs, as
    /// Consumables).
    static let packs: [String: Int] = [
        "studio.primeshots.rollmodel.dabs400": 400,
        "studio.primeshots.rollmodel.dabs2500": 2500,
        "studio.primeshots.rollmodel.dabs5500": 5500,
        "studio.primeshots.rollmodel.dabs12000": 12000,
    ]

    weak var webView: WKWebView?

    private var products: [String: Product] = [:]
    private var updates: Task<Void, Never>?
    /// Bought and verified, waiting for the game to say it has added them: transaction ID to the transaction.
    private var waiting: [UInt64: Transaction] = [:]
    private var pageReady = false

    override init() {
        super.init()
        // Purchases that arrive outside a tap (Ask to Buy approved, a payment that cleared later, a purchase made on another device of
        // the same account for the same app): held for the game like any other.
        updates = Task.detached { [weak self] in
            for await result in Transaction.updates {
                await self?.take(result)
            }
        }
    }

    deinit { updates?.cancel() }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any] else { return }
        if (body["ready"] as? Bool) == true {
            pageReady = true
            Task { await self.loadProducts(); await self.handOverUnfinished() }
        }
        if let id = body["buy"] as? String, !id.isEmpty { Task { await self.buy(id) } }
        if let tx = body["finish"] as? String, let n = UInt64(tx) { Task { await self.finish(n) } }
        if let tx = body["finish"] as? NSNumber { Task { await self.finish(tx.uint64Value) } }
    }

    // MARK: Products

    @MainActor
    private func loadProducts() async {
        do {
            let list = try await Product.products(for: Array(PurchaseBridge.packs.keys))
            for p in list { products[p.id] = p }
            let out: [[String: Any]] = list.map { ["id": $0.id, "price": $0.displayPrice, "n": PurchaseBridge.packs[$0.id] ?? 0] }
            send(["e": "products", "list": out])
        } catch {
            send(["e": "products", "list": [], "why": "error"])
        }
    }

    // MARK: Buying

    @MainActor
    private func buy(_ id: String) async {
        if products[id] == nil { await loadProducts() }
        guard let product = products[id] else {
            send(["e": "fail", "id": id, "why": "unavailable"])
            return
        }
        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                await take(verification)
            case .userCancelled:
                send(["e": "fail", "id": id, "why": "cancel"])
            case .pending:
                send(["e": "fail", "id": id, "why": "pending"])
            @unknown default:
                send(["e": "fail", "id": id, "why": "error"])
            }
        } catch {
            send(["e": "fail", "id": id, "why": "error"])
        }
    }

    /// A purchase from Apple: only one Apple has signed for this app and device counts. It's held until the game says it has the dabs.
    @MainActor
    private func take(_ result: VerificationResult<Transaction>) async {
        guard case .verified(let transaction) = result else {
            if case .unverified(let transaction, _) = result {
                send(["e": "fail", "id": transaction.productID, "why": "unverified"])
            }
            return
        }
        guard PurchaseBridge.packs[transaction.productID] != nil, transaction.revocationDate == nil else {
            await transaction.finish()
            return
        }
        waiting[transaction.id] = transaction
        if pageReady { hand(transaction) }
    }

    @MainActor
    private func hand(_ transaction: Transaction) {
        send(["e": "bought", "id": transaction.productID, "tx": String(transaction.id), "n": PurchaseBridge.packs[transaction.productID] ?? 0])
    }

    /// Purchases Apple still has open from before (the app closed between paying and saving): handed to the game again. The game
    /// remembers which transactions it has already added, so none is added twice.
    @MainActor
    private func handOverUnfinished() async {
        for await result in Transaction.unfinished {
            if case .verified(let transaction) = result, waiting[transaction.id] == nil,
               PurchaseBridge.packs[transaction.productID] != nil, transaction.revocationDate == nil {
                waiting[transaction.id] = transaction
            }
        }
        for transaction in waiting.values { hand(transaction) } // (each once; the game skips any it has already added)
    }

    @MainActor
    private func finish(_ id: UInt64) async {
        guard let transaction = waiting.removeValue(forKey: id) else { return }
        await transaction.finish()
    }

    // MARK: Helpers

    @MainActor
    private func send(_ detail: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: detail), let text = String(data: data, encoding: .utf8) else { return }
        webView?.evaluateJavaScript("window.dispatchEvent(new CustomEvent('nativeiap', { detail: \(text) }));", completionHandler: nil)
    }
}
