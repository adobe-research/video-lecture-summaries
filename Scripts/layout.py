'''
Created on Sep 23, 2014

@author: Valentina
'''
#!/usr/bin/env python
import sys
from lecture import Lecture, LectureSegment
import processframe as pf
import process_aligned_json as pjson
import util
import cv2
import numpy as np
import cvxopt
import operator
from visualobjects import VisualObject


def layout_words_on_cursor_path():
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    cursorpath = sys.argv[3]    
    
    lecture = Lecture(videopath, scriptpath)   
    cursorpos = util.list_of_vecs_from_txt(cursorpath)   
    
    """layout word in each sentence"""
    stc_id = 0
    stc_ts = lecture.get_stc_end_times()
    print 'number of sentences', len(lecture.list_of_stcs)
    layoutdir = lecture.video.videoname + "_stc_endtime"
    keyframes = lecture.capture_keyframes_ms(stc_ts, layoutdir)
    for sentence in lecture.list_of_stcs:
        frame = keyframes[stc_id].frame
        for word in sentence:
            if word.issilent:
                continue
#             print word.original_word
            wordt = (word.startt + word.endt)/2.0
            (textsize, baseline) = textbbox(word.original_word)
            frameid = lecture.video.ms2fid(wordt)
            curpos = cursorpos[frameid]       
            if curpos[0] < 0:
                print 'cursor not tracked'
            curpos[0] = max(1, int(curpos[0]))
            print curpos[0]
            print max(1, int(curpos[0]))
            curpos[1] = max(textsize[1], int(curpos[1]))  
            print curpos[0], curpos[1]
            pf.writetext(frame, word.original_word, (int(curpos[0]), int(curpos[1])), fontscale=1.0, color=(0, 0, 0))
#         util.showimages([frame])          
        util.saveimage(frame, layoutdir, "sentence" +("%03i" %stc_id) +"_word.png")
        stc_id += 1
    
        
def inframe_cstr(obj_ws, obj_hs, obj_bases, frame_w, frame_h):
    vals = []
    rows = []  #rows
    cols = []  #cols
    b = []

    for i in range(0, len(obj_ws)):
        # x_i >= 0    -x_i <= 0
        rows.append(len(rows))
        cols.append(2*i)
        vals.append(-1)
        b.append(0)
        
        # x_i + txt_w[i] <= frame_w    x_i <= frame_w - txt_w[i]
        rows.append(len(rows))
        cols.append(2*i)
        vals.append(1)
        b.append(frame_w - obj_ws[i])
        
        # y_i - txt_hs[i] >= 0    -y_i <= txt_hs[i]
        rows.append(len(rows))
        cols.append(2*i+1)
        vals.append(-1)
        b.append(obj_hs[i])
        
        # y_i + obj_bases[i] <= frame_h    y_i <= frame_h-obj_bases[i]
        rows.append(len(rows))
        cols.append(2*i+1)
        vals.append(1)
        b.append(frame_h - obj_bases[i])
        
    A = cvxopt.spmatrix(vals, rows, cols)
    return (A, b)

def reading_order_cstr(obj_ws, obj_hs, obj_bases):
    # Only top-to-bottom
    n_objs = len(obj_ws)
    rows = []
    cols = []
    vals = []
    b = []
    n_cstr = 0
    for i in range(1, n_objs):
        # y_i + obj_bases[i] <= y_(i+1) - objs_hs[i+1]
        # y_i - y_(i+1) <= -obj_bases[i] - obj_hs[i+1])
        rows.append(n_cstr)
        cols.append(2*i+1)
        vals.append(1)
        rows.append(n_cstr)
        cols.append(2*(i+1)+1)
        vals.append(-1)
        b.append(-obj_bases[i] - obj_hs[i+1])
        n_cstr += 1
        
    A = cvxopt.spmatrix(vals, rows, cols)
    return (A, b)
        
def non_overlap_cstr(ws, hs, bases):
    # non-linear
    return

def textbbox(text):    
    textsize, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
    return (textsize, baseline)


def layout_line_by_line(objs_by_time):
    x_buffer = 10
    y_buffer = 10
    cury = 0
    objs_in_frame = []
    while(len(objs_by_time) > 0):
        curobj = objs_by_time.pop(0) # consider the earliest object
        if (curobj.istext):
            """Put curobj at (x_buffer, cury +y_buffer)"""
            newobj = curobj.copy()
            newobj.setx(x_buffer)
            newobj.sety(cury + y_buffer)
            cury = newobj.bry
            objs_in_frame.append(newobj)
        else:
            """Put curobj at (curobj.x, cury + y_buffer)"""
            min_tly = cury+y_buffer
            newobj = curobj.copy()
            min_tly = min(min_tly, curobj.tly)
#             newobj.sety(cury + y_buffer)
#             cury = newobj.bry
            objs_in_frame.append(newobj)
#             yshift = max(0, newobj.tly - curobj.tly)
            
#             """Put visual objects in-line with curobj"""
#             indices = []
#             for i in range(0, len(objs_by_time)):
#                 if not objs_by_time[i].istext:
#                     if objs_by_time[i].bry <= curobj.bry:
#                         indices.append(i)
#                         min_tly = min(min_tly, objs_by_time[i].tly)
            yshift = (cury + y_buffer - min_tly)
            newobj.shifty(yshift)
            cury = max(0, newobj.bry)
            
#             indices.reverse() # for pop 
#             for i in range(0, len(indices)):
#                 obj = objs_by_time.pop(indices[i])
#                 newobj = obj.copy()
#                 newobj.shifty(yshift)
#                 objs_in_frame.append(newobj)
#                 cury = max(cury, newobj.bry)
                
    return objs_in_frame

def layout_objects(list_of_objs):
    framew = 0
    frameh = 0
    margin = 10
    for obj in list_of_objs:
        framew = max(framew, obj.brx)
        frameh = max(framew, obj.bry)
    framew += margin
    frameh += margin
    print 'layout.layout_objects: framew, frameh:', framew, frameh
    img = np.ones((frameh, framew, 3), dtype=np.uint8) * 255 
    
    for obj in list_of_objs:
#         print obj.tlx, obj.tly, obj.brx, obj.bry
#         util.showimages([obj.img])
        img[obj.tly:obj.bry, obj.tlx:obj.brx, :] = obj.img    
    return img
    

if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
#     panorama = cv2.imread(sys.argv[4])
    
    lec = Lecture(videopath, scriptpath)
    
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
#     img_objs = VisualObject.objs_from_panorama(panorama, objdir)
    txt_objs = []
    for stc in lec.list_of_stcs:
        txt = ""
        for word in stc:
            if not word.issilent:
                txt = txt + " " + word.original_word
        txt = txt +"."
        txt_obj = VisualObject.fromtext(txt, lec.video.ms2fid(stc[0].startt), lec.video.ms2fid(stc[-1].endt))
        txt_objs.append(txt_obj)
    
    vis_objs = img_objs + txt_objs
    sorted_vis_objs = sorted(vis_objs, key=operator.attrgetter('start_fid'))
        
    objs_in_frame = layout_line_by_line(sorted_vis_objs)
    img = layout_objects(objs_in_frame)
#     util.showimages([img])
    util.saveimage(img, objdir, "linear_layout.png")
    
    
    
        
    
    
    
    
    
    
    