#!/usr/bin/env python
import cv2
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy import signal
import processframe as pf
import util
from PIL import Image
import os
import time
import ntpath
import re

class ProcessVideo:
    def __init__(self, video):
        self.video = video
        extension = os.path.splitext(video)[1]
        self.videoname = re.sub(extension, '', self.video)
        cap = cv2.VideoCapture(video)
        self.width = cap.get(3)
        self.height = cap.get(4)
        self.framerate = np.rint(cap.get(5))
        self.numframes = np.rint(cap.get(7))
        self.startt = 0
        self.endt = self.numframes/self.framerate
        if ("mit" in self.videoname or
            "tecmath" in self.videoname or
            "hwt" in self.videoname or
            "armando" in self.videoname or
            "udacity" in self.videoname or
            "pentimento" in self.videoname or
            "slide" in self.videoname):
            self.videotype = "mit"
        elif ("khan" in self.videoname):
            self.videotype = "khan"        
        else:
            raise("video type not specified!")
        cap.release()
        print self.video
        print self.videoname
        print self.videotype
        print 'framerate', self.framerate
    
    def cutvideo(self, start, end):
        """Cut the video from start time to end time"""
        cap = cv2.VideoCapture(self.video)
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(self.videoname+"_"+str(start)+"_"+str(end)+".avi", int(fourcc), int(self.framerate), (int(self.width), int(self.height)))
        framei = 0

        while(cap.isOpened()):          
            ret, frame = cap.read()
            if (ret == True):
                if(framei >= start*self.framerate  and framei <= end*self.framerate):
                    out.write(frame)                    
                framei += 1
            else:
                break

        cap.release()
        out.release()
        return
   
    def countfgpix(self):
        """Return number of foreground pixels"""    
        cap = cv2.VideoCapture(self.video)    
        counts = np.empty(self.numframes)
        index = 0

        while(index < self.numframes):
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if (self.videotype == "mit"):
                counts[index] = pf.numfgpix_mit(gray)
            elif(self.videotype == "khan"):
                counts[index] = pf.numfgpix_khan(gray)
            index += 1
        cap.release()
        return counts    


    def printfgpix(self, counts, txtfilename=None):
        """Print and plot number of foreground pixels per frame"""
        txtfilename = self.videoname + "_numfgpix.txt"        
        imagefilename = self.videoname +"_numfgpix.jpg"
        print txtfilename, imagefilename
        txtfile = open(txtfilename, 'w')
        for n in counts:
            txtfile.write("%i\n" % n)
        txtfile.close()
        t = np.linspace(0, len(counts), len(counts))
        plt.plot(t, counts)
        plt.title("Number of Foreground Pixels")
        plt.xlabel("frames")
        plt.ylabel("pixels")
        plt.xlim(0, len(counts))
        plt.savefig(self.videoname + "_fgpix.jpg")
        plt.close()
        return txtfilename
    
    def removebackground(self, bgsample, outvideo):
        cap = cv2.VideoCapture(self.video)
        print bgsample
        gray_bgsample = cv2.imread(bgsample, 0)
        
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(outvideo, int(fourcc), int(self.framerate), (int(self.width), int(self.height)))
        while(cap.isOpened()):
            ret, frame = cap.read()
            if (frame == None):
                break
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sub_frame = pf.removebackground(gray_frame, gray_bgsample)
            out.write(sub_frame)
        cap.release()
        out.release()
    
    #def getchangeframes(self, counts, gradthres):
    #    subsample = counts[0:len(counts):15]
    #    smoothsample = util.smooth(np.array(subsample))
    #    samplegrad = np.gradient(smoothsample)
    #    return        

    #def getfgpeaks(self, fgpixfilename=None):
    #    """Return frame number where peak of drawing activity occurs"""
    #    if fgpixfilename==None:
    #        fgpixfilename = printfgpix()
    #    fgpixfile = open(fgpixfilename, "r")
    #    counts = []
    #    for val in fgpixfile.readlines():
    #        counts.append(int(val))
    #    array = np.array(counts)
    #    peaks = sp.signal.find_peaks_cwt(array, np.arange(2*framerate, 4*framerate, framerate), None, None, None, None, 1, 10)
    #    return peaks
    #
    #def printfgpeaks(self, fgpixfilename=None, outfile="fgpeaks"):
    #    """Print peak frames by counting foreground pixels per frame"""
    #    peaks = getfgpeaks(fgpixfilename)
    #    peaktxt = open(outfile+".txt", "w")
    #    for peak in peaks:
    #        peaktxt.write("%i\n" % peak)    
    #    peaktxt.close()
    #    return
    #
    #def plotfgpeaks(self, fgpixfilename, fgpeaksfilename, outfile="fgpeaks.png"):
    #    fgpixfile = open(fgpixfilename, "r")
    #    peaks = open(fgpeaksfilename, "r")
    #    numfgpix = []
    #    
    #    plt.figure(1)
    #    t = np.linspace(0, numframe, numframe)        
    #    for val in fgpixfile.readlines():
    #        numfgpix.append(int(val))
    #    plt.plot(t, numfgpix, 'b')
    #    
    #    for peak in fgpeaksfilename.readlines():
    #        plt.axvline(peak, color="r")
    #    
    #    plt.xlim(0, numframe)
    #    plt.xlabel("time (frame id)")
    #    plt.ylabel("Number of Foreground pixels")
    #    plt.savefig(outfile)

    def captureframes(self, fnumbers, outdir= "./"):
        cap = cv2.VideoCapture(self.video)
        fid = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if (frame == None):
                break
            if (fid in fnumbers):
                filename = outdir + "capture_"        
                filename = filename + ("%06i" % fid) + ".png"
                cv2.imwrite(filename, frame)               
            fid += 1
        return
        cap.release()

    def captureframediffs(self, fnumbers, indir="./", outdir="./"):
        for x in range(0, len(fnumbers)-1):
            bfr = fnumbers[x]
            aft = fnumbers[x+1]
            bfr_filename = indir + "capture_" + ("%06i" %bfr) + ".png"
            aft_filename = indir + "capture_" + ("%06i" %aft) + ".png"
            im_bfr = cv2.imread(bfr_filename)
            im_aft = cv2.imread(aft_filename)
            img = cv2.absdiff(im_aft, im_bfr)
            filename = outdir + "framediff_"+("%06i" %bfr)+"_"+("%06i" %aft)+".png"
            cv2.imwrite(filename, img)
        return    

    
    def removetemplate(self, templates, outvideo):
        """Remove templates from video"""
        print "templates"
        for tempfilename in templates:
            print tempfilename
        bgcolor = [0]
        thres = 10
        cap = cv2.VideoCapture(self.video)        
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(outvideo, int(fourcc), int(self.framerate), (int(self.width), int(self.height)))

        while(cap.isOpened()):
            ret, frame = cap.read()
            if (frame == None):
                break
            src = frame.copy()
            gray_src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for template in templates:
                gray_template = cv2.imread(template, 0)  
                mask = np.zeros(gray_src.shape, dtype=np.uint8)                
                tx, ty = pf.matchtemplate(gray_src, gray_template)
                th, tw = gray_template.shape
                for j in range(0, th):
                    for i in range(0, tw):
                        if (gray_template[j, i] > thres):
                            mask[ty+j, tx+i] = 255
#                            src[ty+j, tx+i] = [0, 0, 0]
                img = Image.fromarray(mask)
                img.save("mask.png")
                mask = cv2.imread('mask.png', 0)
                src = cv2.inpaint(src,mask,3,cv2.INPAINT_TELEA)                
            out.write(src)                        
        cap.release()
        out.release()
        return

if __name__ == "__main__":     
    videolist = ["..\\SampleVideos\\more\\mit1.mp4", "..\\SampleVideos\\more\\mit2.mp4"]
    for video in videolist:
        pv = ProcessVideo(video)
        counts = pv.countfgpix()
        pv.printfgpix(counts)
        

    




