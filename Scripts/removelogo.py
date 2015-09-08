#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
from video import Video
import util

def fillcolor(img, logos, color):
    outimg = img.copy()
    for logo in logos:
        hlogo, wlogo = logo.shape[0:2]
        topleft = pf.find_object_exact_inside(outimg, logo, 0.80)        
        if (topleft is None):
            img_copy = img.copy()
            util.showimages([img_copy], "no logo")
            continue
        else:
            tlx = topleft[0]
            tly = topleft[1] 
        brx = tlx + wlogo
        bry = tly + hlogo        
        img_copy = img.copy()
        cv2.rectangle(img_copy, topleft, (brx,bry), 255, 2)
        util.showimages([img_copy], "logo detected")

        outimg[tly:bry, tlx:brx, 0] = color[0]
        outimg[tly:bry, tlx:brx, 1] = color[1]
        outimg[tly:bry, tlx:brx, 2] = color[2]        
        
    return outimg

def fillblack(img, logos):
    return fillcolor(img, logos, (0,0,0))
    
def fillwhite(img, logos):
    return fillcolor(img, logos (255, 255, 255))

def fromvideo(video, logos, is_black, bgcolor):
    cap = cv2.VideoCapture(video.filepath)
    outvideo = video.videoname+"_removelogo.avi"
    fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
    out = cv2.VideoWriter(outvideo, int(fourcc), int(video.fps), (int(video.width), int(video.height)))
    
    fid = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        print "%i / %i" %(fid, video.numframes)
        fid += 1
        if (frame == None):
            break
#         util.showimages([frame], "before logo subtraction")
        for i in range(0, len(logos)):
            frame = pf.subtractlogo(frame, logos[i], is_black, bgcolor)
#         util.showimages([frame], "after, logo subtraction")
        out.write(frame)
    cap.release()
    out.release()
    print 'output: ', outvideo
        

if __name__ == "__main__":    
    """Removes logo from video or image"""
    target = sys.argv[1]
    logodir = sys.argv[2]
    is_black = int(sys.argv[3])
    outdir = os.path.dirname(target)
    extension = os.path.splitext(target)[1]
    logos = util.get_logos(logodir)    
    
    if is_black == 1:
        is_black = True
        bgcolor = (0,0,0)
    else:
        is_black = False
        bgcolor = (255,255,255)
    
    if (".mp4" in extension or ".avi" in extension or ".mov" in extension):
        video = Video(target)
        fromvideo(video, logos, is_black, bgcolor)
    elif (".png" in extension):
        img = cv2.imread(target)
        outimg = fillcolor(img, logos, bgcolor)
        
    else:    
        imagefiles, images = util.get_capture_imgs(target)
        print len(images)
        processed_path = outdir + "\\removelogo"
        if not os.path.exists(processed_path):
            os.makedirs(processed_path)
        
        for i in range(0, len(images)):
            print imagefiles[i]
            img = images[i]
            outimg = fillcolor(img, logos, bgcolor)
            cv2.imwrite(processed_path+"\\"+ imagefiles[i], outimg)
            
            
            