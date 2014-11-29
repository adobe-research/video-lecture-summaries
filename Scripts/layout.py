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
import linebreak

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
    nfig = 1
    for obj in list_of_objs:
        html.opendiv()
        if obj.istext:
            html.pragraph_string(obj.text)
        else:
            html.figure(obj.imgpath, "Figure %i" % nfig)
            nfig += 1
        html.closediv()
    return html

    
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
    print lec.video.fps
    img_objs = VisualObject.objs_from_file(lec.video, objdir)

    line_objs = linebreak.dynamic_lines(img_objs, 120*lec.video.fps)
    line_objs.reverse()
    
    html = WriteHtml(objdir + "/dynamic_linebreak_images.html", title="line break images", stylesheet="../Mainpage/summaries.css")
    html.opendiv(idstring="summary-container")
    stc_idx = 0
    nfig = 1
    for obj in line_objs:
        t = lec.video.fid2ms(obj.end_fid)
        paragraph = []
        while(lec.list_of_stcs[stc_idx][-1].endt < t):
            #write sentence
            paragraph = paragraph + lec.list_of_stcs[stc_idx]
            stc_idx += 1
            if (stc_idx >= len(lec.list_of_stcs)):
                break
        html.paragraph_list_of_words(paragraph)
        html.figure(obj.imgpath, "Figure %i" % nfig)
        nfig += 1
    html.closediv()
    html.closehtml()
    
    
     
    
        
    
    
    
    
    
    
    