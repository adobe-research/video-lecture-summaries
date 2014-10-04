#!/usr/bin/env python
import processvideo
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys

def compute(videoprocessor, diffthres=25):       
    cap = cv2.VideoCapture(videoprocessor.video)    
    counts = np.empty(pv.numframes - 1)
    ret, prevframe = cap.read()
    index = 1        
    while(index < videoprocessor.numframes):
        ret, nextframe = cap.read()
        if (nextframe == None):
            break
        diff = cv2.absdiff(nextframe, prevframe)        
        prevframe = nextframe
        counts[index - 1] = (diff > diffthres).sum()
        ret, dst = cv2.threshold(util.grayimage(diff), diffthres, 255, cv2.THRESH_BINARY_INV)
#         util.showimages([prevframe, nextframe, dst])
        util.showimages([nextframe])
        print 'counts', counts[index-1]
        index += 1            
    cap.release()
    return counts    


def write(counts, filename="framediff.txt"):
    framediff = open(filename, "w")
    for val in counts:
        framediff.write("%i\n" % int(val))
    framediff.close()
    
def plotperframe(counts, filename="_framediff_perframe.png"):
    t = np.linspace(0, len(counts)-1, len(counts))        
    plt.plot(t, counts, "bo-")
    plt.xlabel("Frame Number")       
    plt.ylabel("Absolute Difference")
    plt.xlim(0, len(counts))
    plt.savefig(filename)
    plt.close()       
  
def plotpersec(counts, fps, filename="_framediff_persec.png"):
    smoothsample = util.smooth(np.array(counts))
    subsample = counts[0:len(smoothsample):int(fps)]
    t = np.linspace(0, len(subsample)-1, len(subsample))        
    plt.plot(t, subsample, "bo-")
    plt.xlabel("Time(sec)")       
    plt.ylabel("Absolute Difference")
    plt.xlim(0, len(subsample))
    plt.savefig(filename)
    plt.close()
  

if __name__ == "__main__":
    videopath = sys.argv[1] 
    pv = processvideo.ProcessVideo(videopath)
    counts = compute(pv)
   
    """Write to file"""
#     framedifftxt = pv.videoname + "_framediff.txt"
#     write(counts, framedifftxt) 
    
    """Read frame difference"""
#     framedifftxt = sys.argv[2]
    #framediff = util.stringlist_from_txt(framedifftxt)
    #counts = util.strings2ints(framediff)
    
    """Smooth and Sub-sample 1 frame per second"""
#     plotpersec(counts, pv.framerate, pv.videoname + "_framediff_persec.png")