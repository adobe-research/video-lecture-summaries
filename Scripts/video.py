#!/usr/bin/env python
import os
import re
import cv2
import numpy as np
import processframe as pf
import ntpath
import sys
import util


class Keyframe:
    def __init__(self, frame_path, frame, time, framenum, video=None):
        self.frame_path = os.path.abspath(frame_path)
        self.frame_filename = ntpath.basename(self.frame_path)
        self.extension = os.path.splitext(frame_path)[1]
        self.basename = re.sub(self.extension, '', frame_path) 
        self.frame = frame
        self.height, self.width = frame.shape[:2]
        self.time = time
        self.framenum = framenum
        self.startt = -1
        self.endt = -1
        self.video = video
        self.default_objs = []
        self.fg_mask = None
        if (video != None):
            self.add_default_objs(video.default_objs)
        else:
            self.add_default_objs([])
        self.newobj_mask = None
        
    def new_visual_score(self, ):
        if (self.newobj_mask == None):
            return -1
        return np.count_nonzero(self.newobj_mask)
    
    def add_default_objs(self, objs):
        if objs != None:
            self.default_objs += objs
        fgimg = pf.getnewobj(self.frame, self.default_objs)
        self.fg_mask = pf.fgmask(fgimg)        
        return
    
    def set_newobj_mask(self, objlist):
        objimg = pf.getnewobj(self.frame, objlist)
        mask = pf.fgmask(objimg)
        self.newobj_mask = cv2.bitwise_and(mask, self.fg_mask)
        return        
        
    def get_newobj(self, objlist):        
        fgimg = pf.getnewobj(self.frame, objlist + self.default_objs)
        newobj_mask = pf.fgmask(fgimg)       
        obj = pf.maskimage_white(self.frame)
        return obj
    
    def find_obj(self, obj):
        if obj == None:
            return None
        M = pf.find_object_appx_thres(obj)
        h,w = obj.shape[:2]
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        return dst
    
    def get_fgobj(self, includelogo = False):
        if includelogo:
            mask = pf.fgmask(self.frame)
        else:
            mask = self.fg_mask
        obj = pf.maskimage_white(self.frame, mask)
        return obj    
    
        
    def fg_bbox(self, default_objs=[]):
        bbox = pf.fgbbox(self.fg_mask)    
        return bbox
    
    def newobj_bbox(self, ):
        if self.newobj_mask == None:
            return self.fg_bbox()
        bbox = pf.fgbbox(self.newobj_mask)
        return bbox
    
    @staticmethod
    def get_keyframes(dirname):
        filelist = os.listdir(dirname)
        filelist = [ x for x in filelist if "capture" in x and ".png" in x and "fg" not in x and "overlap" not in x]
        #filelist.sort(cmp=util.filename_comp)
        
        keyframes = []   
        for filename in filelist:
            frame = cv2.imread(dirname + "/" + filename)
#             h, w = frame.shape[:2]
#             frame = frame[1:h-1, 1:w-1,:]
            keyframe = Keyframe(dirname + "/" + filename, frame, -1, -1)
            keyframes.append(keyframe)
        return keyframes
    
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
        self.default_objs = []
        
    def add_default_obj(self, obj):
        self.default_objs.append(obj)
        return    
    
    def extract_foreground(self, threshold, outfile=None):
        cap = cv2.VideoCapture(self.filepath)
        if outfile==None:
            outfile = self.videoname + "_foreground.avi"
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(outfile, int(fourcc), self.fps, (self.width, self.height))
        while(cap.isOpened()):          
            ret, frame = cap.read()
            if (ret == True):
                mask = pf.fgmask(frame, threshold)
                fgframe = pf.maskimage_white(frame, mask)
                util.showimages([frame, fgframe], "video.extract_forground")
                out.write(fgframe)
            else:
                break
        cap.release()
        out.release()
        newoutfile = self.videoname + "_foreground.mp4"
        os.rename(outfile, newoutfile)
        return newoutfile    
        
        
    def negate(self, outfile=None):
        cap = cv2.VideoCapture(self.filepath)
        if outfile==None:
            outfile = self.videoname + "_neagte.avi"
        fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
        out = cv2.VideoWriter(outfile, int(fourcc), self.fps, (self.width, self.height))
        while(cap.isOpened()):          
            ret, frame = cap.read()
            if (ret == True):
                negframe = 255 - frame
                out.write(negframe)
            else:
                break
        cap.release()
        out.release()
        newoutfile = self.videoname + "_negate.mp4"
        os.rename(outfile, newoutfile)
        return newoutfile    
   
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
    
    def fid2sec(self, fid):
        return int(fid/self.fps)
    
    def ms2fid(self, ms):
        return int(ms/1000.0*self.fps)
            
    def capture_keyframes_fid(self, fnumbers, outdir= "./temp"):
        if len(fnumbers) == 0:
            return []
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
                filename = filename + ("%06i" % fid) + "_fid.png"
                if not os.path.isfile(os.path.abspath(filename)):
                    print 'writing', os.path.abspath(filename)
                    cv2.imwrite(filename, frame)
#                 util.showimages([frame], "fid: %i"%fid)
                keyframes.append(Keyframe(filename, frame, self.fid2ms(fid), fid, self))
            fid += 1            
        
        cap.release()
        if (len(keyframes) != len(fnumbers)):
            print "%d out of %d frames captured" %(len(keyframes), len(fnumbers))
        return keyframes
    
    def captureframes_ms(self, ts, outdir="."):
        if len(ts) == 0:
            return []
        tol =  1000.0/self.fps
        if not os.path.exists(os.path.abspath(outdir)):
            os.makedirs(os.path.abspath(outdir))
            
        keyframes = []
        cap = cv2.VideoCapture(self.filepath)
        i = 0
        fid = 0
        pos = self.fid2ms(fid) #float(0.0)
#         print 'pos', pos
        while(cap.isOpened()):                        
            ret, frame = cap.read()
            if (frame == None):
                break   
            if (abs(pos - int(ts[i])) <= tol):
                filename = outdir + "/capture_"        
                filename = filename + ("%06.0f" % ts[i]) + "ms.png"
                if not os.path.isfile(os.path.abspath(filename)):
                    print 'writing', filename
                    cv2.imwrite(filename, frame)
                keyframes.append(Keyframe(filename, frame, ts[i], self.ms2fid(ts[i]), self))
                i += 1
                if (i == len(ts)):
                    break
            prevframe = frame
            fid += 1
            pos = self.fid2ms(fid)
        
        if (i == len(ts)-1):
            filename = outdir + "/capture_"        
            filename = filename + ("%06.0f" % ts[i]) + "ms.png"
            keyframes.append(Keyframe(filename, prevframe, ts[i], self.ms2fid(ts[i]), self))
        cap.release()
        if (len(keyframes) != len(ts)):
            print 'captureframes_ms: missing %i key frames' %(len(ts)-len(keyframes))
        return keyframes
    
    def getframe_ms(self, t):
        cap = cv2.VideoCapture(self.filepath)
        frame_t = 0.0
        tol = 1000.0/self.fps
        while(cap.isOpened()):          
            ret, frame = cap.read()
            if (ret == True):
                if(abs(t - frame_t) < tol):
                    cap.release()
                    return frame
                frame_t += 1000.0/self.fps
            else:
                break
        cap.release()
        return
    
    def getframe_fid(self, fid):
        cap = cv2.VideoCapture(self.filepath)
        frameid = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if (frameid == fid):
                return frame
            elif frameid > fid:
                break
        cap.release()
        return
    
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

    