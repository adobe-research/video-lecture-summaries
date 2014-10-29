#!/usr/bin/env python
import util
import sys
from video import Video
import numpy as np
import cv2
import processframe as pf
import os
from itertools import count


def read_framediff(framediff_txt):
    framediff = util.stringlist_from_txt(framediff_txt)
    framediff = util.strings2ints(framediff)
    return framediff    

def get_object_start_end_frames(framediff, video, thres=50, outfile="obj_fids_temp"):
    """smooth"""
    smooth_framediff = util.smooth(np.array(framediff), window_len=5, window='flat')
    object_fids = []
    drawing = False
    fid = 0
    start_t = -1
    end_t = -1
    
    cap = cv2.VideoCapture(video.filepath)
    for diff in smooth_framediff:
#         ret, frame = cap.read()
#         util.showimages([frame], "original video")   
        if (diff > thres and not drawing):
#             startimg = frame
#             print "================================================start %i================================================" %fid
            drawing = True
            start_t = fid              
        if (diff <= thres and drawing):  
#             endimg = frame
#             util.showimages([startimg, endimg])          
            drawing = False
            end_t = fid
            if (start_t >= 0 and end_t >= 0 and start_t < end_t):
                object_fids.append((start_t, end_t))
#                 print "================================================end %i================================================" %fid
            start_t = -1
            end_t = -1
#         print diff
        fid += 1
#     print 'fid', fid
    """write object times"""
    if not os.path.isfile(os.path.abspath(outfile)):
        frameids = open(outfile, "w")
        for fids in object_fids:
            frameids.write("%i\t%i\n" %(fids[0], fids[1]))
        frameids.close()      
    
    return object_fids



def getobjects():
    videopath = sys.argv[1]
    video = Video(videopath)
    framediffpath = sys.argv[2]
    logopath = sys.argv[3]
    logo = cv2.imread(logopath)
    panorama = cv2.imread(sys.argv[4])
    threshold = int(sys.argv[5])
    
    """read frame difference counts"""
    framediff = read_framediff(framediffpath)    
    
    """compute object start/end frames"""
    objfidspath = video.videoname + "_obj_fids.txt"    
    objects_fids = get_object_start_end_frames(framediff, video, thres=threshold, outfile=objfidspath)
    
    keyframe_fids = [e for l in objects_fids for e in l]
    keyframes = video.capture_keyframes_fid(keyframe_fids, video.videoname + "_temp")
    
    objdir = video.videoname + "_framediff_objs_threshold_%s" % (threshold)
    objfile = "obj_info.txt"
    """write object information"""
    if not os.path.exists(os.path.abspath(objdir)):
        os.makedirs(os.path.abspath(objdir))
    objinfo = open(objdir + "/" + objfile, "w")
    objinfo.write("start_fid \t end_fid \t tlx \t tly \t brx \t bry\t filename\n")
    
    """keep track of scrolling"""
    curx = 0
    cury = 0
    
    """include any default object"""
    initial_frame = video.getframe_fid(0)
    objmask = pf.fgmask(initial_frame, 50, 255, True)
    objbbox = pf.fgbbox(objmask)
    if (objbbox[0] >= 0 and objbbox[2]-objbbox[0] > 0 and objbbox[3] - objbbox[1] > 0): 
        objmask = pf.cropimage(objmask, objbbox[0], objbbox[1], objbbox[2], objbbox[3])
        objcrop = pf.cropimage(initial_frame, objbbox[0], objbbox[1], objbbox[2], objbbox[3])
        objimgname = "obj_%06i_%06i.png" %(0, 0)
        util.saveimage(objcrop, objdir, objimgname)
        objinfo.write("%i\t%i\t%i\t%i\t%i\t%i\t%s\n" %(0, 0, objbbox[0]+curx, objbbox[1]+cury, objbbox[2]+curx, objbbox[3]+cury, objimgname))
    
    i = 0
    while i < len(keyframes):
        """remove cursor"""
        start_frame = keyframes[i+0].frame
#         start_frame = pf.subtractlogo(start_frame, logo, (0,0,0))
        end_frame = keyframes[i+1].frame
        end_frame = pf.subtractlogo(end_frame, logo, (0,0,0))
        
        """subtract start frame from end frame"""
        absdiff = cv2.absdiff(end_frame, start_frame)
        diff = cv2.min(absdiff, end_frame)
        
#         util.showimages([start_frame, end_frame, diff_before, diff], "framediff_segmentation, object")
        """get foreground object and bounding box """
        objmask = pf.fgmask(diff, 50, 255, True)
        count = np.count_nonzero(objmask)
        
        """get rid of noise (minthres) and scrolling (maxthres)"""
        minthres = 20
        maxthres = 10000
        if (count < minthres or count > maxthres):
#             print count
#             util.showimages([diff, objmask])
            i += 2
            continue
        objbbox = pf.fgbbox(objmask)
        if (objbbox[0] < 0 or objbbox[2]-objbbox[0] == 0 or objbbox[3] - objbbox[1] == 0):
            i += 2
            continue  
          
        objmask = pf.cropimage(objmask, objbbox[0], objbbox[1], objbbox[2], objbbox[3])
        objcrop = pf.cropimage(diff, objbbox[0], objbbox[1], objbbox[2], objbbox[3])
#         util.showimages([objcrop], "ojb crop and mask")
        
        topleft = pf.find_object_exact_inside(panorama, end_frame, threshold=-1)
        curx = topleft[0]
        cury = topleft[1]
        
        objimgname = "obj_%06i_%06i.png" %(keyframe_fids[i+0], keyframe_fids[i+1])
        util.saveimage(objcrop, objdir, objimgname)
        objinfo.write("%i\t%i\t%i\t%i\t%i\t%i\t%s\n" %(keyframe_fids[i+0], keyframe_fids[i+1], objbbox[0]+curx, objbbox[1]+cury, objbbox[2]+curx, objbbox[3]+cury, objimgname ))
        i += 2
        
        panorama_temp = panorama.copy()
#         print 'curx, cury', curx, cury
#         cv2.rectangle(panorama_temp, (objbbox[0]+curx, objbbox[1]+cury), (objbbox[2]+curx, objbbox[3]+cury), (255, 255, 255),2)
#         util.showimages([objcrop, panorama_temp])
        
    objinfo.close()
#         cv2.rectangle(diff, (objbbox[0], objbbox[1]), (objbbox[2], objbbox[3]), (255, 255, 255), 2)
#         util.showimages([objmask, diff])     
#         util.showimages([start_frame, end_frame, diff])
#         print "writing", "obj_%06i_%06i.png" %(keyframe_fids[i+0], keyframe_fids[i+1])
#         util.saveimage(diff, diffdir, "obj_%06i_%06i.png" %(keyframe_fids[i+0], keyframe_fids[i+1]))
        
    
if __name__ == "__main__":    
    getobjects()
        
        