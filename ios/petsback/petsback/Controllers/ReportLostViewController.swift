//
//  ReportLostViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 11/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase

class ReportLostViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource {
    
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
    
    var collar: Bool = false
    var chipped: Bool = false
    var neutered: Bool = false
    var fallback: Bool = true
    
    let animalPicker = UIPickerView()
    let animalData = ["Dog", "Cat", "Rabbit", "Bird", "Horse", "Other"]
    
    let datePicker = UIDatePicker()
    
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
    
    @objc func doneClicked(){
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .medium
        dateFormatter.timeStyle = .none
        
        dateMissingTextField.text = dateFormatter.string(from: datePicker.date)
        self.view.endEditing(true)
    }
    
    @IBAction func imageUploaded(_ sender: UIButton) {
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
        // Add a new document with a generated id.
        var ref: DocumentReference? = nil
        ref = db.collection("lost").addDocument(data: [
            "name": nameTextField.text!,
            "age": ageTextField.text!,
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
            "ref_no": "test_ref",
            "fallback": fallback,
            "user_id": ""
        ]) { err in
            if let err = err {
                print("Error adding document: \(err)")
            } else {
                print("Document added with ID: \(ref!.documentID)")
            }
        }
    }
    
}
