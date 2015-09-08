#!/usr/bin/env python
import processvideo 
import sys
import processframe as pf

if __name__ == "__main__":     
    print "Count and print/plot foreground pixels"
    video = sys.argv[1]
    pv = processvideo.ProcessVideo(video)    
    is_black = int(sys.argv[2])
    if (is_black == 1):
        is_black = True
        thres = pf.BLACK_BG_THRESHOLD
    else:
        is_black = False
        thres = pf.WHITE_BG_THRESHOLD
    
    counts = pv.countfgpix(is_black, thres)    
    pv.printfgpix(counts)
