//
//  LoginViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 01/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase

class LoginViewController: UIViewController {

    @IBOutlet weak var emailTextField: UITextField!
    @IBOutlet weak var passwordTextField: UITextField!
    @IBOutlet weak var submitButton: UIButton!
    
    // setting up firestore
    var db: Firestore!
    
    // temporary username and password to make logging in quick
    // these will be auto loaded into the login form upon load
    let username = "admin@petsback.me"
    let password = "password"
    
    override func viewDidLoad() {
        super.viewDidLoad()

        db = Firestore.firestore()
        // loading the email and password viariables into the labels on the storyboard
        emailTextField.text = username
        passwordTextField.text = password
    }
    
    @IBAction func loginWithEmailAndPass(_ sender: UIButton) {
        // grabbing the email and password from the login form and using it to login to petsback
        let email = emailTextField.text
        let pass = passwordTextField.text
        
        // authorising the login
        Auth.auth().signIn(withEmail: email!, password: pass!) { (user, error) in
            // if there is an error then print it to the console
            if error != nil {
                print(error!)
                // else perform segue to the new screen
            } else {
                print("Log in successful")
                // this is the code that segues the screens
                self.performSegue(withIdentifier: "goToHome", sender: self)
            }
            
        }
    }
    
}
