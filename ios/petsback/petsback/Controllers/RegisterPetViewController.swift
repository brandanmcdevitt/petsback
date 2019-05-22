//
//  RegisterPetViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 20/05/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase
import Amazons3

class RegisterPetViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
    
    let db = Firestore.firestore()

    @IBOutlet weak var imageButton: UIButton!
    @IBOutlet weak var nameInput: UITextField!
    @IBOutlet weak var colourInput: UITextField!
    @IBOutlet weak var sexInput: UITextField!
    @IBOutlet weak var breedInput: UITextField!
    @IBOutlet weak var cityInput: UITextField!
    @IBOutlet weak var postcodeInput: UITextField!
    @IBOutlet weak var animalTypeInput: UITextField!
    @IBOutlet var myView: UIView!
    
    var fallback: Bool = true
    
    let animalPicker = UIPickerView()
    let animalData = ["Select","Dog", "Cat", "Rabbit", "Bird", "Horse", "Other"]
    
    let datePicker = UIDatePicker()
    
    var user_id: String?
    var refNo: String?
    
    var handle: AuthStateDidChangeListenerHandle?
    
    var thumbImage: URL?
    
    var vSpinner : UIView?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        animalTypeInput.inputView = animalPicker
        
        animalPicker.delegate = self
    }

    @IBAction func submitPressed(_ sender: UIButton) {
        refNo = "PBMER" + String(Int.random(in: 100000...999999))
        
        showSpinner(onView: myView)
        
        if fallback == false {
            
            let credentials = AmazonCredentials(bucketName: S3_VARS.bucketName, accessKey: S3_VARS.accessKey, secretKey: S3_VARS.secretKey, region: .EUWest2)
            
            AmazonUploader.setup(credentials: credentials)
            
            AmazonUploader.shared.uploadFile(fileUrl: thumbImage!, keyName: "\(refNo!).jpg", permission: .publicRead) { (success, url, error) in
                
                if success {
                    print("success")
                    self.removeSpinner()
                    self.performSegue(withIdentifier: "goToMyPet", sender: self)
                }else{
                    print(error!)
                }
            }
        }
        
        db.collection("reg_pet").document(NSUUID().uuidString.lowercased()).setData([
            "name": nameInput.text!,
            "colour": colourInput.text!,
            "breed": breedInput.text!,
            "location": cityInput.text!,
            "postcode": postcodeInput.text!,
            "animal": animalTypeInput.text!,
            "ref_no": refNo,
            "fallback": String(fallback),
            "user_id": user_id
        ]) { err in
            if let err = err {
                print("Error writing document: \(err)")
            } else {
                print("Document added.")
            }
        }
        
        if fallback == true {
            self.performSegue(withIdentifier: "goToMyPet§", sender: self)
        }
    }
    
    override func viewWillAppear(_ animated: Bool) {
        handle = Auth.auth().addStateDidChangeListener { (auth, user) in
            if let user = user {
                // The user's ID, unique to the Firebase project.
                // Do NOT use this value to authenticate with your backend server,
                // if you have one. Use getTokenWithCompletion:completion: instead.
                self.user_id = user.uid
            }
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        Auth.auth().removeStateDidChangeListener(handle!)
    }
    
    @IBAction func imageUploaded(_ sender: UIButton) {
        let image = UIImagePickerController()
        image.delegate = self
        image.sourceType = UIImagePickerController.SourceType.photoLibrary
        
        image.allowsEditing = false
        fallback = false
        
        self.present(image, animated: true) {
            //after completion
        }
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        if let image = info[UIImagePickerController.InfoKey.originalImage] as? UIImage {
            imageButton.setImage(image, for: .normal)
            thumbImage = info[UIImagePickerController.InfoKey.imageURL] as? URL
        } else {
            //error
        }
        
        self.dismiss(animated: true, completion: nil)
    }
    
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
    
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return animalData.count
    }
    
    func pickerView( _ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        return animalData[row]
    }
    
    func pickerView( _ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        animalTypeInput.text = animalData[row]
        self.view.endEditing(true)
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // if the identifier is equal to "goToDetails" then set the destination view controller and pass over information
        if segue.identifier == "goToDetails" {
            let destinationVC = segue.destination as! PetDetailsViewController
            destinationVC.refNo = refNo
        }
        
    }
    
    func showSpinner(onView : UIView) {
        let spinnerView = UIView.init(frame: onView.bounds)
        spinnerView.backgroundColor = UIColor.init(red: 0.5, green: 0.5, blue: 0.5, alpha: 0.5)
        let ai = UIActivityIndicatorView.init(style: .whiteLarge)
        ai.startAnimating()
        ai.center = spinnerView.center
        
        DispatchQueue.main.async {
            spinnerView.addSubview(ai)
            onView.addSubview(spinnerView)
        }
        
        vSpinner = spinnerView
    }
    
    func removeSpinner() {
        DispatchQueue.main.async {
            self.vSpinner?.removeFromSuperview()
            self.vSpinner = nil
        }
    }
}
