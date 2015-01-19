#!/usr/bin/env python
import cv2
import sys
import processframe as pf
from video import Video, Keyframe
import framediff
import util
import removelogo
import numpy as np



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
    
def scroll_stitch_panorama():
    """written on 10/13/2014
    Capture keyframes after scroll event -- when framediff > thres,
    Remove logo from keyframes
    Stitch keyframes """
    videopath = sys.argv[1]
    framedifftxt = sys.argv[2]
#     logopath = sys.argv[3]
    if (len(sys.argv) == 5):
        thres = int(sys.argv[4])
    else:
        thres = 1000
    
    video = Video(videopath)
    counts = framediff.getcounts(framedifftxt)
    counts = util.smooth(np.array(counts), window_len = int(video.fps))
#     logos = util.get_logos(logopath)
# 
#     
    fid = 0
    last_unmoved_fid = 0
    capture = False
    keyframes_fid = []
    for count in counts:
        if count < 500:
            last_unmoved_fid = fid
        if count >= 500 and not capture:
            capture = True
            keyframes_fid.append(max(0, last_unmoved_fid))
            print 'last_unmoved', last_unmoved_fid
        elif count < 500 and capture:
            capture = False
        fid += 1
    keyframes_fid.append(fid-2*video.fps)
    print 'fid-video.fps', fid-2*video.fps
     
    framedir = video.videoname + "_panorama"
#     panorama_keyframes = framedir + "/panorama_fids.txt"
#     util.write_ints(keyframes_fid, panorama_keyframes)
#     list_of_keyframes = video.capture_keyframes_fid(keyframes_fid, framedir)
    list_of_keyframes = Keyframe.get_keyframes(framedir)
    
    panorama = pf.panorama(list_of_keyframes)
    cv2.imwrite(framedir + "/panorama.png", panorama)

    
if __name__ == "__main__":
    scroll_stitch_panorama()
    