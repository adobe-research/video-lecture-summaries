#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":     
    #videolist = ["..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",
    #             "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
    #             "..\\SampleVideos\\more\\mit3\\mit3.mp4",
    #             "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
    #              "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4"]
  
    videolist = ["..\\SampleVideos\\more\\armando2\\armando2.mp4"]
    for video in videolist:
        pv = processvideo.ProcessVideo(video)  
       
        #Count foreground pixels
        #print "Count and print/plot foreground pixels"
        #counts = pv.countfgpix()
        #pv.printfgpix(counts)
        
        # Subsample and smooth
        #print "Subsample and smooth foreground pixel count"
        #fgpixtxt = pv.videoname+"_numfgpix.txt"
        #fgpixfile = open(fgpixtxt, "r")
        #counts = []
        #for val in fgpixfile.readlines():
        #    counts.append(int(val))
        #subsample = counts[0:len(counts):int(pv.framerate)]
        #smoothsample = util.smooth(np.array(subsample))
        #t = np.linspace(0, len(smoothsample), len(smoothsample))
        #plt.plot(t, smoothsample, color = "g")
        #plt.xlabel("time(sec)")
        #plt.ylabel("Number of foreground pixels")
        #plt.title("Subsampled and smoothed")
        #plt.xlim(0, len(smoothsample))
        #fgpixfile.close()
        
        # read manul time cuts
        print "Manual Segmentation"
        manualtime = open(pv.videoname + "_manualtime.txt", "r")
        manualframe = open(pv.videoname + "_manualframe.txt", "w")
        frame = []
        for val in manualtime.readlines():
            time = val.split('.')
            print time
            sec = int(time[0]) * 60 + int(time[1])
            manualframe.write("%i\n" % sec)        
            frame.append(int(sec))
        manualframe.close()
        manualtime.close()
        
        for f in frame:
            plt.axvline(f, color="r")
        
        plt.savefig(pv.videoname + "_manframe.jpg")
        plt.close()
        
        # Capture Manual Key Frames
        print "Capture Key Frames"
        farray = np.array(frame)
        farray *= pv.framerate
        if not os.path.exists(pv.videoname + "_manual_keyframes"):
            os.makedirs(pv.videoname+"_manual_keyframes")
        pv.captureframes(farray, pv.videoname+"_manual_keyframes\\")

    