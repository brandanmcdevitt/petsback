//
//  UpdateInfoViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 20/05/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase

class UpdateInfoViewController: UIViewController {

    @IBOutlet weak var usernameInput: UITextField!
    @IBOutlet weak var emailInput: UITextField!
    @IBOutlet weak var forenameInput: UITextField!
    @IBOutlet weak var surnameInput: UITextField!
    @IBOutlet weak var contactInput: UITextField!
    @IBOutlet weak var addressInput: UITextField!
    @IBOutlet weak var cityInput: UITextField!
    @IBOutlet weak var postcodeInput: UITextField!
    
    var user_id: String?
    var cellCount = 0
    
    var handle: AuthStateDidChangeListenerHandle?

    override func viewDidLoad() {
        super.viewDidLoad()
        
        usernameInput.isEnabled = false
        emailInput.isEnabled = false

        // Do any additional setup after loading the view.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        handle = Auth.auth().addStateDidChangeListener { (auth, user) in
            if let user = user {
                self.user_id = user.uid
                self.usernameInput.text = user.displayName
                self.emailInput.text = user.email
            }
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        Auth.auth().removeStateDidChangeListener(handle!)
    }

    @IBAction func submitPressed(_ sender: UIButton) {
        let db = Firestore.firestore()
        let docRef = db.collection("user_details").document(user_id!)
        if forenameInput.text != "" {
            docRef.updateData(["forename": forenameInput.text!])
        }
        if surnameInput.text != "" {
            docRef.updateData(["surname": surnameInput.text!])
        }
        if contactInput.text != "" {
            docRef.updateData(["number": contactInput.text!])
        }
        if addressInput.text != "" {
            docRef.updateData(["address": addressInput.text!])
        }
        if cityInput.text != "" {
            docRef.updateData(["city": cityInput.text!])
        }
        if postcodeInput.text != "" {
            docRef.updateData(["postcode": postcodeInput.text!])
        }
        
        _ = navigationController?.popViewController(animated: true)
    }
}
