#!/usr/bin/env python
import numpy as np
import cv2
import sys
import re
from matplotlib import pyplot as plt
import os
from PIL import Image
import images2gif
import processvideo as pv
import processframe as pf
import processscript as ps
import process_aligned_json as pj
from sentence import Sentence
from video import Video, Keyframe
from lecture import Lecture
from writehtml import WriteHtml
import util
from visualobjects import VisualObject
import lectureplot as lecplot
from scipy.signal import argrelextrema
import linebreak
import fgpixel_segmentation as fgpixel




def get_keyframes(dirname):
    filelist = os.listdir(dirname)
    filelist = [ x for x in filelist if "capture" in x and ".png" in x and "fg" not in x and "overlap" not in x]
    #filelist.sort(cmp=util.filename_comp)
    
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
        
def fgbbox(keyframes):   
    dirname = "temp" 
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

def test_overlap(framedir, logodir):   
   
    keyframes = Keyframe.get_keyframes(framedir)
    logos = get_logos(logodir)
    
    print "Save foreground images"
    fgdir = framedir + "\\foreground_highlight"
    if not os.path.exists(os.path.abspath(fgdir)):
        os.makedirs(os.path.abspath(fgdir))
        
    for keyframe in keyframes:
        keyframe.add_default_objs(logos)
        fgframe = np.array(keyframe.frame)
        fgframe = pf.highlight(fgframe, keyframe.fg_mask)
        fgbbox = keyframe.fg_bbox()
        cv2.rectangle(fgframe, (fgbbox[0], fgbbox[1]), (fgbbox[2], fgbbox[3]), (255,0,0,255), 2)
        fgfilename = fgdir + "\\" + keyframe.frame_filename        
        if not os.path.isfile(os.path.abspath(fgfilename)):
            print 'writing', (fgdir + "\\" + keyframe.frame_filename)
        cv2.imwrite(fgdir + "\\" + keyframe.frame_filename, fgframe)
        
    
    "Highlight new objects from each image using previous one frame"
    objdir = framedir + "\\new_obj_highlight"
    if not os.path.exists(os.path.abspath(objdir)):
        os.makedirs(os.path.abspath(objdir))        
    prevframe = None
    for keyframe in keyframes:
        if (prevframe == None):
            prev_obj = []
        else:
            prev_obj = [prevframe.get_fgobj(includelogo=True)]
        keyframe.set_newobj_mask(prev_obj)
        #objframe = np.array(keyframe.frame)
        #objframe = pf.highlight(objframe, keyframe.newobj_mask)
        #objbbox = keyframe.newobj_bbox()
        #cv2.rectangle(objframe, (objbbox[0], objbbox[1]), (objbbox[2], objbbox[3]), (0,0,255,255), 2)
        #objfilename = objdir + "\\" + keyframe.frame_filename
        #print 'writing', (objdir + "\\" + keyframe.frame_filename)
        #cv2.imwrite(objdir + "\\" + keyframe.frame_filename, objframe)        
        prevframe  = keyframe
    
    overlapdir = framedir + "\\overlap_objects"
    if not os.path.exists(os.path.abspath(overlapdir)):
        os.makedirs(os.path.abspath(overlapdir))        

    html = WriteHtml(overlapdir + "\\overlap.html", "Overlap test")    
    prevframe = None
    for keyframe in keyframes:
        overlapframe = np.array(keyframe.frame)
        new_visual = keyframe.new_visual_score()
        if (new_visual <= 0):            
            continue        
        if prevframe == None:
            overlap_area = 0
        else:
            prevfgbbox = prevframe.fg_bbox()
            if prevfgbbox[0] >= 0:
                cv2.rectangle(overlapframe, (prevfgbbox[0], prevfgbbox[1]), (prevfgbbox[2], prevfgbbox[3]), (0, 0, 255, 255), 4)
        curobjbbox = keyframe.newobj_bbox()
        if curobjbbox[0] >= 0:
            cv2.rectangle(overlapframe, (curobjbbox[0], curobjbbox[1]), (curobjbbox[2], curobjbbox[3]), (255, 0, 0, 255), 4)
            
        if (prevframe != None and prevfgbbox[0] >= 0 and curobjbbox[0] >= 0):
            overlap = util.bbox_overlap(prevfgbbox, curobjbbox)
            overlap_area = util.boxarea(overlap)
        else:
            overlap_area = 0
        if (overlap_area > 0):
            cv2.rectangle(overlapframe, (overlap[0], overlap[1]), (overlap[2], overlap[3]), (0, 255, 0, 50), -1)
        prevframe = keyframe
        cv2.imwrite(overlapdir + "\\" + keyframe.frame_filename, overlapframe)          
        
        
        html.opentablerow()
        fgfilename = fgdir + "\\" + keyframe.frame_filename                
        html.cellimagelink(fgfilename, "300")
        objfilename = objdir + "\\" + keyframe.frame_filename
        html.cellimagelink(objfilename, "300")
        overlapfilename = overlapdir + "\\" + keyframe.frame_filename
        html.cellimagelink(overlapfilename, "300")
        html.cellstring( "new visual: " + str(new_visual) + " \n" + "overlap: " + str(overlap_area) + "\n")        
        html.closetablerow()
        
    html.closetable()

    html.closehtml()
    
