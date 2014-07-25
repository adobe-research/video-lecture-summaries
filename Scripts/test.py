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



if __name__ == "__main__":
    
    videopath = sys.argv[1]
    framepath = sys.argv[2]
    
    pv = processvideo.ProcessVideo(videopath)
    
    img1 = cv2.imread(sys.argv[1])
    img2 = cv2.imread(sys.argv[2])
    print 'here'
    
    GifWriter.writeGif("test.gif", [img1, img2], duration=1)
    