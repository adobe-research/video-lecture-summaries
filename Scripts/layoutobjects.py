#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
import scipy as sp

if __name__ == "__main__":

    filelist = os.listdir(sys.argv[1])
    objectfiles = []
    objects = []
    maxw = 0
    totalh = 0
    for filename in filelist:
        if "capture" in filename and "feature" not in filename:
            objectfiles.append(filename)
            obj_img = cv2.imread(sys.argv[1] + "\\" + filename)
            objects.append(obj_img)
            print sys.argv[1] + "\\" + filename
            h, w = obj_img.shape[:2]
            maxw = max(maxw, w)
            totalh += h
            
    
    view = sp.zeros((totalh, maxw, 3), sp.uint8)
    view[:,:,:] = (255, 255, 255)
    curh = 0
    curw = 0

    for obj in objects:
       
        h,w = obj.shape[:2]
        curw = w
        view[curh:curh+h, (maxw-curw)/2:(maxw-curw)/2+curw, :] = obj
        curh += h
    
    cv2.namedWindow("vew", cv2.WINDOW_NORMAL)
    cv2.imshow("vew", view)
    cv2.waitKey(0)
    cv2.imwrite("capture_sum.jpg", view)