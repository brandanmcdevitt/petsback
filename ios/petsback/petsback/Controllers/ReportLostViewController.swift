//
//  ReportLostViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 11/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase
import Amazons3

class ReportLostViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
    
    let db = Firestore.firestore()
    
    @IBOutlet weak var nameTextField: UITextField!
    @IBOutlet weak var ageTextField: UITextField!
    @IBOutlet weak var colourTextField: UITextField!
    @IBOutlet weak var breedTextField: UITextField!
    @IBOutlet weak var locationTextField: UITextField!
    @IBOutlet weak var postcodeTextField: UITextField!
    @IBOutlet weak var animalTypeTextField: UITextField!
    @IBOutlet weak var dateMissingTextField: UITextField!
    @IBOutlet weak var collarCheck: CheckboxButton!
    @IBOutlet weak var chippedCheck: CheckboxButton!
    @IBOutlet weak var neuteredCheck: CheckboxButton!
    @IBOutlet weak var imageButton: UIButton!
    
    var collar: Bool = false
    var chipped: Bool = false
    var neutered: Bool = false
    var fallback: Bool = true
    
    let animalPicker = UIPickerView()
    let animalData = ["Dog", "Cat", "Rabbit", "Bird", "Horse", "Other"]
    
    let datePicker = UIDatePicker()
    
    var user_id: String?
    var refNo: String?
    
    var handle: AuthStateDidChangeListenerHandle?
    
    var thumbImage: URL?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        animalTypeTextField.inputView = animalPicker
        
        animalPicker.delegate = self
        
        //create a toolbar
        let toolbar = UIToolbar()
        toolbar.sizeToFit()
        
        //add a done button on this toolbar
        let doneButton = UIBarButtonItem(barButtonSystemItem: .done, target: nil, action: #selector(doneClicked))
        
        toolbar.setItems([doneButton], animated: true)
        
        //datePicker.inputAccessoryView = toolbar
        toolbar.isUserInteractionEnabled = true
        //datePicker.addSubview(toolbar)
        dateMissingTextField.inputView = datePicker
        dateMissingTextField.inputAccessoryView = toolbar
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
    
    @objc func doneClicked(){
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .medium
        dateFormatter.timeStyle = .none
        
        dateMissingTextField.text = dateFormatter.string(from: datePicker.date)
        self.view.endEditing(true)
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
    
    @IBAction func collarCheckChange(_ sender: Any) {
        if collarCheck.on {
            collar = true
        } else if !collarCheck.on {
            collar = false
        }
    }
    @IBAction func chippedCheckChange(_ sender: Any) {
        if chippedCheck.on {
            chipped = true
        } else if !chippedCheck.on {
            chipped = false
        }
    }
    
    @IBAction func neuteredCheckChange(_ sender: Any) {
        if neuteredCheck.on {
            neutered = true
        } else if !neuteredCheck.on {
            neutered = false
        }
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
        animalTypeTextField.text = animalData[row]
        self.view.endEditing(true)
    }
    @IBAction func submittedForm(_ sender: Any) {
        refNo = "PBMEL" + String(Int.random(in: 100000...999999))
        
        let credentials = AmazonCredentials(bucketName: S3_VARS.bucketName, accessKey: S3_VARS.accessKey, secretKey: S3_VARS.secretKey, region: .EUWest2)
        
        AmazonUploader.setup(credentials: credentials)
        
        AmazonUploader.shared.uploadFile(fileUrl: thumbImage!, keyName: "\(refNo!).jpg", permission: .publicRead) { (success, url, error) in
            
            if success {
                print("success")
            }else{
                print(error!)
            }
        }
        
        db.collection("lost").document(NSUUID().uuidString.lowercased()).setData([
            "name": nameTextField.text!,
            "age": Int(ageTextField.text!),
            "colour": colourTextField.text!,
            "breed": breedTextField.text!,
            "location": locationTextField.text!,
            "postcode": postcodeTextField.text!,
            "animal": animalTypeTextField.text!,
            "missing_since": datePicker.date,
            "collar": collar,
            "chipped": chipped,
            "neutered": neutered,
            "post_date": Date.init(timeIntervalSinceNow: 0),
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
        
        performSegue(withIdentifier: "goToDetails", sender: self)
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // if the identifier is equal to "goToDetails" then set the destination view controller and pass over information
        if segue.identifier == "goToDetails" {
            let destinationVC = segue.destination as! PetDetailsViewController
            destinationVC.refNo = refNo
        }
        
    }
    
}
