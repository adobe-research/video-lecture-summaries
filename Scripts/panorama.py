#!/usr/bin/env python
import cv2
import sys
import processframe as pf
from video import Video, Keyframe
import framediff
import util
import removelogo

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
    logopath = sys.argv[3]
    if (len(sys.argv) == 5):
        thres = int(sys.argv[4])
    else:
        thres = 400000
    
    video = Video(videopath)
    counts = framediff.getcounts(framedifftxt)
    logos = util.get_logos(logopath)

    
    fid = 0
    capture = False
    keyframes_fid = []
    for count in counts:
        if count > thres and not capture:
            capture = True
            keyframes_fid.append(max(0, fid-3))
        if count <= thres and capture:
            capture = False
        fid += 1
    keyframes_fid.append(fid-3)
    
    framedir = video.videoname + "_panorama"
    video.capture_keyframes_fid(keyframes_fid, framedir)
    
    list_of_frames = []
    keyframes = Keyframe.get_keyframes(framedir)
    for keyframe in keyframes:
        frame = keyframe.frame
        for logo in logos:
            frame = removelogo.fillblack(frame, logo)
        list_of_frames.append(frame)
    
   
    panorama = pf.panorama(list_of_frames)
    cv2.imwrite(framedir + "/panorama.png", panorama)
#     util.showimages([panorama])
    
if __name__ == "__main__":
    scroll_stitch_panorama()
    