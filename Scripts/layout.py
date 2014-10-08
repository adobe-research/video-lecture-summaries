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


def layout_word():
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    lecture = Lecture(videopath, scriptpath)   
    
    """read cursor path"""
    cursorpath = sys.argv[3]    
    cursorpos = util.list_of_vecs_from_txt(cursorpath)   
    
    """layout word in each sentence"""
    stc_id = 0
    stc_ts = lecture.get_stc_end_times()
    print 'len(stc_ts)', len(stc_ts)
    print 'len(list_of_stcs)', len(lecture.list_of_stcs)
    keyframes = lecture.capture_keyframes_ms(stc_ts, lecture.video.videoname + "_temp")
    print 'len(keyframes)', len(keyframes)
    for sentence in lecture.list_of_stcs:
        frame = keyframes[stc_id].frame
        for word in sentence:
            if word.issilent:
                continue
#             print word.original_word
            wordt = (word.startt + word.endt)/2.0
            frameid = lecture.video.ms2fid(wordt)
            curpos = cursorpos[frameid]       
            if cursorpos[0] < 0:
                cursorpos[0] = 1
                cursorpos[1] = 1      
            pf.writetext(frame, word.original_word, (int(curpos[0]), int(curpos[1])), fontscale=1.0, color=(0, 0, 0))
#             util.showimages([frame])          
        layoutdir = lecture.video.videoname+"_layout"
        util.saveimage(frame, layoutdir, "sentence" +("%03i" %stc_id) +"_word.png")
        stc_id += 1
        
def inframe_cstr(txt_ws, txt_hs, txt_bases, frame_w, frame_h):
    vals = []
    rows = []  #rows
    cols = []  #cols
    b = []

    for i in range(0, len(txt_ws)):
        # x_i >= 0    -x_i <= 0
        rows.append(len(rows))
        cols.append(2*i)
        vals.append(-1)
        b.append(0)        
        
        # x_i + txt_w[i] <= frame_w    x_i <= frame_w - txt_w[i]
        rows.append(len(rows))
        cols.append(2*i)
        vals.append(1)
        b.append(frame_w - txt_ws[i])
        
        # y_i - txt_hs[i] >= 0    -y_i <= txt_hs[i]
        rows.append(len(rows))
        cols.append(2*i+1)
        vals.append(-1)
        b.append(txt_hs[i])
        
        # y_i + txt_bases[i] <= frame_h    y_i <= frame_h-txt_bases[i]
        rows.append(len(rows))
        cols.append(2*i+1)
        vals.append(1)
        b.append(frame_h - txt_bases[i])
        
    A = cvxopt.spmatrix(vals, rows, cols)
    return (A, b)
        


def textbbox(text):
    
    textsize, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
    img = np.zeros((300, 300, 3))
    
    cv2.rectangle(img, (0, 0), (textsize[0], -textsize[1]), (255, 255, 255))
    cv2.rectangle(img, (0, baseline), (textsize[0], 100-textsize[1]-baseline), (0,255,0))
    
    cv2.putText(img, text, (0,0), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    cv2.imshow("image", img)
    cv2.waitKey(0)
    
    
  


if __name__ == "__main__":
    textbbox("my life")
    