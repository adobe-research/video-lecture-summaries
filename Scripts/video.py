#!/usr/bin/env python
import os
import re
import cv2
import numpy as np
import processframe as pf

class Keyframe:
    def __init__(self, frame_path, frame, time, framenum):
        self.frame_path = os.path.abspath(frame_path)
        self.frame = frame
        self.time = time
        self.framenum = framenum

class Video:
    def __init__(self, filepath):
        self.filepath = filepath
        self.extension = os.path.splitext(filepath)[1]
        self.videoname = re.sub(self.extension, '', filepath)
        tempcap = cv2.VideoCapture(filepath)
        self.width = int(tempcap.get(3))
        self.height = int(tempcap.get(4))
        self.fps = np.rint(tempcap.get(5))
        self.numframes = np.rint(tempcap.get(7))
        self.startt = 0.0
        self.endt = (self.numframes / self.fps)*1e3
        self.fourcc = int(tempcap.get(6))
        tempcap.release()
   
    def cut(self, ms_start, ms_end, outfile=None):
        """Cut the video from start time to end time (in milliseconds) and write to outpath
            Hack: use CV_FOURCC('D','I','V','X') and save as .avi file, then rename back to orignal extension
            TODO: audio lost in cutting"""        
        cap = cv2.VideoCapture(self.filepath)
        if outfile==None:
            outfile = self.videoname + "_" + str(ms_start) + "_" + str(ms_end) + ".avi"
        print 'fourcc', self.fourcc
        print  'fps', self.fps
        print 'width', self.width
        print 'height', self.height
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(outfile, int(fourcc), self.fps, (self.width, self.height))
        while(cap.isOpened()):          
            ret, frame = cap.read()
            if (ret == True):
                if (cap.get(0) >= ms_start and cap.get(0) < ms_end):
                    out.write(frame)
                elif (cap.get(0) >= ms_end):
                  break
            else:
                break
        cap.release()
        out.release()
        newoutfile = self.videoname + "_" + str(ms_start) + "_" + str(ms_end) + ".mp4"
        os.rename(outfile, newoutfile)
        return newoutfile
    
    def fid2ms(self, fid):
        return int(fid/self.fps * 1000)
    
    def ms2fid(self, ms):
        return int(ms*self.fps)
            
    def captureframes_fid(self, fnumbers, outdir= "."):
        if not os.path.exists(os.path.abspath(outdir)):
            os.makedirs(os.path.abspath(outdir))
            
        keyframes = []
        cap = cv2.VideoCapture(self.filepath)
        fid = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if (frame == None):
                break
            if (fid in fnumbers):
                filename = outdir + "/capture_"        
                filename = filename + ("%06i" % fid) + ".png"
                cv2.imwrite(filename, frame)
                keyframes.append(Keyframe(filename, frame, self.fid2ms(fid), fid))
            fid += 1
        cap.release()
        return keyframes
    
    def captureframes_ms(self, ts, outdir="."):
        tol =  1000.0/self.fps
        if not os.path.exists(os.path.abspath(outdir)):
            os.makedirs(os.path.abspath(outdir))
            
        keyframes = []
        cap = cv2.VideoCapture(self.filepath)
        i = 0
        pos = float(0.0)
        while(cap.isOpened()):                        
            ret, frame = cap.read()
            if (frame == None):
                break           
            if (abs(pos - float(ts[i])) < tol):
                filename = outdir + "/capture_"        
                filename = filename + ("%06f" % ts[i]) + "ms.png"
                cv2.imwrite(filename, frame)
                print 'writing', filename
                keyframes.append(Keyframe(filename, frame, ts[i], self.ms2fid(ts[i])))                
                i += 1
                if (i == len(ts)):
                    break
            pos += float(1000.0/self.fps )
        cap.release()
        return keyframes
    
    def highlight_new(self):
        """Highlight new part in each frame using absdiff with previous frame"""
        cap = cv2.VideoCapture(self.filepath)
        prevframe = np.empty((self.height, self.width, 3), dtype=np.uint8)
        while (True):
            ret, frame = cap.read()
            if (not ret):
                break
            
            diff = cv2.absdiff(frame, prevframe)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY)
            highlight_frame = pf.highlight(frame, mask)
            cv2.imshow("highlight", highlight_frame)
            prevframe = frame
            
            if  cv2.waitKey(int(1000/self.fps)) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        pass
    