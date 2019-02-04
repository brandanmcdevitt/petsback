//
//  RegisterViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 04/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase

class RegisterViewController: UIViewController {

    @IBOutlet weak var emailTextField: UITextField!
    @IBOutlet weak var passwordTextField: UITextField!
    override func viewDidLoad() {
        super.viewDidLoad()
        
    }
    @IBAction func submitPressed(_ sender: UIButton) {
        Auth.auth().createUser(withEmail: emailTextField.text!, password: passwordTextField.text!) { (authResult, error) in
            // ...
            guard let user = authResult?.user else { return }
            
            self.performSegue(withIdentifier: "goToHome", sender: self)
        }
    }
    
}
