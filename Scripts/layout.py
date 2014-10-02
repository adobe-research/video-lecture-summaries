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



if __name__ == "__main__":    
    layout_word()
    
#     
#     videopath = sys.argv[1]
#     scriptpath = sys.argv[2]
#     lecture = Lecture(videopath, scriptpath)
#     
#     """segment lecture"""
#     framediffpath = sys.argv[3]
#     keyframe_ts = util.get_keyframe_ts_framediff(framediffpath, lecture.video.fps)    
#     lecsegs = lecture.segment(keyframe_ts, lecture.video.videoname + "_framediff")        
#      
#     """read cursor path"""
#     cursorpath = sys.argv[4]    
#     cursorpos = util.list_of_vecs_from_txt(cursorpath)   
#      
#     """layout word in each segment"""
#     layoutdir = lecture.video.videoname+"_layout"
#          
#     for lecseg in lecsegs:
#         sentences = pjson.get_sentences(lecseg.list_of_words)   
#         stc_id = 0  
#         for stc in sentences:            
#             stc_start = stc[0].startt
#             stc_end = stc[-1].endt
#             start_frame = lecture.video.ms2fid(stc_start)
#             end_frame = lecture.video.ms2fid(stc_end)
#             z_cursorpos = map(list, zip(*cursorpos))
#             avg_xpos = np.mean(util.strings2ints(z_cursorpos[0][start_frame:end_frame+1]))
#             avg_ypos = np.mean(util.strings2ints(z_cursorpos[1][start_frame:end_frame+1]))
#            
#             frame = lecseg.keyframe.frame.copy()
#             text = pjson.listofwords2text(stc)
#             pf.writetext(frame, text, (int(avg_xpos), int(avg_ypos)), fontscale=1.0, color=(255, 255, 255))
#             util.showimages([frame])          
#             util.saveimage(frame, layoutdir, lecseg.keyframe.frame_filename +"_stc" + ("%02i" % stc_id)  + ".png")
#             stc_id += 1