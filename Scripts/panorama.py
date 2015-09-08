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
from scipy.signal._peak_finding import argrelextrema


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
    
def plot_keyframes(numfg, indices):
    t = np.linspace(1, len(numfg), len(numfg))        
    plt.plot(t, numfg)
    plt.scatter(indices, numfg[indices], c='red')
    plt.title("Panorama Keyframes")
    plt.xlabel("Frames")
    plt.ylabel("Pixels")
    plt.xlim(0, len(numfg))
    plt.savefig(video.videoname + "_panorama_keyframes.pdf")
    plt.show()
    plt.close()
 
    
if __name__ == "__main__":

    videopath = sys.argv[1]
    numfgpixtxt = sys.argv[2]
    is_black = int(sys.argv[3])    
    if (len(sys.argv) == 5):
        thres = int(sys.argv[4])
    else:
        thres = -3000
    
    video = Video(videopath)
    numfgpix = util.stringlist_from_txt(numfgpixtxt)
    counts = util.strings2ints(numfgpix)
    
    if (is_black == 1):
        is_black = True
    else:
        is_black = False
    
        
    countdiffs = []
    for i in range(0, len(counts)-1):
        diff = counts[i+1] - counts[i]
        countdiffs.append(diff)
    fid = 0
    last_unmoved_fid = 0
    capture = False
    keyframes_fid = [0]
    for diff in countdiffs:
        if diff < thres and not capture:
            keyframes_fid.append(max(0, fid-2))
            capture = True
        elif diff <= thres:
            capture = False
        fid += 1
    print fid-2*video.fps
    keyframes_fid.append(fid-2*video.fps)
     
    framedir = video.videoname + "_panorama"
    if not os.path.exists(os.path.abspath(framedir)):
        os.makedirs(os.path.abspath(framedir))
    panorama_keyframes = framedir + "/panorama_fids.txt"
    
    util.write_ints(keyframes_fid, panorama_keyframes)
    list_of_keyframes = video.capture_keyframes_fid(keyframes_fid, framedir)
#     list_of_keyframes = Keyframe.get_keyframes(framedir)
    print "stitch panorama"
    panorama = pf.panorama(list_of_keyframes, is_black)
    cv2.imwrite(framedir + "/panorama.png", panorama)

    