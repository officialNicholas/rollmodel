import UIKit
import WebKit

/// The player picks upright or wide play when the game first opens, and can change it in Settings. The game posts that choice
/// here as "port", "land" or "" (no preference), and the iPhone turns to match. iPad already turns freely, so it's left as it is.
final class OrientBridge: NSObject, WKScriptMessageHandler {

    static let messageName = "orient"

    weak var viewController: UIViewController?

    /// What the iPhone may turn to: upright until the game says otherwise.
    private(set) var mask: UIInterfaceOrientationMask = .portrait

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        let choice = message.body as? String ?? ""
        let next: UIInterfaceOrientationMask = choice == "land" ? .landscape : (choice == "port" ? .portrait : .allButUpsideDown)
        guard next != mask else { return }
        mask = next
        guard let viewController = viewController, UIDevice.current.userInterfaceIdiom == .phone else { return }
        if #available(iOS 16.0, *) {
            viewController.setNeedsUpdateOfSupportedInterfaceOrientations()
            viewController.view.window?.windowScene?.requestGeometryUpdate(.iOS(interfaceOrientations: next)) { _ in
                // Refused (say the player has Rotation Lock on): the game shows its "turn your phone" card instead.
            }
        } else {
            // iOS 15: turn the device's orientation, then let UIKit settle on what the controller now allows.
            if choice == "land" || choice == "port" {
                let target: UIInterfaceOrientation = choice == "land" ? .landscapeRight : .portrait
                UIDevice.current.setValue(target.rawValue, forKey: "orientation")
            }
            UIViewController.attemptRotationToDeviceOrientation()
        }
    }
}
