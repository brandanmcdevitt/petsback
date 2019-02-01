//
//  HomeViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 01/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase

class HomeViewController: UIViewController {

    @IBOutlet weak var homeLabel: UILabel!
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // connect to firestore and authenticate the user
        let db = Firestore.firestore()
        let user = Auth.auth().currentUser
        
        // if the user is authenticated then get user details and display them in the labels
        if let user = user {
            let email = user.email
            let displayName = user.displayName
            
            homeLabel.text = email
            
        }

    }

}
