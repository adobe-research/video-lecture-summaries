'''
Created on Sep 23, 2014

@author: Valentina
'''
#!/usr/bin/env python
import sys
from lecture import Lecture, LectureSegment
import processframe as pf
import util

if __name__ == "__main__":    
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    cursorpath = sys.argv[3]
    cursorpos = util.list_of_vecs_from_txt(cursorpath)   
   
    lecture = Lecture(videopath, scriptpath)
     
    for word in lecture.list_of_words:
        t = (word.startt + word.endt) / 2.0  # milliseconds
        framei = lecture.video.ms2fid(t)
        print framei
        frame = lecture.video.getframe_ms(t)
        pos = cursorpos[framei]
        print word.original_word
        print pos
        pf.writetext(frame, word.original_word, (int(pos[0]), int(pos[1])), fontscale=1.0, color=(255, 255, 255))
        util.showimages([frame])                     