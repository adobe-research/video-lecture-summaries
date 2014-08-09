#!/usr/bin/env python
import cv2
import numpy as np
import math
import processframe as pf
import sys
import os

if __name__ == "__main__":
  
    dir_path = sys.argv[1]
    filelist = os.listdir(dir_path)
    imagefiles = []
    image_list = []
    avg_lum = 0     # average luminance of keyframes used as foreground threshold
    
    # read all keyframes
    for filename in filelist:
        if "capture" in filename and "png" in filename:
            #print filename
            imagefiles.append(filename)
            image = cv2.imread(dir_path + "\\" + filename)
            image_list.append(image)          
            avg_lum += np.mean(image)
            #var = np.std(image, 2)
            #maximum = np.amax(var)
            #minimum = np.amin(var)
            #print maximum, minimum
            #plt.imshow(var, cmap='gray')
            #plt.show()
            
    avg_lum /= len(imagefiles)
    lum_thres = avg_lum * 0.8
        
    # extract and crop to foreground
    fgcropdir = dir_path + "\\foreground_crop"
    if not os.path.exists(fgcropdir):
      os.makedirs(fgcropdir)
      
    fgcrop_image_list =  []
    for i in range(0, len(imagefiles)):      
      image = image_list[i]
      lum_mask = pf.fgmask(image, lum_thres)
      hue_mask = pf.fgmask_hue(image)
      fg_mask = cv2.bitwise_or(lum_mask, hue_mask)
      fg_img = pf.maskimage_white(image, fg_mask)
      tlx, tly, brx, bry = pf.fgbbox(fg_mask)
      fgcrop_image = pf.cropimage(fg_img, tlx, tly, brx, bry)
      if fgcrop_image != None:
        cv2.imwrite(fgcropdir + "\\" + imagefiles[i], fgcrop_image)