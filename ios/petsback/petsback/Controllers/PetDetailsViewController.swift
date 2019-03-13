//
//  PetDetailsViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 05/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase
import Kingfisher
import MapKit
import CoreLocation

class PetDetailsViewController: UIViewController {
    @IBOutlet weak var nameLabel: UILabel!
    @IBOutlet weak var thumbnail: UIImageView!
    @IBOutlet weak var refLabel: UILabel!
    @IBOutlet weak var locationLabel: UILabel!
    @IBOutlet weak var timeDateLabel: UILabel!
    @IBOutlet weak var ageLabel: UILabel!
    @IBOutlet weak var colourLabel: UILabel!
    @IBOutlet weak var sexLabel: UILabel!
    @IBOutlet weak var breedLabel: UILabel!
    @IBOutlet weak var petLocationMap: MKMapView!
    @IBOutlet weak var hasCollar: UIImageView!
    @IBOutlet weak var hasChip: UIImageView!
    @IBOutlet weak var collarLabel: UILabel!
    @IBOutlet weak var chipLabel: UILabel!
    
    // declaring refNo that will be populated by the previous screen upon segue
    var refNo : String? = nil
    // cell count will count the documents in firebase
    var cellCount = 0
    var locationForMapDefault = ""

    override func viewDidLoad() {
        super.viewDidLoad()
        if (refNo?.contains("PBMEL"))! {
            getData(state: "lost")
        } else if (refNo?.contains("PBMEF"))! {
            getData(state: "found")
        }
        
        thumbnail.layer.cornerRadius = 8
        thumbnail.layer.masksToBounds = true
    }
    
    func getLocation(defaultLocation: String) {
        let geocoder = CLGeocoder()
        
        geocoder.geocodeAddressString(defaultLocation) {
            placemarks, error in
            let placemark = placemarks?.first
            let lat = placemark?.location?.coordinate.latitude
            let lon = placemark?.location?.coordinate.longitude
            
            let initialLocation = CLLocation(latitude: lat ?? 54.5739396, longitude: lon ?? -5.9228062)
            
            let regionRadius: CLLocationDistance = 5999
            let coordinateRegion = MKCoordinateRegion(center: initialLocation.coordinate,
                                                          latitudinalMeters: regionRadius, longitudinalMeters: regionRadius)
            self.petLocationMap.setRegion(coordinateRegion, animated: true)
        }
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
                        let missingSince = querySnapshot!.documents[i].data()["missing_since"] as? Date
                        let dateFound = querySnapshot!.documents[i].data()["date_found"] as? Date
                        let collar = querySnapshot!.documents[i].data()["collar"] as? Bool
                        let chipped = querySnapshot!.documents[i].data()["chipped"] as? Bool
                        
                        self.locationForMapDefault = "\(location!), \(postcode!)"
                        self.getLocation(defaultLocation: self.locationForMapDefault)
                        
                        let newDateFormat = DateFormatter()
                        newDateFormat.dateFormat = "dd-MM-YYYY"
                        
                        if state == "lost" {
                            let date = newDateFormat.string(from: missingSince!)
                            let name = querySnapshot!.documents[i].data()["name"] as? String
                            let age = querySnapshot!.documents[i].data()["age"] as? Int
                            self.nameLabel.text = "Missing \(animal!) \(name!)"
                            self.ageLabel.text = "\(age!)"
                            self.timeDateLabel.text = "Went missing on \(date)"
                            if collar == true {
                                self.hasCollar.image = #imageLiteral(resourceName: "has_collar")
                                self.collarLabel.text = "Has collar"
                            } else {
                                self.hasCollar.image = #imageLiteral(resourceName: "no_collar")
                                self.collarLabel.text = "No collar"
                            }
                            
                            if chipped == true {
                                self.hasChip.image = #imageLiteral(resourceName: "has_chip")
                                self.chipLabel.text = "Chipped"
                            } else {
                                self.hasChip.image = #imageLiteral(resourceName: "no_chip")
                                self.chipLabel.text = "Not chipped"
                            }
                        } else if state == "found" {
                            let date = newDateFormat.string(from: dateFound!)
                            self.nameLabel.text = "Missing " + animal!
                            self.timeDateLabel.text = "Found on \(date)"
                            self.collarLabel.isHidden = true
                            self.chipLabel.isHidden = true
                        }
                        
                        self.refLabel.text = self.refNo
                        self.locationLabel.text = "\(location!), \(postcode!)"
                        self.colourLabel.text = colour
                        self.sexLabel.text = sex
                        self.breedLabel.text = breed
                        
                        let fallback = querySnapshot!.documents[i].data()["fallback"] as! String
                        // do/catch for populating the imageView with the pets image hosted in Amazons S3 bucket
                        do {
                            var url = URL(string: "")
                            // if fallback is true then set the url to retreive the fallback image
                            if fallback == "true" {
                                url = URL(string: "http://pets-back-me.s3.eu-west-2.amazonaws.com/fallback.jpg")!
                                // if fallback is false then set the url to retrieve the image based on the refNo
                            } else {
                                url = URL(string: "http://pets-back-me.s3.eu-west-2.amazonaws.com/\(self.refNo!).jpg")!
                            }
                            // using kingfisher to display the image
                            self.thumbnail.kf.setImage(with: url)
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
