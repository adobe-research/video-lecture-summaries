#!/usr/bin/env python
import cv2
import numpy as np
import math
import sys
import processframe as pf
import processscript as ps
from video import Video, Keyframe
from lecture import Lecture
from PIL import Image
import os
import util

def get_logos(dirname):
    logos = []
    
    if not os.path.exists(dirname):
        return logos
    
    filelist = os.listdir(dirname)
    for filename in filelist:
        if ('logo' in filename and 'png' in filename):
            logo = cv2.imread(dirname + "\\" + filename)
            logos.append(logo)
    return logos

if __name__ == "__main__":
  
    framedir = sys.argv[1]
    logodir = sys.argv[2]
    keyframes = Keyframe.get_keyframes(framedir)
    logos = get_logos(logodir)

    util.showimages(logos)

    print "Removing Logo from each Key frame"
    for keyframe in keyframes:
        keyframe.add_default_objs(logos)
    
    print "Detecting New Objects in each Key frame"
    prevframe = None
    for keyframe in keyframes:
        if (prevframe == None):
            prev_obj = []
        else:
            prev_obj = [prevframe.get_fgobj(includelogo=True)]
        keyframe.set_newobj_mask(prev_obj)
        prevframe  = keyframe    
    
    list_of_frames = []
    for keyframe in keyframes:
        if (keyframe.new_visual_score() > 0):
            frame = pf.maskimage_white(keyframe.frame, keyframe.fg_mask)            
            list_of_frames.append(frame)
    
    print "Stitching Panorama"        
    panorama = pf.panorama(list_of_frames)
    
    cv2.imwrite(framedir + "\\panorama_new.png", panorama)
    cv2.imshow("panorama", panorama)
    cv2.waitKey(0)