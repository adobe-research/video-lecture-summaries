#!/usr/bin/env python
import numpy as np
import cv2
import sys
import re
from matplotlib import pyplot as plt
import os
from PIL import Image
import images2gif
import processvideo
import processframe as pf
import processscript as ps
import process_aligned_json as pj
from sentence import Sentence
from video import Video, Keyframe
from lecture import Lecture
from writehtml import WriteHtml
import util
import framediff_segmentation as fdseg

def get_keyframes(dirname):
    filelist = os.listdir(dirname)
    filelist = [ x for x in filelist if "capture" in x and ".png" in x and "fg" not in x and "overlap" not in x]
    filelist.sort(cmp=util.filename_comp)
    
    keyframes = []   
    for filename in filelist:
        frame = cv2.imread(dirname + "\\" + filename)
        keyframe = Keyframe(dirname + "\\" + filename, frame, -1, -1)
        keyframes.append(keyframe)
    return keyframes
    
    
def mask_new_from_prev_keyframes(dirname):       
    filelist = os.listdir(dirname)
    filelist = [ x for x in filelist if "capture" in x and ".png" in x and "fg" not in x and "overlap" not in x]
    print filelist
    filelist.sort(cmp=util.filename_comp)
    
    keyframes = []   
    for filename in filelist:
        frame = cv2.imread(dirname + "\\" + filename)
        keyframe = Keyframe(dirname + "\\" + filename, frame, -1, -1)
        keyframes.append(keyframe)
            
    # mask new parts compared to previous frames
    if (len(keyframes) == 0):
        return
    
    # first frame
    keyframes[0].mask = pf.fgmask(keyframes[0].frame)
    prevframe = keyframes[0]
    #cv2.imshow("curframe", keyframes[0].frame)
    #cv2.imshow("mask", keyframes[0].mask)
    #cv2.waitKey(0)

    for i in range(1, len(keyframes)):        
        curframe = keyframes[i]
        curframe.mask_new(prevframe)
        prevframe = curframe
    
    return keyframes
        #cv2.imshow("curframe", curframe.frame)
        #if (curframe.mask != None):
        #    cv2.imshow("mask", curframe.mask)       
        #cv2.waitKey(0)
        
def fgbbox(keyframes):    
    for keyframe in keyframes:
        fgbbox = keyframe.fg_bbox()        
        temp1 = np.array(keyframe.frame)
        cv2.rectangle(temp1, (fgbbox[0], fgbbox[1]), (fgbbox[2], fgbbox[3]), 0, 2)               
        cv2.imwrite(dirname + "/" + os.path.splitext(os.path.basename(keyframe.frame_path))[0]+ "_fgbbox.png", temp1)        
    return

def new_fgbbox(keyframes):
    prevobjs = []
    i = 0
    for keyframe in keyframes:
        print i 
        keyframe.mask_objs(prevobjs)
        curobj = keyframe.get_newobj()                
        bbox = keyframe.mask_bbox()
        temp = np.array(keyframe.frame)
        cv2.rectangle(temp, (bbox[0], bbox[1]), (bbox[2], bbox[3]), 0, 2)
        util.showimages([keyframe.frame, temp] + prevobjs)
        prevobjs = [curobj]        
        #cv2.imwrite(dirname + "/" + os.path.splitext(os.path.basename(keyframe.frame_path))[0]+ "new_fgbbox.png", temp)
        i += 1
    return       

if __name__ == "__main__":      
    dirname = sys.argv[1]
    logodir = sys.argv[2]
    logolist = os.listdir(logodir)
    logos = []
    for filename in logolist:
        logo = cv2.imread(logodir + "\\" + filename)
        logos.append(logo)
        
    keyframes = get_keyframes(dirname)
    for keyframe in keyframes:
        keyframe.add_default_objs(logos)
    
    #fgbbox(keyframes)
    new_fgbbox(keyframes)
        
        
    
    
    #keyframes = mask_new_from_prev_keyframes(dirname)
    #new_fgbbox(keyframes)
    #
    #
    #print "Writing to html"
    #html = WriteHtml(dirname + "/test_visaul.html", "Visual Information in Keyframes")
    #html.openbody()
    #html.opentable()
    #prevframe = None
    #for keyframe in keyframes:
    #    html.opentablerow()
    #    html.writestring("<td><img src=" +html.relpath(keyframe.frame_path)+"></td>\n")
    #    html.writestring("<td><img src=" + html.relpath(dirname + "/" + os.path.splitext(os.path.basename(keyframe.frame_path))[0]+ "new_fgbbox.png")+"></td>\n")
    #    
    #    overlaparea = -1
    #    if (prevframe != None):
    #        prev_fgbbox = prevframe.fgbbox()            
    #        newbbox = keyframe.newbbox()            
    #        overlap = util.bbox_overlap(prev_fgbbox, newbbox)
    #        overlaparea = util.boxarea(overlap)
    #        if (overlaparea > 0):
    #            cv2.rectangle(keyframe.frame, (overlap[0], overlap[1]), (overlap[2], overlap[3]), 0, 2)
    #            cv2.imwrite(dirname + "/" + os.path.splitext(os.path.basename(keyframe.frame_path))[0]+ "_new_overlap.png", keyframe.frame)
    #            html.writestring("<td><img src="  +html.relpath(dirname + "/" + os.path.splitext(os.path.basename(keyframe.frame_path))[0]+ "_new_overlap.png ") + "></td>\n")
    #            
    #    
    #    html.opentablecell()
    #    html.writestring("keyframe new visual:" + str(keyframe.new_visual()) +"<br>" )
    #    html.writestring("keyframe overlap:" + str(overlaparea) + "<br>")        
    #    html.closetablecell()
    #    prevframe = keyframe
    #    html.closetablerow()   
    #html.closetable()
    #html.closebody()
    #html.closehtml()
        
        
        

    
    
    
    
  
    