#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import sys


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
    
    
    for video in videolist:
        gradzero = False
        
        pv = processvideo.ProcessVideo(video)
        outvideo = pv.videoname+"_proc1.avi"
       
        # Count foreground pixels
        print "Count foreground pixels"
        fgpixtxt = pv.videoname+"_numfgpix.txt"
        fgpixfile = open(fgpixtxt, "r")
        counts = []
        for val in fgpixfile.readlines():
            counts.append(int(val))
        
        # Smooth and subsample 1 frame per second
        print "Smooth and subsmaple 1 frame per second"
        smoothsample = util.smooth(np.array(counts))
        subsample = counts[0:len(smoothsample):int(pv.framerate)]
        
        # Compute gradient
        samplegrad = np.gradient(subsample)
        t = np.linspace(0, len(samplegrad), len(samplegrad))
        plt.plot(t, samplegrad, "b")
        plt.xlabel("time(sec)")       
        plt.ylabel("gradient")
        plt.title("Gradient")
        plt.xlim(0, len(samplegrad))
        
        # segment based on where gradient is 0
        autoframe = open(pv.videoname + "_gradzero_frame.txt", "w")
        frame = []
        fnumbers = []
        sec = 0
        gradthres = int(sys.argv[1])
        print 'gradthres = ', gradthres
        for grad in samplegrad:
            if abs(grad) < gradthres:
                if not gradzero:
                    autoframe.write("%i\n" % sec)
                    frame.append(int(sec))
                    fnumbers.append(sec*pv.framerate)
                    gradzero = True
            elif abs(grad) > gradthres:
                gradzero = False
            sec += 1
        
        print "Automatic Segmentation"        
        for f in frame:
            plt.axvline(f, color="g")
        plt.axhline(gradthres, color="r")
        plt.axhline(-gradthres, color = "r")
        
        autoframe.close()    
        plt.savefig(pv.videoname + "_gradzero" + str(gradthres) + ".jpg")
        plt.close()
        
        # Capture Key Frames
        
        #print "Capture Key Frames"
        capturedir = "_gradzero"+str(gradthres)+"_keyframes"
        if not os.path.exists(pv.videoname + capturedir):
            os.makedirs(pv.videoname + capturedir)
        pv.captureframes(fnumbers, pv.videoname + capturedir + "\\")
        
    