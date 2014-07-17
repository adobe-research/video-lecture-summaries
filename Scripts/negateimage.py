#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os

if __name__ == "__main__":
    
    dir_path = sys.argv[1]
    filelist = os.listdir(sys.argv[1])
    imagefiles = []
    for filename in filelist:
        if ".png" in filename:
            imagefiles.append(filename)
            
    processed_path = dir_path + "\\negate"
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)
    
        
    for i in range(0, len(imagefiles)):
        img_path1 = dir_path + "\\" + imagefiles[i]
        img1 = cv2.imread(img_path1)
        reverse_img = 255-img1
        cv2.imwrite(processed_path+"\\"+imagefiles[i], reverse_img)
        
    