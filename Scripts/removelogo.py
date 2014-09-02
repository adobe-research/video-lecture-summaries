#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os

if __name__ == "__main__":
    """Removes logo from image.
    logo.png must be in same directory as image files.
    Replaces logo with black background."""
    
    dir_path = sys.argv[1]
    filelist = os.listdir(sys.argv[1])
    imagefiles = []
    logofiles = []
    for filename in filelist:
        if "capture" in filename:
            imagefiles.append(filename)
        if "logo" in filename and (".png" in filename or ".jpg" in filename):
            logofiles.append(filename)
            
    processed_path = dir_path + "\\removelogo"
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)
    
    for logofile in logofiles:        
     
        logo = cv2.imread(dir_path + "\\"+logofile)
        gray_logo = cv2.imread(dir_path + "\\"+logofile, 0)
        print dir_path + "\\" + logofile
        wlogo, hlogo = gray_logo.shape[::-1]
           
        for i in range(0, len(imagefiles)):
            img_path1 = dir_path + "\\" + imagefiles[i]
            if ("logo" in imagefiles[i]):
                continue
            print img_path1
            img1 = cv2.imread(img_path1)
            print img1.shape
            gray_img1 = cv2.imread(img_path1, 0)
            tlx, tly = pf.matchtemplate(gray_img1, gray_logo)
            brx = tlx + wlogo
            bry = tly + hlogo
            img1[tly:bry, tlx:brx, 0] = 255
            img1[tly:bry, tlx:brx, 1] = 255
            img1[tly:bry, tlx:brx, 2] = 255
            
            cv2.imwrite(processed_path+"\\"+imagefiles[i], img1)
           
    