//
//  BreedCheckerViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 27/05/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Photos

private let classifier = ImageClassifier()

class BreedCheckerViewController: UIViewController, UINavigationControllerDelegate, UIImagePickerControllerDelegate {

    @IBOutlet weak var imageButton: UIButton!
    var thumbImage: URL?
    
    @IBOutlet weak var resultsLabel: UILabel!
    override func viewDidLoad() {
        super.viewDidLoad()
        
        resultsLabel.text = "Upload a photo of your pet and our system will give you the closest match!"
        resultsLabel.sizeToFit()
        resultsLabel.numberOfLines = 0

        // Do any additional setup after loading the view.
    }
    @IBAction func upload(_ sender: UIButton) {
        let image = UIImagePickerController()
        image.delegate = self
        image.sourceType = UIImagePickerController.SourceType.photoLibrary
        
        image.allowsEditing = false
        
        self.present(image, animated: true) {
            //after completion
        }
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        if let image = info[UIImagePickerController.InfoKey.originalImage] as? UIImage, let cgImage = image.cgImage {
            imageButton.setImage(image, for: .normal)
            thumbImage = info[UIImagePickerController.InfoKey.imageURL] as? URL
            classifier.classifyImageWithVision(image: cgImage) { (results) in
                DispatchQueue.main.async {
                    self.resultsLabel.text = results
                }
            }
        } else {
            //error
        }
        
        self.dismiss(animated: true, completion: nil)
    }
}
