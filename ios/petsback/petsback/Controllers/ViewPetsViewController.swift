//
//  ViewPetsViewController.swift
//  petsback
//
//  Created by Brandan McDevitt on 01/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import UIKit
import Firebase
import Kingfisher

class ViewPetsViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    @IBOutlet weak var tableView: UITableView!
    @IBOutlet weak var stateControl: UISegmentedControl!
    
    var cellCount = 0
    var fallbackArray = [String]()
    var refArray = [String]()
    var nameArray = [String]()
    var locationArray = [String]()
    var postCodeArray = [String]()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        getData(state: "lost")
        
        tableView.rowHeight = 250
        
        
        // declare the delegate and datasource of the tableviews
        tableView.delegate = self
        tableView.dataSource = self

    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return cellCount
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell:CustomCell = self.tableView.dequeueReusableCell(withIdentifier: "myCell") as! CustomCell
        
        cell.cellBackground.layer.cornerRadius = 8
        cell.cellBackground.layer.masksToBounds = true
        cell.cellBackground.layer.borderColor = UIColor( red: 153/255, green: 153/255, blue:0/255, alpha: 1.0 ).cgColor
        cell.cellBackground.layer.borderWidth = 2.0
        
        // do/catch for populating the imageview
        do {
            var url = URL(string: "")
            //if fallback is equal to true then retrieve this fallback url
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
        
        cell.cellName.text = nameArray[indexPath.row]
        cell.cellLocation.text = locationArray[indexPath.row] + ", " + postCodeArray[indexPath.row]
        cell.cellPostCode.text = refArray[indexPath.row]
        
        return cell
    }
    
    // function for making the firestore connection
    func getData(state: String) {
        // connect to firestore and authenticate the user
        let db = Firestore.firestore()
        //let user = Auth.auth().currentUser

        // connect to the 'lost' collection on firestore
        db.collection(state).getDocuments() { (querySnapshot, err) in
            // if there is an error, print the error
            if let err = err {
                print("Error getting documents: \(err)")
                // else grab the data
            } else {
                // cellcount for counting the number of documents in the collection
                self.cellCount = querySnapshot!.documents.count
                // loop through the documents and fetch all data to append to differnt arrays
                for i in 0..<self.cellCount {
                    self.refArray.append(querySnapshot!.documents[i].data()["ref_no"] as! String)
                    self.nameArray.append(querySnapshot!.documents[i].data()["name"] as! String)
                    self.locationArray.append(querySnapshot!.documents[i].data()["location"] as! String)
                    self.postCodeArray.append(querySnapshot!.documents[i].data()["postcode"] as! String)
                    self.fallbackArray.append(querySnapshot!.documents[i].data()["fallback"] as! String)
                }
                // reload the tableview once data has been populated
                self.tableView.reloadData()
            }
        }
    }
    
    @IBAction func stateChanged(_ sender: UISegmentedControl) {
        if sender.selectedSegmentIndex == 0 {
            
        }
    }
    

}
