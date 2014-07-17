#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":     
    videolist = ["..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",
                 "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
                 "..\\SampleVideos\\more\\khan1\\khan1.mp4", "..\\SampleVideos\\more\khan2\\khan2.mp4",
                 "..\\SampleVidoes\\more\\mit1\\mit1.mp4", "..\\SampleVidoes\\more\\mit2\\mit2.mp4",
                 "..\\SampleVideos\\more\\mit3\\mit3.mp4",
                 "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
                 "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4",
                 "..\\SampleVideos\\more\\pentimento1\\pentimento1.mp4",
                 "..\\SampleVidoes\\more\\slide1\\slide1.mp4"]
    for video in videolist:
        pv = processvideo.ProcessVideo(video)
        outvideo = pv.videoname+"_proc1.avi"
       
        # Count foreground pixels
        print "Count foreground pixels"
        fgpixtxt = pv.videoname+"_numfgpix.txt"
        fgpixfile = open(fgpixtxt, "r")

        # Compute key frame locations
        print "Compute Key Frame Locations"
        counts = []
        for val in fgpixfile.readlines():
            counts.append(int(val))
        subsample = counts[0:len(counts):15]
        smoothsample = util.smooth(np.array(subsample))
        samplegrad = np.gradient(smoothsample)
        samplegrad = abs(samplegrad)
        t = np.linspace(0, len(samplegrad), len(samplegrad))
        plt.plot(t, samplegrad, "b")
        #
        #prevsample = 0
        #gradthres = 1000
        #fn_filename = pv.videoname + "_sampleframes.txt"
        #sampleframe = open(fn_filename, "w")
        #for i in xrange(0, len(samplegrad)):
        #    if (samplegrad[i] <= 0 and abs(samplegrad[i]) < gradthres and i - prevsample > 10):
        #        plt.axvline(i, color="r")
        #        sampleframe.write("%i\n" % (i*15))
        #        prevsample = i
        ##t = np.linspace(0, len(counts), len(counts))
        #t = np.linspace(0, len(smoothsample), len(smoothsample))
        ##plt.plot(t, counts, color="b")
        #plt.plot(t, smoothsample, color = "b")
        #plt.xlabel("frames")
        plt.xlabel("time(sec)")       
        plt.ylabel("pixel diff")
        plt.title("Gradient")
        #plt.xlim(0, len(counts))
        plt.xlim(0, len(smoothsample))
        plt.savefig(pv.videoname + "_absgrad.jpg")
        plt.close()
        #sampleframe.close()
    
        # Capture Key Frames
        #print "Capture Key Frames"
        #fnumbers = []
        #frametxt = open(fn_filename, "r")
        #for val in frametxt.readlines():
        #    fnumbers.append(int(val))
        #array = np.array(fnumbers)
        #pv = processvideo.ProcessVideo(video)
        #if not os.path.exists(pv.videoname + "\sampleframes"):
        #    os.makedirs(pv.videoname+"\sampleframes")
        #if not os.path.exists(pv.videoname + "\keyframes"):
        #    os.makedirs(pv.videoname+"\keyframes")
        #pv.captureframes(fnumbers, pv.videoname+"\keyframes//")
        #print "Compute Frame Differences"
        #pv.captureframediffs(fnumbers, pv.videoname+"\keyframes//", pv.videoname+"\sampleframes//")

    