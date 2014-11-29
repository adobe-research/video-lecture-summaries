'''
Created on Nov 21, 2014

@author: hijungshin
'''

from visualobjects import VisualObject
import sys
import util
import processframe as pf
import os
import cv2
from video import Video

def remove_duplicate_pixels(visobj, panorama_fg, cleanupdir):
    """objects appear only once, related to first time that they appear
        panorama_fg: all objects that can still appear in panorama 
        visobj: current visobj to be cleaned """
    obj_mask = pf.fgmask(visobj.img, 50, 255, True)
#     util.showimages([panorama_fg], "panorama foreground")
    panorama_fg_crop = panorama_fg[visobj.tly:visobj.bry+1, visobj.tlx:visobj.brx+1]
    new_mask = cv2.bitwise_and(obj_mask, panorama_fg_crop)
    new_bbox = pf.fgbbox(new_mask)
    
    if new_bbox[0] < 0:
        return None, panorama_fg
    new_img = pf.maskimage(visobj.img, new_mask)
    new_img, new_mask = pf.croptofg(new_img, new_mask)
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

def main_white_background():
    objdir = sys.argv[1]
    list_of_objs = VisualObject.objs_from_file(None, objdir)
    for obj in list_of_objs:
        fgmask = pf.fgmask(obj.img, 225)
        obj.img[fgmask == 0] = (255, 255, 255)
        print obj.imgpath
        util.saveimage(obj.img, objdir, obj.imgpath)
        
def main_remove_duplicate_pixels():
    objdir = sys.argv[1]
    panorama_path = sys.argv[2]
    
    cleanupdir = objdir + "/cleanup"
    if not os.path.exists(cleanupdir):
        os.makedirs(cleanupdir)
        
    visobjs = VisualObject.objs_from_file(None, objdir)
    print '# objs before cleanup', len(visobjs)
    panorama = cv2.imread(panorama_path)
    panorama_fg = pf.fgmask(panorama, 50, 255, True)
   
    list_of_new_visobjs = []
    for visobj in visobjs:
        new_visobjs, panorama_fg = remove_duplicate_pixels(visobj, panorama_fg, cleanupdir )
#         util.showimages([panorama_fg])
        if new_visobjs is not None:
            list_of_new_visobjs = list_of_new_visobjs + new_visobjs
    print '# objs after cleanup', len(list_of_new_visobjs)
    new_objinfopath = cleanupdir + "/obj_info.txt"
    VisualObject.write_to_file(new_objinfopath, list_of_new_visobjs)   
    
def main_group_overlapping():
    objdir = sys.argv[1]
    overlapdir = objdir + "/overlap"
    if not os.path.exists(overlapdir):
        os.makedirs(overlapdir)
        
    list_of_objs = VisualObject.objs_from_file(None, objdir)
    num_objs = len(list_of_objs)
    
    
    print 'num ungrouped objs', len(list_of_objs)
    grouped_objs = []
    while(len(list_of_objs) > 0):
        firstobj = list_of_objs.pop(0)
        overlapping_objs = [firstobj]
        added = True
        while(added):
            added_idx = []
            added = False
            for i in range(0, len(list_of_objs)):
                obj = list_of_objs[i]
                tempobj = VisualObject.group(overlapping_objs, "temp")
                overlap = VisualObject.overlap(tempobj, obj)
                if (overlap > 0.15):
#                     print 'overlap', overlap
                    overlapping_objs.append(obj)
                    added_idx.append(i)
                    added = True
            list_of_objs = [i for j, i in enumerate(list_of_objs) if j not in added_idx]
            
        final_group = VisualObject.group(overlapping_objs, overlapdir)
        grouped_objs.append(final_group)
#         util.showimages([final_group.img])
    VisualObject.write_to_file(overlapdir + "/obj_info.txt", grouped_objs)
    print 'num grouped obj', len(grouped_objs)
                    
                
    
def main_group_color_time_space():
    videopath = sys.argv[1]
    objdir = sys.argv[2]
    groupdir = objdir + "/group"
    if not os.path.exists(groupdir):
        os.makedirs(groupdir)
        
    video = Video(videopath)
    list_of_objs = VisualObject.objs_from_file(video, objdir)
    grouped_objs = []
    group = []
    group.append(list_of_objs[0])
    prevobj = list_of_objs[0]
    for i in range(1, len(list_of_objs)):
        curobj = list_of_objs[i]
        time_distance = VisualObject.gap_frames(prevobj, curobj) / video.fps
        color_distance = VisualObject.colorgap_distance(prevobj, curobj)
        x_distance = VisualObject.xgap_distance(prevobj, curobj)
        y_distance = VisualObject.ygap_distance(prevobj, curobj)
        
        if (color_distance < 0.02 and time_distance <= 5.0 and x_distance < 100 and y_distance < 100):
            group.append(curobj)
        else:
            print 'time_distance', time_distance, 'color_distance', color_distance, 'x_distance', x_distance, 'y_distance', y_distance
            group_obj = VisualObject.group(group, groupdir)
            grouped_objs.append(group_obj)
#             images = [group_obj.img]
#             images = images + [a.img for a in group]
#             util.showimages(images, "grouped images")
#             util.showimages([curobj.img], "current object")
            group = [curobj]
        prevobj = curobj
    group_obj = VisualObject.group(group, groupdir)
    grouped_objs.append(group_obj)
    
        
    VisualObject.write_to_file(groupdir + "/obj_info.txt", grouped_objs)
        
if __name__ == "__main__":
    main_remove_duplicate_pixels()
#     main_group_overlapping()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        