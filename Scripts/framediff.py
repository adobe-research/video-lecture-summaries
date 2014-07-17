#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import cv2


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
        pv = processvideo.ProcessVideo(video)
       
        #cap = cv2.VideoCapture(pv.video)    
        #counts = np.empty(pv.numframes-1)
        #ret,prevframe = cap.read()
        #index = 1        
        #while(index < pv.numframes):
        #    ret, nextframe = cap.read()
        #    if (nextframe == None):
        #        break
        #    diff = cv2.absdiff(nextframe, prevframe)
        #    prevframe = nextframe
        #    counts[index-1] = np.sum(diff)
        #    index += 1            
        #cap.release()
        #
        #framedifftxt = pv.videoname+"_framediff.txt"
        #framediff = open(framedifftxt, "w")
        #for val in counts:
        #    framediff.write("%i\n" % int(val))
        #framediff.close()
        #
        #t = np.linspace(0, len(counts), len(counts))
        #plt.plot(t, counts, color = "b")
        #plt.xlabel("frames")
        #plt.ylabel("Frame Difference")
        #plt.xlim(0, len(counts))
        #plt.savefig(pv.videoname + "_framediff.jpg")
        #plt.close()
        
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
      
        
        print "Manual Segmentation"
        manualtime = open(pv.videoname + "_manualtime.txt", "r")
        manualframe = open(pv.videoname + "_manualframe.txt", "w")
        frame = []
        values = []
        for val in manualtime.readlines():
            time = val.split('.')
            print time
            sec = int(time[0]) * 60 + int(time[1])
            manualframe.write("%i\n" % sec)        
            frame.append(int(sec))
            values.append(subsample[sec])
        manualframe.close()
        manualtime.close()
              
      
        for f in frame:
            plt.axvline(f, color="r")
        
        plt.axhline(max(values), color="g")
        
        
        plt.savefig(pv.videoname+"_framediff_smooth.jpg")
        plt.close()        

        