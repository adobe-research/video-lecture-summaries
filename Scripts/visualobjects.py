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
        return cls(img, None, start_fid, end_fid, 0, 0, textsize[0], textsize[1]+baseline, True, text)                        
        
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
        
    @classmethod
    def group(cls, list_of_imgobjs, objdir="temp"):
        min_tlx = sys.maxint
        min_tly = sys.maxint
        max_brx = -1
        max_bry = -1
        min_start_fid = sys.maxint
        max_end_fid = -1
        for imgobj in list_of_imgobjs:
            min_tlx = min(min_tlx, imgobj.tlx)
            min_tly = min(min_tly, imgobj.tly)
            max_brx = max(max_brx, imgobj.brx)
            max_bry = max(max_bry, imgobj.bry)
            min_start_fid = min(min_start_fid, imgobj.start_fid)
            max_end_fid = max(max_end_fid, imgobj.end_fid)
        w = max_brx - min_tlx
        h = max_bry - min_tly
        groupimg = np.ones((h, w, 3), dtype=np.uint8)*255
        for obj in list_of_imgobjs:
            """Assume images are white background"""
            resize_img = np.ones((h,w,3), dtype=np.uint8)*255
            new_tlx = obj.tlx - min_tlx
            new_tly = obj.tly - min_tly
            resize_img[new_tly:new_tly + obj.height, new_tlx:new_tlx + obj.width] = obj.img
            mask = pf.fgmask(resize_img, threshold=225, var_threshold=100)
            idx = mask != 0
            groupimg[idx] = resize_img[idx]
            groupimgname = "obj_%06i_%06i.png" %(min_start_fid, max_end_fid)
            util.saveimage(groupimg, objdir, groupimgname)
            imgpath = objdir + "/" + groupimgname
        return cls(groupimg, imgpath, min_start_fid, max_end_fid, min_tlx, min_tly, max_brx, max_bry)    
            
    @staticmethod
    def objs_from_transcript(lec):
        """Return list of objects, where each object corresponds to a sentence in lecture transcript """
        list_of_objs = []
        for stc in lec.list_of_stcs:
            txt = ""
            for word in stc:
                if not word.issilent:
                    txt = txt + " " + word.original_word
            txt_obj = VisualObject.fromtext(txt, lec.video.ms2fid(stc[0].startt), lec.video.ms2fid(stc[-1].endt))
            list_of_objs.append(txt_obj)
        return list_of_objs
        
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
    objdirpath = sys.argv[1]
    objs_in_panorama = VisualObject.objs_from_file(None, objdirpath)
    VisualObject.group(objs_in_panorama)
    