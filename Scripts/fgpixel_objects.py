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
    
    videolist = ["..\\SampleVideos\\more\\khan1\\khan1.mp4", "..\\SampleVideos\\more\\khan2\\khan2.mp4",
                 "..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4",                 
                 "..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4",
                  "..\\SampleVideos\\more\\mit1\\mit1.mp4",  "..\\SampleVideos\\more\\mit2\\mit2.mp4", "..\\SampleVideos\\more\\mit3\\mit3.mp4",
                 "..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
                  "..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4"]

    for video in videolist:
        pv = processvideo.ProcessVideo(video)
        actionfilename = pv.videoname + "_action.txt"
        actionfile = open(actionfilename, "r")
        
        draw = False
        drawstart = []
        drawend = []
        starttimes = []
        endtimes = []
        sec = 0
        for stat in actionfile.readlines():
            stat = int(stat)
            if (stat == 1 and not draw):
                starttimes.append(sec)
                drawstart.append(pv.framerate*sec)
                draw = True
            elif (stat == 0 and draw):
                endtimes.append(sec-1)
                drawend.append(pv.framerate*(sec-1))
                draw = False
            sec += 1
        if (draw):
            drawend.append(pv.framerate*(sec-1))
            endtimes.append(sec-1)
            
        # Smooth and subsample
        counts = pv.readfgpix()
        smoothsample = util.smooth(np.array(counts), window_len = pv.framerate)
        subsample = counts[0:len(smoothsample):int(pv.framerate)]
        t = np.linspace(0, len(subsample), len(subsample))
        plt.plot(t, subsample)
        for val in starttimes:
            plt.axvline(val, color='g')
        for val in endtimes:
            plt.axvline(val, color='r')
        plt.xlim(-10.0, len(subsample))    
        plt.savefig(pv.videoname + "_fgpix_drawtimes.jpg")
        plt.close()
            
        startdir = pv.videoname + "startdraw"
        enddir = pv.videoname + "enddraw"
        if not os.path.exists(startdir):
            os.makedirs(startdir)
        if not os.path.exists(enddir):
            os.makedirs(enddir)
        pv.captureframes(drawstart, startdir+"/")
        pv.captureframes(drawend, enddir+"/")
        
        startfilelist = os.listdir(startdir)
        startimages = []
        for filename in startfilelist:
                startimages.append(cv2.imread(startdir+"/"+filename))
    
        endfilelist = os.listdir(enddir)
        endimages = []
        for filename in endfilelist:
            endimages.append(cv2.imread(enddir+"/"+filename))
        
        objectdir = pv.videoname + "fgobject"
        if not os.path.exists(objectdir):
            os.makedirs(objectdir)
            
        for i in range(0, len(startimages)):
            object_img = cv2.absdiff(startimages[i], endimages[i])
            cv2.imwrite(objectdir+"/object"+str(i)+".jpg", object_img)
        
        
    


        
    
    
                
