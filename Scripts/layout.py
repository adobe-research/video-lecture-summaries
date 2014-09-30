'''
Created on Sep 23, 2014

@author: Valentina
'''
#!/usr/bin/env python
import sys
from lecture import Lecture, LectureSegment
import processframe as pf
import util
import cv2

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
    for lecseg in lecsegs:
        frame = lecseg.keyframe.frame.copy()
		numstc = lecseg.num_stc()
        for word in lecseg.list_of_words:
            if word.issilent:
                continue
            print word.original_word
            t = (word.startt + word.endt)/2.0
            frameid = lecture.video.ms2fid(t)
            curpos = cursorpos[frameid]            
            pf.writetext(frame, word.original_word, (int(curpos[0]), int(curpos[1])), fontscale=1.0, color=(255, 255, 255))
#             util.showimages([frame])          
        layoutdir = lecture.video.videoname+"_layout"
        util.saveimage(frame, layoutdir, lecseg.keyframe.frame_filename +"_word.png")