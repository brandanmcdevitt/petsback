//
//  MyPetDetailsViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 13/03/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase
import Kingfisher

class MyPetDetailsViewController: UIViewController {
    
    @IBOutlet weak var nameLabel: UILabel!
    @IBOutlet weak var thumbnail: UIImageView!
    @IBOutlet weak var refLabel: UILabel!
    @IBOutlet weak var locationLabel: UILabel!
    @IBOutlet weak var ageLabel: UILabel!
    @IBOutlet weak var colourLabel: UILabel!
    @IBOutlet weak var sexLabel: UILabel!
    @IBOutlet weak var breedLabel: UILabel!
    @IBOutlet weak var qrImage: UIImageView!
    
    var refNo : String? = nil
    var cellCount = 0

    override func viewDidLoad() {
        super.viewDidLoad()
        
        thumbnail.layer.cornerRadius = 8
        thumbnail.layer.masksToBounds = true
        
        getData(state: "reg_pet")

    }
    
    func getData(state: String) {
        
        // connect to firestore and get user details
        let db = Firestore.firestore()
        // connect to the 'lost' collection to pull information about lost pets
        db.collection(state).getDocuments() { (querySnapshot, err) in
        if let err = err {
            print("Error getting documents: \(err)")
        } else {
            // count the number of documents within the collection
            self.cellCount = querySnapshot!.documents.count
            // loop through the documents to find specific data
            for i in 0..<self.cellCount {
            let currentRef = querySnapshot!.documents[i].data()["ref_no"] as! String
            // if the current reference number is equal to the refNo passed in from the previous screen then get details
            if currentRef == self.refNo {
            // assign details from document matching refNo to the labels text
            let animal = querySnapshot!.documents[i].data()["animal"] as? String
            let location = querySnapshot!.documents[i].data()["location"] as? String
            let postcode = querySnapshot!.documents[i].data()["postcode"] as? String
            let breed = querySnapshot!.documents[i].data()["breed"] as? String
            let colour = querySnapshot!.documents[i].data()["colour"] as? String
            let sex = querySnapshot!.documents[i].data()["sex"] as? String
            
            let name = querySnapshot!.documents[i].data()["name"] as? String
            let age = querySnapshot!.documents[i].data()["age"] as? Int
            self.nameLabel.text = "\(name!)"
            self.refLabel.text = self.refNo
            self.locationLabel.text = "\(location!), \(postcode!)"
            self.colourLabel.text = colour
            self.sexLabel.text = sex
            self.breedLabel.text = breed
            
            let fallback = querySnapshot!.documents[i].data()["fallback"] as! String
            // do/catch for populating the imageView with the pets image hosted in Amazons S3 bucket
            do {
                var url = URL(string: "")
                var qrUrl = URL(string: "")
                // if fallback is true then set the url to retreive the fallback image
                if fallback == "true" {
                    url = URL(string: "http://pets-back-me.s3.eu-west-2.amazonaws.com/fallback.jpg")!
                // if fallback is false then set the url to retrieve the image based on the refNo
                } else {
                    url = URL(string: "http://pets-back-me.s3.eu-west-2.amazonaws.com/\(self.refNo!).jpg")!
                }
                qrUrl = URL(string: "https://s3.eu-west-2.amazonaws.com/pets-back-me/qr-\(self.refNo!).png")!
                print(qrUrl)
                // using kingfisher to display the image
                self.thumbnail.kf.setImage(with: url)
                self.qrImage.kf.setImage(with: qrUrl!)
            }
            // print any errors if there are any
            catch{
                print(error)
            }
            }
            }
            }
        }
        }

}
