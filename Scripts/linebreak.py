'''
Created on Nov 14, 2014

@author: hijungshin
'''

from visualobjects import VisualObject

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


