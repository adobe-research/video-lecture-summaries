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
from video import Video, Keyframe
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
        elif (fg - prevfg < 2000 and not drawing):
            """scroll down event"""
            maxfg = fg
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

def capture_object_keyframes(object_fids, video):
    end_fids = [0]
    start_fids = [0]
    for fids in object_fids:
        start_fids.append(fids[0])
        end_fids.append(fids[1])
        
    keyframes = video.capture_keyframes_fid(end_fids, video.videoname + "_temp")
    return keyframes
    
def getobjects(video, object_fids, panorama, objdir):
    print 'video.fps', video.fps
    if not os.path.exists(os.path.abspath(objdir)):
        os.makedirs(os.path.abspath(objdir))
    
    end_fids = [0]
    start_fids = [0]
    for fids in object_fids:
        start_fids.append(fids[0])
        end_fids.append(fids[1])
    
    images, filenames = util.get_images(video.videoname + "_temp/negate", end_fids) #video.capture_keyframes_fid(end_fids, video.videoname + "_temp")
    keyframes = []
    for i in range(0, len(images)):
        keyframes.append(Keyframe(filenames[i], images[i], video.fid2ms(end_fids[i]), end_fids[i]))
#          
#     keyframes = video.capture_keyframes_fid(end_fids, video.videoname + "_temp")
    
    prevframe = np.zeros((video.height, video.width, 3), dtype=np.uint8)
    list_of_objs = []
    i = 0    
    prevx = 0 
    prevy = 0
    for keyframe in keyframes:
#         util.showimages([keyframe.frame], "keyframe")
        prev_id = start_fids[i]
        cur_id = end_fids[i]
         
        """get relative scroll position from previous frame"""
        topleft = pf.find_object_exact_inside(panorama, keyframe.frame, threshold=-1)
        curx = topleft[0]
        cury = topleft[1]
        
        curx = curx-prevx
        cury = cury-prevy
#         print 'curx, cury', curx, cury
#         if (curx != 0 or cury != 0):
#             i += 1
#             prevx = topleft[0]
#             prevy = topleft[1]
#             prevframe = keyframe.frame
#             continue
            
        curh, curw = keyframe.frame.shape[:2]
        diff_frame = keyframe.frame.copy()
        
        curframe_overlap = diff_frame[max(0,-cury):min(curh-cury, curh), max(0, -curx):min(curw-curx, curw)] 
        prevframe_overlap = prevframe[max(0, cury):min(curh, curh+cury), max(0, curx):min(curw+curx, curw)]
        cur_overlaph, cur_overlapw = curframe_overlap.shape[:2]
        pre_overlaph, pre_overlapw = prevframe_overlap.shape[:2]
        print 'i',  keyframe.frame_path, curx, cury
        if (cur_overlaph != pre_overlaph or cur_overlapw != pre_overlapw or cur_overlaph == 0 or cur_overlapw == 0):
            i += 1
            prevx = topleft[0]
            prevy = topleft[1]
            prevframe = keyframe.frame
            continue
        
        diff_frame[max(0,-cury):min(curh-cury, curh), max(0, -curx):min(curw-curx, curw)] = cv2.absdiff(curframe_overlap, prevframe_overlap)
        obj_frame = cv2.min(keyframe.frame, diff_frame) 
#         util.showimages([obj_frame], "obj_frame")
        obj_mask = pf.fgmask(obj_frame, 50, 255, True)
#         util.showimages([obj_mask], "obj_mask")
        obj_bbox = pf.fgbbox(obj_mask)
        
       
        if (obj_bbox[0] < 0 ):
#         if obj_crop is None:
            i += 1
            prevx = topleft[0]
            prevy = topleft[1]
            prevframe = keyframe.frame
#             print 'no fg object detected'
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
        visobj_segmented = [visobj] #visobj.segment_cc()
        list_of_objs = list_of_objs + visobj_segmented
        prevframe = keyframe.frame
        i += 1
        prevx = topleft[0]
        prevy = topleft[1]
       
    objinfopath = objdir + "/obj_info.txt"
    VisualObject.write_to_file(objinfopath, list_of_objs)
    return list_of_objs
 
    
    
def segment_main():
    videopath = sys.argv[1]
    video = Video(videopath)
    
    
    objfidspath = sys.argv[2]
    object_fids = read_obj_fids(objfidspath)
    
    panoramapath = sys.argv[3]
    panorama = cv2.imread(panoramapath)
    getobjects(video, object_fids, panorama, video.videoname + "_fgpixel_objs_noseg")
             

if __name__ == "__main__":  
    segment_main()