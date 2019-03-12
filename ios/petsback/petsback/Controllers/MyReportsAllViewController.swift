//
//  MyReportsAllViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 12/03/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase
import Kingfisher

class MyReportsAllViewController: UIViewController,  UITableViewDelegate, UITableViewDataSource {
    @IBOutlet weak var tableView: UITableView!
    @IBOutlet weak var stateChanged: UISegmentedControl!
    
    var cellCount = 0
    var fallbackArray = [String]()
    var refArray = [String]()
    var nameArray = [String]()
    var locationArray = [String]()
    var postCodeArray = [String]()
    var breedArray = [String]()
    var refNo = ""
    var user_id: String?
    
    var handle: AuthStateDidChangeListenerHandle?
    
    override func viewDidLoad() {
        super.viewDidLoad()

        tableView.rowHeight = 250
        
        // declare the delegate and datasource of the tableviews
        tableView.delegate = self
        tableView.dataSource = self
    }
    
    override func viewDidAppear(_ animated: Bool) {
        handle = Auth.auth().addStateDidChangeListener { (auth, user) in
            if let user = user {
                // The user's ID, unique to the Firebase project.
                // Do NOT use this value to authenticate with your backend server,
                // if you have one. Use getTokenWithCompletion:completion: instead.
                self.user_id = user.uid
            }
        }
        getData(state: "lost")
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        Auth.auth().removeStateDidChangeListener(handle!)
    }
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return cellCount
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell:CustomCell = self.tableView.dequeueReusableCell(withIdentifier: "myCell") as! CustomCell
        
        cell.cellBackground.layer.cornerRadius = 8
        cell.cellBackground.layer.masksToBounds = true
        cell.cellBackground.layer.borderColor = UIColor(red:0.78, green:0.40, blue:0.40, alpha:1.0).cgColor
        cell.cellBackground.layer.borderWidth = 2.0
        
        // do/catch for populating the imageview
        do {
            var url = URL(string: "")
            //if fallback is equal to true then retrieve this fallback url
            print(fallbackArray[indexPath.row])
            if fallbackArray[indexPath.row] == "true" {
                url = URL(string: "http://pets-back-me.s3.eu-west-2.amazonaws.com/fallback.jpg")
                // else retrieve the url based on the refNo in refArray
            } else {
                url = URL(string: "http://pets-back-me.s3.eu-west-2.amazonaws.com/\(refArray[indexPath.row]).jpg")
            }
            // using kingfisher to populate the imageView
            cell.cellThumbnail.kf.setImage(with: url)
        }
            // print any errors
        catch{
            print(error)
        }
        
        if nameArray.count != 0 {
            cell.cellName.text = nameArray[indexPath.row] + " - " + breedArray[indexPath.row]
        } else {
            cell.cellName.text = breedArray[indexPath.row]
        }
        cell.cellLocation.text = locationArray[indexPath.row] + ", " + postCodeArray[indexPath.row]
        cell.cellPostCode.text = refArray[indexPath.row]
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        refNo = refArray[indexPath.row]
        
        performSegue(withIdentifier: "goToDetails", sender: self)
    }
    
    // function for making the firestore connection
    func getData(state: String) {
        // connect to firestore and authenticate the user
        let db = Firestore.firestore()
        //let user = Auth.auth().currentUser
        
        // connect to the 'lost' or 'found' collection on firestore
        db.collection(state).getDocuments() { (querySnapshot, err) in
            // if there is an error, print the error
            if let err = err {
                print("Error getting documents: \(err)")
                // else grab the data
            } else {
                // cellcount for counting the number of documents in the collection
                //self.cellCount = querySnapshot!.documents.count
                
                self.refArray.removeAll()
                self.nameArray.removeAll()
                self.fallbackArray.removeAll()
                self.locationArray.removeAll()
                self.postCodeArray.removeAll()
                self.breedArray.removeAll()
                self.cellCount = 0
                // loop through the documents and fetch all data to append to differnt arrays
                for i in 0..<querySnapshot!.documents.count {
                    if self.user_id! == querySnapshot!.documents[i].data()["user_id"] as! String {
                        
                        if state == "lost" {
                            self.nameArray.append(querySnapshot!.documents[i].data()["name"] as! String)
                        }
                        self.refArray.append(querySnapshot!.documents[i].data()["ref_no"] as! String)
                        self.locationArray.append(querySnapshot!.documents[i].data()["location"] as! String)
                        self.postCodeArray.append(querySnapshot!.documents[i].data()["postcode"] as! String)
                        self.fallbackArray.append(querySnapshot!.documents[i].data()["fallback"] as! String)
                        self.breedArray.append(querySnapshot!.documents[i].data()["breed"] as! String)
                        
                        self.cellCount += 1
                    }
                }
                // reload the tableview once data has been populated
                self.tableView.reloadData()
            }
        }
    }
    
    @IBAction func stateChanged(_ sender: UISegmentedControl) {
        if sender.selectedSegmentIndex == 0 {
            getData(state: "lost")
        } else if sender.selectedSegmentIndex == 1 {
            getData(state: "found")
        }
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // if the identifier is equal to "goToDetails" then set the destination view controller and pass over information
        if segue.identifier == "goToDetails" {
            let destinationVC = segue.destination as! PetDetailsViewController
            destinationVC.refNo = refNo
        }
        
    }

}
