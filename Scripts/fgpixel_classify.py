#!/usr/bin/env python
import processvideo
import processframe as pf
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys


if __name__ == "__main__":       
    
    videolist = ["..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",
                 "..\\SampleVideos\\more\\khan1\\khan1.mp4", "..\\SampleVideos\\more\\khan2\\khan2.mp4",
                 "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
                  "..\\SampleVideos\\more\\mit1\\mit1.mp4",  "..\\SampleVideos\\more\\mit2\\mit2.mp4", "..\\SampleVideos\\more\\mit3\\mit3.mp4",
                 "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
                  "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4"]


    for video in videolist:
        pv = processvideo.ProcessVideo(video)
        counts = pv.readfgpix()

        # Smooth and subsample
        smoothsample = util.smooth(np.array(counts), window_len = pv.framerate)
        subsample = counts[0:len(smoothsample):int(pv.framerate)]
        t = np.linspace(0, len(subsample), len(subsample))
        
        actionfilename = pv.videoname + "_action.txt"
        actionfile = open(actionfilename, "w")
        
        scroll_thres = 5e3
        dec_thres = -2e3
        prevpix = 0
        color = []
        starttimes = []
        endtimes = []
        for i in range(0, len(subsample)):
            curpix = subsample[i]
            if (curpix - prevpix < dec_thres or abs(curpix-prevpix) > scroll_thres):  # erase or scroll
                status = 0
                endtimes.append(i)
            else:
                status = 1
                starttimes.append(i)                
            actionfile.write("%i\n" % status)
            prevpix = curpix
        actionfile.close()
        

        
        

        
        
        
        

    