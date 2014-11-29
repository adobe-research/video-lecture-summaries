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
        print self.numframes
        print self.framerate
        self.endt = self.numframes/self.framerate
        if ("mit" in self.videoname or
            "tecmath" in self.videoname or
            "hwt" in self.videoname or
            "armando" in self.videoname or
            "udacity" in self.videoname or
            "pentimento" in self.videoname or
            "slide" in self.videoname):
            self.videotype = "mit"
        else:
            self.videotype = "khan"        
        cap.release()
        print self.video
        print self.videoname
        print self.videotype
        print 'framerate', self.framerate
    
    def tracktemplate(self, template):
        cap = cv2.VideoCapture(self.video)
        pos = []
        i = 0
        while (cap.isOpened()):
            ret, frame = cap.read()
            if (ret == True):                
                loc = pf.find_template_ctr(frame, template)
                pos.append(loc)                
            else:
                break
            print i, '/', self.numframes 
            i += 1  
        cap.release()                  
        return pos
    
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
    
    def getframe_at_time(self, sec):
        """Get frame at specified time"""
        cap = cv2.VideoCapture(self.video)
        framei = 0
        while(cap.isOpened()):          
            ret, frame = cap.read()
            if (ret == True):
                if(framei == sec*self.framerate):
                    cap.release()
                    return frame
                framei += 1
            else:
                break
        cap.release()
        return
       
    def countfgpix(self, fgthres):
        """Return number of foreground pixels"""    
        cap = cv2.VideoCapture(self.video)    
        counts = np.empty(self.numframes)
        index = 0

        while(index < self.numframes):
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            counts[index] = pf.numfgpix_thresh(gray, fgthres)
            index += 1
        cap.release()
        return counts    

    def readfgpix(self):
        """Return number of foreground pixels"""
        fgpixtxt = self.videoname+"_numfgpix.txt"
        fgpixfile = open(fgpixtxt, "r")
        fgpix = []
        for val in fgpixfile:
            fgpix.append((int(val)))
        return fgpix

    def printfgpix(self, counts, txtfilename=None):
        """Print and plot number of foreground pixels per frame"""
        txtfilename = self.videoname + "_numfgpix.txt"        
        imagefilename = self.videoname +"_numfgpix.png"
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
        plt.savefig(imagefilename)
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
    
    def removelogo(self, gray_logos, color):
        cap = cv2.VideoCapture(self.video)
        
        outvideo = self.videoname+"_removelogo.avi"
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(outvideo, int(fourcc), int(self.framerate), (int(self.width), int(self.height)))
        
        while(cap.isOpened()):
            ret, frame = cap.read()
            if (frame == None):
                break
                       
            for gray_logo in gray_logos:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                wlogo, hlogo = gray_logo.shape[::-1]
                tlx, tly = pf.find_object_exact_inside(gray_frame, gray_logo)
                brx = tlx + wlogo
                bry = tly + hlogo
                frame[tly:bry, tlx:brx, 0] = color[0]
                frame[tly:bry, tlx:brx, 1] = color[1]
                frame[tly:bry, tlx:brx, 2] = color[2]
            
            out.write(frame)
        cap.release()
        out.release()
        print 'output:' , outvideo
    

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
        cap.release()
        return
    

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
                tx, ty = pf.find_object_exact_inside(gray_src, gray_template)
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
        

    




