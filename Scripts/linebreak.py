'''
Created on Nov 14, 2014

@author: hijungshin
'''

from visualobjects import VisualObject
from kalman import KalmanFilter
import math
import util
import sys


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
    obj_miny = curobj.tly
    obj_maxy = curobj.bry
    obj_ctr = (curobj.bry + curobj.tly)/2.0       

    if (obj_ctr >= ymin - minvar):
        if (obj_ctr <= ymax + maxvar):
            return True
        print 'ymax, delta, objctr', ymax, maxvar, obj_ctr
        return False
    print 'ymin, delta, objctr', ymin, minvar, obj_ctr
    return False


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

def greedy_lines(list_of_objs):
    lineobjs = []    
    initobj = list_of_objs[0]    
    objs_in_line = [initobj]    
    ymin_kf = KalmanFilter(initobj.tly, initobj.height*initobj.height) 
    ymax_kf = KalmanFilter(initobj.bry, initobj.height*initobj.height)
    for i in range(1, len(list_of_objs)):
        curobj = list_of_objs[i]
        if inline(ymin_kf.state_mean, ymin_kf.state_var, ymax_kf.state_mean, ymax_kf.state_var, curobj):
            objs_in_line.append(curobj)            
            new_miny = min(ymin_kf.state_mean, curobj.tly)
            new_maxy = max(ymax_kf.state_mean, curobj.bry)
            ymin_kf.update(new_miny, new_maxy - new_miny)
            ymax_kf.update(new_maxy, new_maxy - new_miny)
        else:
            line = VisualObject.group(objs_in_line, "lineobj")
            util.showimages([line.img, curobj.img], "temp")
            lineobjs.append(line)
            objs_in_line = []
            objs_in_line.append(curobj)
            ymin_kf = KalmanFilter(curobj.tly, (curobj.height*curobj.height)) 
            ymax_kf = KalmanFilter(curobj.bry, (curobj.height*curobj.height))
    
    line = VisualObject.group(objs_in_line)
    util.showimages([line.img], "temp")
    lineobjs.append(line)
    return lineobjs
            
if __name__ == "__main__":
    objdirpath = sys.argv[1]    
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    greedy_lines(list_of_objs)
        

