#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


if __name__ == "__main__":     
    #videolist = ["..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",
    #             "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
    #             "..\\SampleVideos\\more\\mit3\\mit3.mp4",
    #             "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
    #             "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4",
    #videolist = ["..\\SampleVideos\\more\\mit3\\mit3.mp4", "..\\SampleVideos\\more\\hwt1\\hwt1.mp4", "..\\SampleVideos\\more\\hwt2\\hwt2.mp4"]#, "..\\SampleVideos\\more\\khan2\\khan2.mp4",
    #             "..\\SampleVideos\\more\\mit1\\mit1.mp4", "..\\SampleVideos\\more\\mit2\\mit2.mp4"]  
    videolist = ["..\\SampleVideos\\more\\pentimento1\\pentimento1.mp4"]
    for video in videolist:
        pv = processvideo.ProcessVideo(video)  
       
        #Count foreground pixels
        #print "Count and print/plot foreground pixels"
        #counts = pv.countfgpix()
        #pv.printfgpix(counts)
        
        # Subsample and smooth
        minsamplewidth = 5
        thres = 10
        smwin = 15
        print "Subsample and smooth foreground pixel count"
        fgpixtxt = pv.videoname+"_numfgpix.txt"
        fgpixfile = open(fgpixtxt, "r")
        counts = []
        for val in fgpixfile.readlines():
            counts.append(int(val))
        subsample = counts[0:len(counts):int(pv.framerate)]
        smoothsample = util.smooth(np.array(subsample))
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
        plt.ylabel("Number of Foreground Pixels")
        plt.title("Gradient Gradient Key Frames")
        plt.xlim(0, len(smoothsample))
        plt.savefig(pv.videoname + "_gradgradframe.jpg")
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
        if not os.path.exists(pv.videoname + "_gradgrad_keyframes"):
            os.makedirs(pv.videoname+"_gradgrad_keyframes")
        pv.captureframes(fnumbers, pv.videoname+"_gradgrad_keyframes//")
    

    