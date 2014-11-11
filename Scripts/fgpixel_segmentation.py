#!/usr/bin/env python
import processvideo
import processframe as pf
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys
from video import Video
from visualobjects import VisualObject

def read_fgpixel(fgpixel_txt):
    numfg = util.stringlist_from_txt(fgpixel_txt)
    numfg = util.strings2ints(numfg)
    return numfg    

def read_obj_fids(objfidspath):
    object_fids = util.list_of_vecs_from_txt(objfidspath, n=2)
    objfids = []
    for fids in object_fids:
        objfids.append((int(fids[0]), int(fids[1])))
    return objfids

def get_object_start_end_frames(numfg, video, outfile=None):
    object_fids = []
    drawing = False
    maxfg = numfg[0]
    prevfg = -1 
    start_fid = -1
    end_fid = -1
    fid = 0
    
#     cap = cv2.VideoCapture(video.filepath)
    for fg in numfg:
        print fg
#         ret, frame = cap.read()
#         if (fid == 0):
#             last_endimg = frame
        if (fg > maxfg and not drawing):
#             startimg = frame
            drawing = True
            start_fid = fid
        elif (fg == prevfg and drawing):
#             endimg = frame
            drawing = False
            end_fid = fid
            if (start_fid >= 0 and end_fid >= 0 and start_fid < end_fid):
                object_fids.append((start_fid, end_fid))
            start_fid = -1
            end_fid = -1
            
#             absdiff = cv2.absdiff(endimg, last_endimg)
#             objmask = pf.fgmask(absdiff, 50, 255, True)
#             objbbox = pf.fgbbox(objmask) 
#             endimg_copy = endimg.copy()
#             cv2.rectangle(endimg_copy, (objbbox[0], objbbox[1]), (objbbox[2], objbbox[3]), (255, 255, 255),2)
#             util.showimages([absdiff, endimg_copy], "Start and End Frame")
#             last_endimg = endimg        
        fid += 1
        maxfg = max(fg, maxfg)
        prevfg = fg
        
    """write object times"""
    if outfile is None:
        outfile = video.videoname + "_fgpixel_obj_fids.txt"
    if not os.path.isfile(os.path.abspath(outfile)):
        frameids = open(outfile, "w")
        for fids in object_fids:
            frameids.write("%i\t%i\n" %(fids[0], fids[1]))
        frameids.close()      
    
    return object_fids
        

def getnewobject_frame(prev_panorama, curframe, curx, cury):
    h, w = curframe.shape[:2]
    
    panorama_overlap = prev_panorama[cury:cury+h, curx:curx+w]
    diff_frame = cv2.absdiff(curframe, panorama_overlap)
    diff_frame = np.minimum(diff_frame, curframe)
    util.showimages([curframe, diff_frame], "new object")
    obj_mask = pf.fgmask(diff_frame, 50, 255, True)
    obj_bbox = pf.fgbbox(obj_mask)
    if (obj_bbox[0] < 0 or obj_bbox[2]-obj_bbox[0] == 0 or obj_bbox[3] - obj_bbox[1] == 0):
        return None, None
    else:
        obj_crop = pf.cropimage(diff_frame, obj_bbox[0], obj_bbox[1], obj_bbox[2], obj_bbox[3])
        return obj_bbox, obj_crop
    
def update_panorama_frame(prev_panorama, curframe, curx, cury):
    h, w = curframe.shape[:2]
    curframe_resize = prev_panorama.copy()
    curframe_resize[cury:cury + h, curx:curx+w] = curframe
    prev_panorama = cv2.max(prev_panorama, curframe_resize)
    util.showimages([prev_panorama])
    return prev_panorama


def cleanup(visobj, panorama_fg, cleanupdir):
    """objects appear only once, related to first time that they appear
        panorama_fg: all objects that can still appear in panorama 
        visobj: current visobj to be cleaned """
    obj_mask = pf.fgmask(visobj.img, 50, 255, True)
    panorama_fg_crop = panorama_fg[visobj.tly:visobj.bry+1, visobj.tlx:visobj.brx+1]
    new_mask = cv2.bitwise_and(obj_mask, panorama_fg_crop)
    new_bbox = pf.fgbbox(new_mask)
    
    if new_bbox[0] < 0:
        return None, panorama_fg
    new_img = pf.maskimage(visobj.img, new_mask)
    new_img = pf.cropimage(new_img, new_bbox[0], new_bbox[1], new_bbox[2], new_bbox[3])
    new_imgname = os.path.basename(visobj.imgpath)
    util.saveimage(new_img, cleanupdir, new_imgname)
    tlx = visobj.tlx + new_bbox[0]
    tly = visobj.tly + new_bbox[1]
    brx = visobj.tlx + new_bbox[2]
    bry = visobj.tly + new_bbox[3]
    new_visobj = VisualObject(new_img, cleanupdir + "/" + visobj.imgpath, visobj.start_fid, visobj.end_fid, tlx, tly, brx, bry)
    new_fg = pf.fit_mask_to_img(panorama_fg, new_mask, new_visobj.tlx, new_visobj.tly)
    new_bg = cv2.bitwise_not(new_fg)
    panorama_fg = cv2.bitwise_and(panorama_fg, new_bg) 
    
    new_visobjs = new_visobj.segment_cc()
    
    return new_visobjs, panorama_fg
    
        
