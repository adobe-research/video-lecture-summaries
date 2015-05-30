#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
import util

if __name__ == "__main__":
    
    dir_path = sys.argv[1]
    filelist = os.listdir(sys.argv[1])
    imagefiles = []
    for filename in filelist:
        if ".png" in filename:
            imagefiles.append(filename)
            
#     processed_path = dir_path + "/negatefg"
#     if not os.path.exists(processed_path):
#         os.makedirs(processed_path)
#             
    for i in range(0, len(imagefiles)):
        img_path1 = dir_path + "/" + imagefiles[i]
        img1 = cv2.imread(img_path1)
        newimg = img1.copy()
        mask1 = pf.fgmask(img1, threshold=200, inv=False) #below
#         mask2 = pf.fgmask(img1, threshold=200, inv=True) #above
#         mask = cv2.bitwise_and(mask1, mask2)
#         util.showimages([mask1, mask2, mask])
        mask = mask1
        reverse_img = 255-img1
        util.showimages([img1, mask, reverse_img])
        idx = (mask!=0)
        newimg[idx] = reverse_img[idx]
        util.showimages([img1, newimg])
        
#         cv2.imwrite(processed_path+"/"+imagefiles[i], reverse_img)
        
    