#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import sys
import subprocess

if __name__ == "__main__":
    print 'Argument List:', str(sys.argv)
    video = sys.argv[1]
    startt = sys.argv[2]
    endt = sys.argv[3]
    pv = processvideo.ProcessVideo(video)
    print ['ffmpeg', '-i', video, '-ss', startt, '-t', endt, '-async 1', pv.videoname + "_cut.mp4"]
    subprocess.call(['ffmpeg', '-i', video, '-ss', startt, '-t', endt, '-async', '1', pv.videoname + "_cut.mp4"])
