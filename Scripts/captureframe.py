'''
Created on Jan 7, 2015

@author: hijungshin
'''

import sys
from processvideo import ProcessVideo
import util

if __name__ == "__main__":     
    videoname = sys.argv[1]
    outdir = sys.argv[2]
    fnumbers = [5010, 5015]
    pv = ProcessVideo(videoname)
    pv.captureframes(fnumbers, outdir)