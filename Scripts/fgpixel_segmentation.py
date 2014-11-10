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
        

def getnewobject(prev_panorama, curframe, curx, cury):
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
    
def update_panorama(prev_panorama, curframe, curx, cury):
    h, w = curframe.shape[:2]
    curframe_resize = prev_panorama.copy()
    curframe_resize[cury:cury + h, curx:curx+w] = curframe
    prev_panorama = cv2.max(prev_panorama, curframe_resize)
    util.showimages([prev_panorama])
    return prev_panorama
    
        
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
        print 'curx, cury', curx, cury
#         obj_bbox, obj_crop = getnewobject(prev_panorama, keyframe.frame, curx, cury)
        
        curx = curx-prevx
        cury = cury-prevy
 
        curh, curw = keyframe.frame.shape[:2]
          
        diff_frame = keyframe.frame.copy()
        curframe_overlap = diff_frame[max(0,-cury):min(curh-cury, curh), max(0, -curx):min(curw-curx, curw)] 
        prevframe_overlap = prevframe[max(0, cury):min(curh, curh+cury), max(0, curx):min(curw+curx, curw)]
        diff_frame[max(0,-cury):min(curh-cury, curh), max(0, -curx):min(curw-curx, curw)] = cv2.absdiff(curframe_overlap, prevframe_overlap)
         
#         print 'curx, cury', curx, cury
 
        obj_frame = cv2.min(diff_frame, keyframe.frame)
        obj_mask = pf.fgmask(obj_frame, 50, 255, True)
        obj_bbox = pf.fgbbox(obj_mask)
        if (obj_bbox[0] < 0 or obj_bbox[2]-obj_bbox[0] == 0 or obj_bbox[3] - obj_bbox[1] == 0):
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
#         util.showimages([keyframe.frame, obj_crop], str(start_fids[i]) + " " + str(end_fids[i]) + " " + objimgname)
        util.saveimage(obj_crop, objdir, objimgname)
        visobj = VisualObject(obj_crop, objdir + "/" + objimgname, start_fids[i], end_fids[i], obj_bbox[0] + topleft[0], obj_bbox[1] + topleft[1], obj_bbox[2] + topleft[0], obj_bbox[3] + topleft[1])
        visobj_segmented = visobj.segment_cc()
        list_of_objs = list_of_objs + visobj_segmented
        prevframe = keyframe.frame
#         prev_panorama = update_panorama(prev_panorama, keyframe.frame, topleft[0], topleft[1])
        i += 1
        prevx = topleft[0]
        prevy = topleft[1]
     
    objinfopath = objdir + "/obj_info.txt"
    VisualObject.write_to_file(objinfopath, list_of_objs)
    return list_of_objs
    
    
if __name__ == "__main__":   
    videopath = sys.argv[1]
    video = Video(videopath)
    
    
    objfidspath = sys.argv[2]
    object_fids = read_obj_fids(objfidspath)
    
    panoramapath = sys.argv[3]
    panorama = cv2.imread(panoramapath)
    getobjects(video, object_fids, panorama, video.videoname + "_fgpixel_objs")
   
#     videolist = ["..\\SampleVideos\\more\\khan1\\khan1.mp4", "..\\SampleVideos\\more\\khan2\\khan2.mp4",
#                  "..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",                 
#                  "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
#                   "..\\SampleVideos\\more\\mit1\\mit1.mp4",  "..\\SampleVideos\\more\\mit2\\mit2.mp4", "..\\SampleVideos\\more\\mit3\\mit3.mp4",
#                  "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
#                   "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4"]
# 
#     for video in videolist:
#         pv = processvideo.ProcessVideo(video)
#         actionfilename = pv.videoname + "_action.txt"
#         actionfile = open(actionfilename, "r")
#         
#         draw = False
#         drawstart = []
#         drawend = []
#         starttimes = []
#         endtimes = []
#         sec = 0
#         for stat in actionfile.readlines():
#             stat = int(stat)
#             if (stat == 1 and not draw):
#                 starttimes.append(sec)
#                 drawstart.append(pv.framerate*sec)
#                 draw = True
#             elif (stat == 0 and draw):
#                 endtimes.append(sec-1)
#                 drawend.append(pv.framerate*(sec-1))
#                 draw = False
#             sec += 1
#         if (draw):
#             drawend.append(pv.framerate*(sec-1))
#             endtimes.append(sec-1)
#             
#         # Smooth and subsample
#         counts = pv.readfgpix()
#         smoothsample = util.smooth(np.array(counts), window_len = pv.framerate)
#         subsample = counts[0:len(smoothsample):int(pv.framerate)]
#         t = np.linspace(0, len(subsample), len(subsample))
#         plt.plot(t, subsample)
#         for val in starttimes:
#             plt.axvline(val, color='g')
#         for val in endtimes:
#             plt.axvline(val, color='r')
#         plt.xlim(-10.0, len(subsample))    
#         plt.savefig(pv.videoname + "_fgpix_drawtimes.jpg")
#         plt.close()
#             
#         startdir = pv.videoname + "startdraw"
#         enddir = pv.videoname + "enddraw"
#         if not os.path.exists(startdir):
#             os.makedirs(startdir)
#         if not os.path.exists(enddir):
#             os.makedirs(enddir)
#         pv.captureframes(drawstart, startdir+"/")
#         pv.captureframes(drawend, enddir+"/")
#         
#         startfilelist = os.listdir(startdir)
#         startimages = []
#         for filename in startfilelist:
#                 startimages.append(cv2.imread(startdir+"/"+filename))
#     
#         endfilelist = os.listdir(enddir)
#         endimages = []
#         for filename in endfilelist:
#             endimages.append(cv2.imread(enddir+"/"+filename))
#         
#         objectdir = pv.videoname + "fgobject"
#         if not os.path.exists(objectdir):
#             os.makedirs(objectdir)
#             
#         for i in range(0, len(startimages)):
#             object_img = cv2.absdiff(startimages[i], endimages[i])
#             cv2.imwrite(objectdir+"/object"+str(i)+".jpg", object_img)
        
        
    


        
    
    
                
