#!/usr/bin/env python
import cv2
import sys
import processframe as pf
from visualobjects import VisualObject
import os
from lecture import Lecture
from writehtml import WriteHtml
import util


def init_old():
    panorama = cv2.imread(sys.argv[1])
    keyframe_dir = sys.argv[2]
    filelist = os.listdir(keyframe_dir)
    keyframes = []
    for filename in filelist:
        if "capture" in filename and ".png" in filename:
            keyframes.append(cv2.imread(keyframe_dir + "\\" + filename))
       
    # identify new objects in each keyframe
    objectmasks = pf.get_objectmasks(keyframes)
    
    panorama_highlight = "panorama_highlight"
    if not os.path.exists(keyframe_dir + "\\" + panorama_highlight):
        os.makedirs(keyframe_dir + "\\"+ panorama_highlight)        

    
    # find frame in panorama
    ph, pw = panorama.shape[0:2]
    masks = []
    for i in range(0, len(keyframes)):
        keyframe = keyframes[i]
        objmask = objectmasks[i]
        if (objmask == None):
            continue
        
        M = pf.find_object_appx(panorama, keyframe)
        if (M == None):
            continue
        
        if not pf.isgoodmatch(M):
            continue
        
        # warp object mask to panorama
        warp_mask = cv2.warpPerspective(objmask, M, (pw, ph))
        #cv2.imshow("warp_mask before", warp_mask)
        for prevmask in masks:
            #negate prevmask: only parts previously not highlighted are eligible
            #cv2.imshow("prevmask", prevmask)
            negmask = cv2.bitwise_not(prevmask)            
            #cv2.imshow("negamsk", negmask)
            warp_mask = cv2.bitwise_and(negmask, warp_mask)
            #cv2.imshow("warp mask", warp_mask)
            #cv2.waitKey(0)
        masks.append(pf.expandmask(warp_mask))
        highlight = pf.highlight(panorama, warp_mask)
        #cv2.imshow("highlight", highlight)
        #cv2.waitKey(0)
        cv2.imwrite(keyframe_dir + "\\" + panorama_highlight + "\\panorama_highlight" + ("%06i" % i) + ".png", highlight)

def write_html(filename, panoramapath, transcript_segs, list_of_areas):
    html = WriteHtml(filename, "Panorama")
    html.opentable()
    html.opentablerow()
    html.opentablecell()
    html.image(panoramapath, mapname="panorama-map")
    html.closetablecell()
    list_item_names = []
    seg_id = 1
    for seg in transcript_segs:
        list_item_names.append("text"+str(seg_id))
        seg_id += 1

    html.opentablecell()
    write_transcript_divs(html, transcript_segs, list_item_names)
    html.closetablecell()
    html.closetablerow()
    html.closetable()
    write_map(html, "panorama-map", list_of_areas, list_item_names)
    html.closehtml()
    
def write_transcript_divs(html, transcript_segs, list_item_names): 
    pid = 0
    for seg in transcript_segs:
        html.opendiv(idstring=list_item_names[pid], class_string="display")
        html.paragraph(seg)
        html.closediv()
        pid += 1
    
        
def write_map(html, mapname, list_of_areas, list_item_names):
    html.map(mapname, list_of_areas, list_item_names)

def get_map(panorama, list_of_objimgs):
    """Return list of map areas specified by 4 corners, or None"""
    
    list_of_areas = []
    for objimg in list_of_objimgs:
        list_of_areas.append(get_map_area(panorama, objimg))
    return list_of_areas

def get_map_area(panorama, objimg):
    
    """Return 4 corners of obj area inside panorama"""
    
    objh, objw = objimg.shape[:2]
    tl = pf.find_object_exact_inside(panorama, objimg, 0.25)
    if tl is None:
        print "panorama_highlight::get_map_area\nobject not found in panorama"
        util.showimages([panorama, objimg])
        return (-1, -1, -1, -1)
    else:
        return (tl[0], tl[1], tl[0] + objw, tl[1] + objh)


if __name__ == "__main__":
    """ Returns a hover-over panorama page
        
    Input arguments: 
    panorama.png
    video
    obj directory -- directory containing object images and objinfo.txt
    transcript.json
    outfile.html
    """
    
    panoramapath = sys.argv[1]
    panorama = cv2.imread(panoramapath)
    videopath = sys.argv[2]
    transcriptpath = sys.argv[3]
    objdir = sys.argv[4]
    outfilename = sys.argv[5]
    visobjs = VisualObject.objs_from_file(videopath, objdir)
    lecture = Lecture(videopath, transcriptpath)
    
    list_of_ts = []
    list_of_objimgs = []
    for obj in visobjs:
        list_of_ts.append(lecture.video.fid2ms(obj.end_fid))
        list_of_objimgs.append(obj.img)
    
    """Segment Transcript"""
    transcript_segs = lecture.segment_script(list_of_ts)
    
    list_of_areas = get_map(panorama, list_of_objimgs)
    
    write_html(outfilename, panoramapath, transcript_segs, list_of_areas)
    
    
    
        
    