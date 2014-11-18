'''
Created on Nov 14, 2014

@author: hijungshin
'''

from visualobjects import VisualObject
from kalman import KalmanFilter
import math
import util
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2

def is_jump(lineobjs, obj):
    return False

def time(lineobjs, obj, fps): 
    start_fid = lineobjs[0].start_fid
    end_fid = obj.end_fid
    nframes = end_fid - start_fid
    sec = nframes/fps
    return sec
    
def num_words():
    return -1

def visual_content():
    return -1

def frame_gap(lineobjs, obj):
    prev_end = lineobjs[-1].end_fid
    cur_start = obj.start_fid
    return (cur_start - prev_end)

def is_cut(lineobjs, obj, fps, min_gap, maxt, max_words, max_visual):
    if frame_gap(lineobjs, obj) < min_gap:
        return False
    if time(lineobjs, obj) > maxt:
        return True
    if num_words() > max_words:
        return True
    if visual_content() > max_visual:
        return True 
    if is_jump(lineobjs, obj):
        return True
    return False

def inline(ymin, minvar, ymax, maxvar, curobj):     
    if minvar == 0:
        minvar = (ymax - ymin)/5.0
    if maxvar == 0:
        maxvar = (ymax - ymin)/5.0  
    if (curobj.bry >= ymin - minvar):
        if (curobj.tly <= ymax + maxvar):
            return True
        print 'ymax + delta', ymax, '+', maxvar, '=', ymax+maxvar,   'objctr', curobj.tly
        return False
    print 'ymin - delta', ymin, '-', minvar, '=', ymin-minvar, 'objctr', curobj.bry
    return False


def show_inline_region(panorama, objs_in_line, miny, maxy, var1, var2, curobj):
    if var1 == 0:
        var1 = (maxy - miny)/5.0
    if var2 == 0:
        var2 = (maxy - miny)/5.0  
    
    pcopy = panorama.copy()
    curline = VisualObject.group(objs_in_line, "temp")
    # current line object
    cv2.rectangle(pcopy, (curline.tlx, curline.tly), (curline.brx, curline.bry), (0,0,255), 3)
    # inline region
    cv2.rectangle(pcopy, (curline.tlx, int(miny - var1)), (curline.brx, int(maxy + var2)), (255, 0, 0), 1)
    cv2.rectangle(pcopy, (curobj.tlx, curobj.tly), (curobj.brx, curobj.bry), (0,0,0), 1)
    util.showimages([pcopy])
    

def greedy_break(lec, list_of_objs, objdir, min_gap, maxt, max_words, max_visual):
    lineobjs = []
    objs_in_line = []
    for obj in list_of_objs:
        if is_cut(objs_in_line, obj, lec.video.fps, min_gap, maxt, max_words, max_visual):
            line = VisualObject.group(objs_in_line, objdir)
            lineobjs.append(line)
            objs_in_line = []
        else:
            objs_in_line.append(obj)
    return lineobjs



def greedy_lines(list_of_objs, panorama):
    lineobjs = []    
    initobj = list_of_objs[0]    
    objs_in_line = [initobj]  
    minys = []  
    maxys = []
    miny = initobj.tly
    maxy = initobj.bry
    minys.append(initobj.tly)
    maxys.append(initobj.bry)
    var1 = np.std(minys)
    var2 = np.std(maxys)
    for i in range(1, len(list_of_objs)):
        curobj = list_of_objs[i]
        show_inline_region(panorama, objs_in_line, miny, maxy, var1, var2, curobj)
        if inline(miny, var1, maxy, var2, curobj):
            if (miny > curobj.tly):
                miny = curobj.tly
                minys.append(miny)
            if (maxy < curobj.bry):
                maxy = curobj.bry
                maxys.append(maxy)
            objs_in_line.append(curobj)           
            var1 = np.std(minys)
            var2 = np.std(maxys)
        else:
            line = VisualObject.group(objs_in_line, "lineobj")
#             util.showimages([line.img, curobj.img], "lineobject")
            lineobjs.append(line)
            objs_in_line = []
            objs_in_line.append(curobj)
            miny = curobj.tly
            maxy = curobj.bry
            minys = [miny]
            maxys = [maxy]
            var1 = np.std(minys)
            var2 = np.std(maxys)
    line = VisualObject.group(objs_in_line)
#     util.showimages([line.img], "temp")
    lineobjs.append(line)
    return lineobjs
            
if __name__ == "__main__":
    objdirpath = sys.argv[1]    
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    greedy_lines(list_of_objs)
        