def test_keyframe_object_in_panorama(framedir, logodir, panorama):
    keyframes = Keyframe.get_keyframes(framedir)
    logos = get_logos(logodir)
    
    print "Detect logos in each key frame"
    for keyframe in keyframes:
        keyframe.add_default_objs(logos)    
    
    print "Set new objects in each key frame using previous one frame"
    prevframe = None
    for keyframe in keyframes:
        if (prevframe == None):
            prev_obj = []
        else:
            prev_obj = [prevframe.get_fgobj(includelogo=True)]
        keyframe.set_newobj_mask(prev_obj)
        prevframe  = keyframe
        
    print "Find object in panorama"
    for keyframe in keyframes:
        if (keyframe.new_visual_score() <= 0):
            continue
        objcrop, objcropmask = pf.croptofg(keyframe.frame, keyframe.newobj_mask)
        if objcrop == None:
            continue
        #M = pf.find_object_exact(panorama, objcrop)
        #if not pf.isgoodmatch(M):
        M = pf.find_object_appx_thres(panorama, objcrop)
        if not pf.isgoodmatch(M):
            continue
        h, w = objcrop.shape[:2]
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        cv2.polylines(panorama, [np.int32(dst)], True,(0, 0, 0, 255),2)
        util.showimages([pf.highlight(objcrop,objcropmask), panorama])
        
    cv2.imwrite(framedir+ "\\panoarama_objects.png", panorama)

def test_panorama(framedir, logodir):
    keyframes = get_keyframes(framedir)
    logos = get_logos(logodir)
    
    for keyframe in keyframes:
        keyframe.add_default_objs(logos)
        
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
            #fgcrop = pf.croptofg(frame, keyframe.fg_mask )
            list_of_frames.append(frame)
            
    panorama = pf.panorama(list_of_frames)
    
    cv2.imwrite(framedir + "\\panorama_new.png", panorama)
    return panorama        
    
def test_panorama_path(panorama, keyframes):    
    panorama_gray = cv2.cvtColor(panorama, cv2.COLOR_BGRA2GRAY)    
    pathimg = np.array(panorama)
        
    for keyframe in keyframes:        
        M = None
        M = pf.find_object_exact(panorama, keyframe.frame)        
        if (M == None or not pf.isgoodmatch(M)):
            print 'Did not find frame in panorama'
            continue
        else:
            print 'Found  a good match'
            print M
        h,w = keyframe.frame.shape[:2]
        print h, w
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        cv2.polylines(pathimg,[np.int32(dst)],True,(0, 255, 0, 255),1)
        cv2.imshow("Frame foreground", keyframe.frame)
        cv2.imshow("path", pathimg)
        cv2.waitKey(0)
        
    return pathimg


def test_highlight_in_panorama(panorama, frame, highlight_mask):
    panorama_gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    M = pf.find_object_appx_thres(panorama_gray, frame_gray)
    if M == None:
        print 'frame not found'
        return
    h,w = panorama.shape[:2]
    #util.showimages([highlight_mask])
    print 'mask.shape before warp', highlight_mask.shape
    #mask = cv2.perspectiveTransform(highlight_mask,M)
    mask = cv2.warpPerspective(highlight_mask, M, (w,h), borderValue = 0, borderMode = cv2.BORDER_CONSTANT)
    #util.showimages([mask])
    print 'mask.shape after warp', mask.shape
    temp = np.array(panorama)
    high = pf.highlight(temp, mask)
    #util.showimages([high])
    return high
        

def test_panorama_projectile_main():
    panorama = cv2.imread(sys.argv[1])
    min_points =[]
    h,w = panorama.shape[0:2]
    panorama_fg = pf.fgmask(panorama, 50, 255, True)
    for i in range(0, 4):
        w1 = (i*0.25) * w
        w2 = (i+1)*0.25 *w
        print w1, w2
        quarter_img = panorama_fg[:,w1:w2]
        y = np.empty(h, dtype=np.uint8)
        for j in range(0, h):
            y[j] = np.count_nonzero(quarter_img[j,:])
        y = util.smooth(y, window_len=15)
        plt.plot(y)
        plt.show()          
    
    
def test_merge_inline_objects_main():
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    lec = Lecture(videopath, scriptpath)
    line_objs = VisualObject.objs_from_file(lec.video, objdir)
    line_objs_w_context = []
    line_idx = []
    lines = []
    n = len(line_objs)
    bestline_j = -1
    for i in range(0, n):
        curobj = line_objs[i]
        min_score = 1.0
        bestline = None
        for j in range(0, len(lines)):
            line = lines[j]
            score = VisualObject.inline_score(curobj, line, line_objs[i+1:])
            if (score < min_score):
                min_score = score
                bestline = line
                bestline_j = j
        if bestline is None:
            merged_obj = VisualObject.group([curobj], objdir + "/merged")
            line_objs_w_context.append(merged_obj)
            line_idx.append(len(lines))
            lines.append(curobj)
        else:
            merged_obj = VisualObject.group([curobj, bestline], objdir + "/merged")
            line_objs_w_context.append(merged_obj)
            line_idx.append(bestline_j)
#             before = lines[bestline_j]
            lines[bestline_j] = merged_obj
#             util.showimages([before.img, lines[bestline_j].img], "line before and after merging")
        print 'num separate lines', len(lines)
            
    html = WriteHtml(objdir + "merged/figures_w_context.html", title="Figures with Context", stylesheet=os.path.abspath("../Mainpage/summaries.css"))
    html.opendiv(idstring="summary-container")
    html.obj_script(line_objs_w_context, line_idx,  lec)
    html.closediv()
    html.closehtml()
    
def test_numfgframe():
    
    video = sys.argv[1]
    cap = cv2.VideoCapture(video)
    fgpixel_txt = sys.argv[2]
    numfg = fgpixel.read_fgpixel(fgpixel_txt)    
    
    index = 0
    while (cap.isOpened() and index < len(numfg)):
        ret, frame = cap.read()
        if (ret):
            fgmask = pf.fgmask(frame, 50, 255, True)
            print 'numfg', numfg[index]
            
            util.showimages([fgmask])
        else:
            cap.release()
        index += 1
        
    
    
if __name__ == "__main__":
    test_numfgframe()
    
    
       