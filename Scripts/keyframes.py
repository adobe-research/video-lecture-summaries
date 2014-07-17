#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


if __name__ == "__main__":     
    videolist = ["..\\SampleVideos\\more\\slide1\\slide1.mp4"]
    for video in videolist:
        pv = processvideo.ProcessVideo(video)
        outvideo = pv.videoname+"_proc1.avi"
       
        # Count foreground pixels
        #print "Count foreground pixels"
        fgpixtxt = pv.videoname+"_numfgpix.txt"
        fgpixfile = open(fgpixtxt, "r")

        # Compute key frame locations
        #print "Compute Key Frame Locations"
        minsamplewidth = 5
        thres = 20
        counts = []
        smwin = 15
        for val in fgpixfile.readlines():
            counts.append(int(val))
        subsample = counts[0:len(counts):int(pv.framerate)]
        smoothsample = util.smooth(np.array(subsample), smwin)
        samplegrad = np.gradient(smoothsample)
        gradgrad = np.gradient(samplegrad)
        extreme = argrelextrema(gradgrad, np.less) #local minimum
        prevsample = -1
        t = np.linspace(0, len(smoothsample), len(smoothsample))
        
        fn_filename = pv.videoname +"_gradgrad_keyframes.txt"
        keyframe = open(fn_filename, "w")
        keyframe.write("%i\n" % 1)
        plt.plot(t, smoothsample, "g")
        for ex in extreme:
            for val in ex:
                if (abs(gradgrad[val]) > thres and val - prevsample > minsamplewidth):
                    plt.axvline(val, color = "r")
                    keyframe.write("%i\n" % (val*int(pv.framerate)))
                    prevsample = val
    
        plt.xlabel("time(sec)")       
        plt.ylabel("Num Foreground Pixels")
        plt.title("Key Frames")
        plt.xlim(0, len(smoothsample))
        plt.savefig(pv.videoname + "_gradgrad_keyframes.jpg")
        plt.close()          
        keyframe.close()
    
        #Capture Key Frames
        print "Capture Key Frames"
        fnumbers = []
        frametxt = open(fn_filename, "r")
        for val in frametxt.readlines():
            fnumbers.append(int(val))
        array = np.array(fnumbers)
        frametxt.close()
        
        pv = processvideo.ProcessVideo(video)
        if not os.path.exists(pv.videoname + "\gradgrad_keyframes"):
            os.makedirs(pv.videoname+"\gradgrad_keyframes")
        pv.captureframes(fnumbers, pv.videoname+"\gradgrad_keyframes//")
    
        #print "Compute Frame Differences"
        #if not os.path.exists(pv.videoname + "\gradgrad_diff"):
        #    os.makedirs(pv.videoname+"\gradgrad_diff")
        #pv.captureframediffs(fnumbers, pv.videoname+"\gradgrad_keyframes//", pv.videoname+"\gradgrad_diff//")

    