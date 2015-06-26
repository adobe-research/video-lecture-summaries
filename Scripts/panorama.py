#!/usr/bin/env python
import cv2
import sys
import processframe as pf
from video import Video, Keyframe
import framediff
import util
import removelogo
import numpy as np
import os
import matplotlib.pyplot as plt


def new_obj_panorama():
  
    framedir = sys.argv[1]
    logodir = sys.argv[2]
    keyframes = Keyframe.get_keyframes(framedir)
    logos = util.get_logos(logodir)

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
 
    
if __name__ == "__main__":
    """written on 6/26/2015"""

    videopath = sys.argv[1]
    numfgpixtxt = sys.argv[2]
    if (len(sys.argv) == 4):
        thres = int(sys.argv[3])
    else:
        thres = 1000
    
    video = Video(videopath)
    numfgpix = util.stringlist_from_txt(numfgpixtxt)
    counts = util.strings2ints(numfgpix)

    countdiffs = []
    for i in range(0, len(counts)-1):
        diff = abs(counts[i+1] - counts[i])
        countdiffs.append(diff)

    fid = 0
    last_unmoved_fid = 0
    capture = False
    keyframes_fid = []
    for diff in countdiffs:
        if diff > thres and not capture:
            keyframes_fid.append(fid)
            capture = True
        elif diff <= thres:
            capture = False
        fid += 1
    if len(keyframes_fid) == 0:
        keyframes_fid.append(fid-2*video.fps)
     
    framedir = video.videoname + "_panorama"
    if not os.path.exists(os.path.abspath(framedir)):
        os.makedirs(os.path.abspath(framedir))
    panorama_keyframes = framedir + "/panorama_fids.txt"
#     panorama_keyframes = util.stringlist_from_txt(panorama_keyframes)
#     keyframes_fid = util.strings2ints(panorama_keyframes)
    
    util.write_ints(keyframes_fid, panorama_keyframes)
    list_of_keyframes = video.capture_keyframes_fid(keyframes_fid, framedir)
#     list_of_keyframes = Keyframe.get_keyframes(framedir)
    
    panorama = pf.panorama(list_of_keyframes)
    cv2.imwrite(framedir + "/panorama.png", panorama)

    