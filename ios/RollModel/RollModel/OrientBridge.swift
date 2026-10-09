import UIKit

/// Holds the orientation the game asked for. The page posts "port", "land" or "" (free) to the `orient` message handler
/// whenever the player picks one at launch or changes it in Settings.
final class OrientBridge {
    static let shared = OrientBridge()
    private(set) var mask: UIInterfaceOrientationMask = .all

    func apply(_ value: String, from viewController: UIViewController) {
        switch value {
        case "port": mask = .portrait
        case "land": mask = .landscape
        default: mask = .all
        }
        if #available(iOS 16.0, *) {
            viewController.setNeedsUpdateOfSupportedInterfaceOrientations()
            if let scene = viewController.view.window?.windowScene {
                scene.requestGeometryUpdate(.iOS(interfaceOrientations: mask)) { _ in }
            }
        } else {
            let target: UIInterfaceOrientation = value == "land" ? .landscapeRight : .portrait
            UIDevice.current.setValue(target.rawValue, forKey: "orientation")
            UIViewController.attemptRotationToDeviceOrientation()
        }
    }
}
