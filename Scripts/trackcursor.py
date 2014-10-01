'''
Created on Sep 30, 2014

@author: Valentina
'''

import sys
import processvideo as pv
import cv2

if __name__ == "__main__":    
    videoname = sys.argv[1]
    cursorfile = sys.argv[2]
    video = pv.ProcessVideo(videoname)
    cursor = cv2.imread(cursorfile)
    pos = video.tracktemplate(cursor)
    cursorpostxt = video.videoname+"_cursorpos.txt"
    print cursorpostxt
    cursorpos = open(cursorpostxt, "w")
    for p in pos:
        if (p == None):
            cursorpos.write("%i\t%i\n" % (-1, -1))            
        else:
            cursorpos.write("%i\t%i\n" % (int(p[0]), int(p[1])))
    cursorpos.close()