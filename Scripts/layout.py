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
from writehtml import WriteHtml
import mycluster
import panorama_object
import os

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

def layout_line_by_line_html(objs_by_time, img_objs_by_time, img_lines, html, objdir="temp"):
    img_id = 0
    for obj in objs_by_time:
        html.opendiv()
        if obj.istext:
            html.pragraph_string(obj.text)
        else:
            linenum = img_lines[img_id]
            inline_objs = [obj]
            for i in range(0, img_id):
                
                if (img_lines[i] == linenum):
                    
                    inline_objs.append(img_objs_by_time[i])
            inlineobj = VisualObject.group(inline_objs, objdir)
            html.image(inlineobj.imgpath)
            img_id += 1
        html.closediv()
    return

def layout_objects_html(list_of_objs, html):
    for obj in list_of_objs:
        html.opendiv()
        if obj.istext:
            html.pragraph_string(obj.text)
        else:
            html.image(obj.imgpath)
        html.closediv()
    return

    
def layout_objects_img(list_of_objs):
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
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    
    lec = Lecture(videopath, scriptpath)
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
    txt_objs = VisualObject.objs_from_transcript(lec)
    
    
    timethres = 5*VisualObject.avg_duration(img_objs)
    linethres = 3*VisualObject.avg_height(img_objs)
    print 'timethres', timethres, 'linethres', linethres
    timeobjs = mycluster.cluster_wth_threshold(img_objs, timethres, linethres, objdir)
    
    panorama_cluster = panorama_object.draw_clusters(panorama, timeobjs, range(len(timeobjs))) 
    outfile1 = objdir + "/" + "threshold_cluster_panorama.png"
    cv2.imwrite(outfile1, panorama_cluster)
    
    
    img_line_labels = mycluster.get_line_labels(timeobjs, 1*VisualObject.avg_height(timeobjs))
    print '# lines', len(np.unique(img_line_labels))
    panorama_lines = panorama_object.draw_clusters(panorama, timeobjs, img_line_labels)
    outfile2 = objdir + "/" + "threshold_line_cluster_panorama.png"
    cv2.imwrite(outfile2, panorama_lines)
    

     
    vis_objs = timeobjs + txt_objs
    sorted_vis_objs = sorted(vis_objs, key=operator.attrgetter('start_fid'))
    sorted_img_objs = sorted(timeobjs, key=operator.attrgetter('start_fid')) 
     
    html = WriteHtml(objdir + "/" + "threshold_cluster_lines.html", "Objects clustered with time/linebreak threshold", stylesheet="../Mainpage/summaries.css")
    html.image(outfile1, idstring="panorama_cluster")
    html.image(outfile2, idstring ="panorama_cluster")
    html.opendiv(idstring="summary-container")
    html.writestring("<h1>" + lec.video.videoname + "</h1>")
    layout_line_by_line_html(sorted_vis_objs, sorted_img_objs, img_line_labels, html, objdir)
    html.closediv()
    html.closehtml()
     
    
        
    
    
    
    
    
    
    