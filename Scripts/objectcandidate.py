#!/usr/bin/env python
import numpy as np


class ObjectCandidate:
    def __init__(self, image, keypoints):
        self.image = image
        self.keypoints = keypoints
        pointsx = []
        pointsy = []
        self.points = []
        for point in keypoints:
            pointsx.append(point.pt[0])
            pointsy.append(point.pt[1])
            self.points.append(point.pt)
        
        self.tlx = np.floor(np.amin(pointsx))
        self.tly = np.floor(np.amin(pointsy))
        self.brx = np.ceil(np.amax(pointsx))
        self.bry = np.ceil(np.amax(pointsy))
        self.ctr = ((self.tlx+self.brx)/2.0, (self.tly + self.bry)/2.0)
 
        
        
        
        

    
        
