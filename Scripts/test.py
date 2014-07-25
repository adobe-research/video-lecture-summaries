#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
from PIL import Image
import images2gif
import processvideo
from sentence import Sentence
import processscript as ps


if __name__ == "__main__":
    
    
    scriptpath = sys.argv[1]
    scriptfile = os.path.basename(scriptpath)
    endtime = sys.argv[2]
    endtime = ps.time_in_sec(endtime)
    videopath = sys.argv[3]
    framepath = sys.argv[4]
    
    pv = processvideo.ProcessVideo(videopath)
    sentences = ps.get_sentences(scriptpath, endtime)
    
    keyframes = []
    filelist = os.listdir(framepath)
    for filename in filelist:
        if "capture" in filename and ".png" in filename:
            keyframes.append(filename)
        
    
        