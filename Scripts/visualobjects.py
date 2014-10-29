'''
Created on Oct 8, 2014

@author: hijungshin
'''
import cv2
import numpy as np
import util
import sys
import processframe as pf
import matplotlib.pyplot as plt

class VisualObject:
    def __init__(self, img, imgpath, start_fid, end_fid, tlx, tly, brx, bry, istext=False, text=None):
        self.img = img
        self.imgpath = imgpath
        self.start_fid = start_fid
        self.end_fid = end_fid
        self.tlx = tlx
        self.tly = tly
        self.brx = brx
        self.bry = bry
        self.width = brx - tlx
        self.height = bry - tly
        self.istext = istext
        self.text = text
        
    @classmethod
    def fromtext(cls, text, start_fid, end_fid):        
        (textsize, baseline) = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
        img = np.ones((textsize[1]+baseline, textsize[0], 3), dtype=np.uint8) * 255
        cv2.putText(img, text, (0, textsize[1]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0))    
        return VisualObject(img, None, start_fid, end_fid, 0, 0, textsize[0], textsize[1]+baseline, True, text)                        
        
    def size(self):
        return (self.width, self.height)
    
    def copy(self):
        return VisualObject(self.img, self.imgpath, self.start_fid, self.end_fid, self.tlx, self.tly, self.brx, self.bry, self.istext, self.text)
    
    def shiftx(self, x):
        self.tlx += x
        self.brx += x
        
    def shifty(self, y):
        self.tly += y
        self.bry += y
        
    def setx(self, x):
        self.tlx = x
        self.brx = self.tlx + self.width
    
    def sety(self, y):
        self.tly = y
        self.bry = self.tly + self.height
        
    @staticmethod
    def objs_from_panorama(panorama, objdir, objtxt=None):
        if objtxt is None:
            objtxt = "obj_info.txt"
        objfile = objdir + "/" + objtxt
        obj_list = []
        obj_info = util.list_of_vecs_from_txt(objfile)
        obj_info.pop(0)
        for i in range(0, len(obj_info)):
            info = obj_info[i]
            obj = VisualObject(None, None, int(info[0]), int(info[1]), int(info[2]), int(info[3]), int(info[4]), int(info[5]))
            objimg = panorama[obj.tly:obj.bry, obj.tlx:obj.brx,:]
            obj.img = objimg
            obj_list.append(obj)
        return obj_list       
        
    @staticmethod
    def objs_from_file(video, objdir, objtxt=None):
        if objtxt is None:
            objtxt = "obj_info.txt"
        objfile = objdir + "/" + objtxt
        obj_list = []
        obj_info = util.list_of_vecs_from_txt(objfile)
        obj_info.pop(0)
        obj_endts = [obj[1] for obj in obj_info]
        obj_endts = util.strings2ints(obj_endts)
#         keyframes = video.capture_keyframes_fid(obj_endts)        
        for i in range(0, len(obj_info)):
            info = obj_info[i]
            imgpath = objdir + "/" + str(info[6])
            objimg = cv2.imread(imgpath)
            obj = VisualObject(objimg, imgpath, int(info[0]), int(info[1]), int(info[2]), int(info[3]), int(info[4]), int(info[5]))
            obj_list.append(obj)
        return obj_list       
        
if __name__ == "__main__":
    """Plot object y position within panorama"""
    panoramapath = sys.argv[1]
    panorama = cv2.imread(panoramapath)
    videopath = sys.argv[2]
    objdir = sys.argv[3]
    visobjs = VisualObject.objs_from_file(videopath, objdir)
    outfile = sys.argv[4]
    
    ypos = []
    for obj in visobjs:
        objh, objw = obj.img.shape[:2]
        tl = pf.find_object_exact_inside(panorama, obj.img, 0.25)
        if tl is None:
            ypos.append(-1.0)
        else:
            ypos.append(tl[1] + objh/2)
    
    plt.plot(ypos, 'o')
    plt.xlabel('Objects')
    plt.ylabel('y-position')
    plt.xlim(0, len(visobjs))
    plt.savefig(outfile)
    plt.show()
    plt.close()
    
    

    
    
    
