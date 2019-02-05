//
//  CustomCell.swift
//  petsback
//
//  Created by Brandan McDevitt on 05/02/2019.
//  Copyright © 2019 Brandan McDevitt. All rights reserved.
//

import Foundation
import UIKit

class CustomCell: UITableViewCell {
    // setting up the UI elements within my cell in the table view
    @IBOutlet weak var cellThumbnail: UIImageView!
    @IBOutlet weak var cellName: UILabel!
    @IBOutlet weak var cellLocation: UILabel!
    @IBOutlet weak var cellPostCode: UILabel!
    @IBOutlet weak var cellBackground: UIView!
    
}
