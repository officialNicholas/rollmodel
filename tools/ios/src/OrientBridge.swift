import UIKit
import WebKit

/// The game asks for the way up the player picked (portrait or landscape, chosen on the first launch and in Settings).
/// The choice is kept here so the app opens the right way up next time, and the window follows it straight away.
final class OrientBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "orient"
    static let key = "orient"

    weak var controller: UIViewController?

    static var mask: UIInterfaceOrientationMask {
        switch UserDefaults.standard.string(forKey: key) ?? "" {
        case "land": return .landscape
        case "port": return .portrait
        default: return UIDevice.current.userInterfaceIdiom == .pad ? .all : .allButUpsideDown
        }
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let value = message.body as? String else { return }
        let was = UserDefaults.standard.string(forKey: OrientBridge.key) ?? ""
        if value.isEmpty { UserDefaults.standard.removeObject(forKey: OrientBridge.key) } else { UserDefaults.standard.set(value, forKey: OrientBridge.key) }
        guard value != was, let controller = controller else { return }
        if #available(iOS 16.0, *) {
            controller.setNeedsUpdateOfSupportedInterfaceOrientations()
            if let scene = controller.view.window?.windowScene {
                scene.requestGeometryUpdate(.iOS(interfaceOrientations: OrientBridge.mask)) { _ in }
            }
        } else {
            UIViewController.attemptRotationToDeviceOrientation()
        }
    }
}