def getobjects(video, object_fids, panorama, objdir):
    if not os.path.exists(os.path.abspath(objdir)):
        os.makedirs(os.path.abspath(objdir))
    
    end_fids = [0]
    start_fids = [0]
    for fids in object_fids:
        start_fids.append(fids[0])
        end_fids.append(fids[1])
    
    keyframes = video.capture_keyframes_fid(end_fids, video.videoname + "_temp")
    prevframe = np.zeros((video.height, video.width, 3), dtype=np.uint8)
     
    list_of_objs = []
    i = 0    
    prevx = 0 
    prevy = 0
#     prev_panorama = np.zeros(panorama.shape, dtype=np.uint8)
    for keyframe in keyframes:
        prev_id = start_fids[i]
        cur_id = end_fids[i]
         
        """get relative scroll position from previous frame"""
        topleft = pf.find_object_exact_inside(panorama, keyframe.frame, threshold=-1)
        curx = topleft[0]
        cury = topleft[1]
        
        curx = curx-prevx
        cury = cury-prevy
        curh, curw = keyframe.frame.shape[:2]
         
        diff_frame = keyframe.frame.copy()
        curframe_overlap = diff_frame[max(0,-cury):min(curh-cury, curh), max(0, -curx):min(curw-curx, curw)] 
        prevframe_overlap = prevframe[max(0, cury):min(curh, curh+cury), max(0, curx):min(curw+curx, curw)]
        diff_frame[max(0,-cury):min(curh-cury, curh), max(0, -curx):min(curw-curx, curw)] = cv2.absdiff(curframe_overlap, prevframe_overlap)
        diff_frame = cv2.min(keyframe.frame, diff_frame) 
        obj_frame = cv2.min(diff_frame, keyframe.frame)
        obj_mask = pf.fgmask(obj_frame, 50, 255, True)
        obj_bbox = pf.fgbbox(obj_mask)
        
       
        if (obj_bbox[0] < 0 ):
#         if obj_crop is None:
            i += 1
            prevx = topleft[0]
            prevy = topleft[1]
            prevframe = keyframe.frame
            continue
        obj_crop = pf.cropimage(obj_frame, obj_bbox[0], obj_bbox[1], obj_bbox[2], obj_bbox[3])
      
#         print 'curx, cury', curx, cury
#         util.showimages([diff_frame], "diff frame")
        """if not a scroll event"""
        objimgname = "obj_%06i_%06i.png" % (prev_id, cur_id)
#         util.showimages([obj_frame], objimgname)
#         util.showimages([keyframe.frame, obj_crop], str(start_fids[i]) + " " + str(end_fids[i]) + " " + objimgname)
        util.saveimage(obj_crop, objdir, objimgname)
        visobj = VisualObject(obj_crop,  objdir + "/" + objimgname, start_fids[i], end_fids[i], obj_bbox[0] + topleft[0], obj_bbox[1] + topleft[1], obj_bbox[2] + topleft[0], obj_bbox[3] + topleft[1])
        visobj_segmented = visobj.segment_cc()
        list_of_objs = list_of_objs + visobj_segmented
        prevframe = keyframe.frame
        i += 1
        prevx = topleft[0]
        prevy = topleft[1]
       
    objinfopath = objdir + "/obj_info.txt"
    VisualObject.write_to_file(objinfopath, list_of_objs)
    return list_of_objs
 
 
def cleanup_main():
    panorama_path = sys.argv[1]
    objdir = sys.argv[2]
    cleanupdir = objdir + "/cleanup"
    if not os.path.exists(cleanupdir):
        os.makedirs(cleanupdir)
        
    visobjs = VisualObject.objs_from_file(None, objdir)
    print '# objs before cleanup', len(visobjs)
    panorama = cv2.imread(panorama_path)
    panorama_fg = pf.fgmask(panorama, 50, 255, True)
   
    list_of_new_visobjs = []
    for visobj in visobjs:
        new_visobjs, panorama_fg = cleanup(visobj, panorama_fg, cleanupdir )
#         util.showimages([panorama_fg])
        if new_visobjs is not None:
            list_of_new_visobjs = list_of_new_visobjs + new_visobjs
    print '# objs after cleanup', len(list_of_new_visobjs)
    new_objinfopath = cleanupdir + "/obj_info.txt"
    VisualObject.write_to_file(new_objinfopath, list_of_new_visobjs)   
    
    
def segment_main():
    videopath = sys.argv[1]
    video = Video(videopath)
    
    
    objfidspath = sys.argv[2]
    object_fids = read_obj_fids(objfidspath)
    
    panoramapath = sys.argv[3]
    panorama = cv2.imread(panoramapath)
    getobjects(video, object_fids, panorama, video.videoname + "_fgpixel_objs")
             

if __name__ == "__main__":  
    cleanup_main()
   