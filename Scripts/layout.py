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

if __name__ == "__main__":    
    
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    lecture = Lecture(videopath, scriptpath)
    
    """segment lecture"""
    framediffpath = sys.argv[3]    
    keyframe_ts = util.get_keyframe_ts_framediff(framediffpath, lecture.video.fps)    
    lecsegs = lecture.segment(keyframe_ts, lecture.video.videoname + "_framediff")        
    
    """read cursor path"""
    cursorpath = sys.argv[4]    
    cursorpos = util.list_of_vecs_from_txt(cursorpath)   
    
    """layout word in each segment"""
    layoutdir = lecture.video.videoname+"_layout"
        
    for lecseg in lecsegs:
        sentences = pjson.get_sentences(lecseg.list_of_words)   
        stc_id = 0  
        for stc in sentences:            
            stc_start = stc[0].startt
            stc_end = stc[-1].endt
            start_frame = lecture.video.ms2fid(stc_start)
            end_frame = lecture.video.ms2fid(stc_end)
            z_cursorpos = map(list, zip(*cursorpos))
            avg_xpos = np.mean(util.strings2ints(z_cursorpos[0][start_frame:end_frame+1]))
            avg_ypos = np.mean(util.strings2ints(z_cursorpos[1][start_frame:end_frame+1]))
          
            frame = lecseg.keyframe.frame.copy()
            text = pjson.listofwords2text(stc)
            pf.writetext(frame, text, (int(avg_xpos), int(avg_ypos)), fontscale=1.0, color=(255, 255, 255))
            util.showimages([frame])          
            util.saveimage(frame, layoutdir, lecseg.keyframe.frame_filename +"_stc" + ("%02i" % stc_id)  + ".png")
            stc_id += 1