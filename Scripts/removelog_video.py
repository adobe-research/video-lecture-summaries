#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
import processvideo as pv

if __name__ == "__main__":
    video = sys.argv[1]
    logodir = sys.argv[2]
    
    filelist = os.listdir(logodir)
    logofiles = []
    gray_logos = []
    for filename in filelist:
        if "logo" in filename and (".png" in filename or ".jpg" in filename):
            logofiles.append(filename)          
            gray_logo = cv2.imread(logodir+"\\"+filename, 0)
            gray_logos.append(gray_logo)
    
    video_obj = pv.ProcessVideo(video)
    video_obj.removelogo(gray_logos, (0, 0, 0))
    