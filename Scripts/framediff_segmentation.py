#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.signal import argrelextrema



if __name__ == "__main__":     
    videolist = ["..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",
                 "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
                 "..\\SampleVideos\\more\\khan1\\khan1.mp4", "..\\SampleVideos\\more\khan2\\khan2.mp4",
                 "..\\SampleVideos\\more\\mit1\\mit1.mp4", "..\\SampleVideos\\more\\mit2\\mit2.mp4",
                 "..\\SampleVideos\\more\\mit3\\mit3.mp4",
                 "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
                 "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4",
                 "..\\SampleVideos\\more\\pentimento1\\pentimento1.mp4",
                 "..\\SampleVideos\\more\\slide1\\slide1.mp4"]
    
    min_width = 5 #seconds
    for video in videolist:
               
        pv = processvideo.ProcessVideo(video)
        outvideo = pv.videoname+"_proc1.avi"
       
        # Count frame difference
        print "Read framediff.txt"
        framedifftxt = pv.videoname+"_framediff.txt"
        framedifffile = open(framedifftxt, "r")
        counts = []
        for val in framedifffile.readlines():
            counts.append(int(val))
        
        # Smooth and subsample 1 frame per second
        print "Smooth and subsmaple 1 frame per second"
        smoothsample = util.smooth(np.array(counts))
        subsample = counts[0:len(smoothsample):int(pv.framerate)]
        t = np.linspace(0, len(subsample)-1, len(subsample))        
        plt.plot(t, subsample, "bo-")
        plt.xlabel("time(sec)")       
        plt.ylabel("Frame Difference")
        plt.xlim(0, len(subsample))
        
        
        average = np.mean(subsample)
        thres = float(sys.argv[1]) * average
        
        fn_filename = pv.videoname +"_framediff_absmin_"+str(sys.argv[1])+"_keyframes.txt"
        keyframe = open(fn_filename, "w")
        frame = []
        fnumbers = []
        sec = 0
        capturing = False
        for diff in subsample:
            if diff < thres:
                if not capturing:                    
                    frame.append(int(sec))                    
                    plt.axvline(sec, color="g")
                    fnumbers.append(sec*pv.framerate)
                    keyframe.write("%i\n" % (sec*pv.framerate))
                    capturing = True
            elif diff > thres:
                capturing = False
            sec += 1
        plt.axhline(thres, color="r")
        plt.savefig(pv.videoname + "_framediff_absmin_"+str(sys.argv[1])+".jpg")
        plt.close()
        keyframe.close()
    
        #Capture Key Frames
        fnumbers = []
        frametxt = open(fn_filename, "r")
        for val in frametxt.readlines():
            fnumbers.append(int(val))
        array = np.array(fnumbers)
        frametxt.close()
        
        print fnumbers
        print "Capture Key Frames"
        capturedir = "_framediff_absmin_keyframes_"+str(sys.argv[1])
        if not os.path.exists(pv.videoname + capturedir):
            os.makedirs(pv.videoname + capturedir)
        pv.captureframes(fnumbers, pv.videoname + capturedir + "\\")
        
    