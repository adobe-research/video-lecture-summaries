'''
Created on Jun 26, 2015

@author: hijungshin
'''
import sys
import cv2
from video import Video
import util
import processframe as pf

if __name__ == "__main__":
    video = Video(sys.argv[1])
    panorama = cv2.imread(sys.argv[2])
    outfile1 = video.videoname + "_scroll.txt"
    scrolltxt = open(outfile1, "w")
    outfile2 = video.videoname + "_scroll_ids.txt"
    scrollid_txt = open(outfile2, "w")
    
    prev = None
    cap = cv2.VideoCapture(video.filepath)
    fid = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if (frame == None):
            break
        topleft = pf.find_object_exact_inside(panorama, frame, threshold=0)
        scrolltxt.write("%i\t%i\n"%(topleft[0], topleft[1]))
        
        if (prev is not None):
            dx = topleft[0] - prev[0]
            dy = topleft[1] - prev[1]
            if (dx != 0 or dy != 0):
                scrollid_txt.write("%i\n"%fid)
        fid += 1        
        prev = topleft
        
    scrolltxt.close()
    scrollid_txt.close()    