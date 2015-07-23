#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import sys
import processframe as pf

if __name__ == "__main__":     
    print "Count and print/plot foreground pixels"
    video = sys.argv[1]
    pv = processvideo.ProcessVideo(video)  
    counts = pv.countfgpix(pf.BLACK_BG_THRESHOLD)
    pv.printfgpix(counts)
        
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
        #plt.savefig(pv.videoname + "_sub_smooth.jpg")
        #plt.close()        

        

    