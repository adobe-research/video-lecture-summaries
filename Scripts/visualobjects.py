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
from scipy import ndimage
import os

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
        self.width = brx - tlx+1
        self.height = bry - tly+1
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
        w = max_brx - min_tlx+1
        h = max_bry - min_tly+1
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
        print 'objfile', objfile
        obj_list = []
        obj_info = util.list_of_vecs_from_txt(objfile)
        obj_info.pop(0)
        obj_endts = [obj[1] for obj in obj_info]
        obj_endts = util.strings2ints(obj_endts)
        print len(obj_info)
        for i in range(0, len(obj_info)):
            info = obj_info[i]
            imgpath = os.path.basename(str(info[6]))
            objimg = cv2.imread(objdir + "/" + imgpath)
            obj = VisualObject(objimg, imgpath, int(info[0]), int(info[1]), int(info[2]), int(info[3]), int(info[4]), int(info[5]))
            obj_list.append(obj)
        return obj_list      
    
    @staticmethod
    def write_to_file(outfilepath, list_of_objs):
        objinfo = open(outfilepath, "w")
        objinfo.write("start_fid \t end_fid \t tlx \t tly \t brx \t bry\t filename\n")
        for obj in list_of_objs:
            objinfo.write("%i\t%i\t%i\t%i\t%i\t%i\t%s\n" %(obj.start_fid, obj.end_fid, obj.tlx, obj.tly, obj.brx, obj.bry, obj.imgpath ))
        objinfo.close()
    
    def segment_cc(self, mask=None):
        """segment into connected componnets""" 
        if mask is None:
            mask = pf.fgmask(self.img, 50, 255, True)
        label_im, num_labels = ndimage.label(mask)
        temp = os.path.splitext(self.imgpath)
        img_prefix = temp[0]
#         util.showimages([self.img, mask], self.imgpath)
        list_of_objs = []
        for i in range(0, num_labels+1):
            label_mask = (label_im == i)
            label_img = self.img.copy()
            label_img[label_mask==0] = 0
#             util.showimages([label_img])
#             label_img, new_mask = pf.croptofg(self.img, label_mask)
            if (label_img is None):
                print 'label image is None'
                continue
            new_mask = pf.fgmask(label_img, 50, 255, True)
            (tlx2, tly2, brx2, bry2) = pf.fgbbox(new_mask)
            label_img = pf.cropimage(label_img, tlx2, tly2, brx2, bry2)
            if (tlx2 < 0):
                continue
            label_imgpath = img_prefix + "_%03i" %i + ".png"
            print label_imgpath
            cv2.imwrite(label_imgpath, label_img)
            label_obj = VisualObject(label_img, label_imgpath, self.start_fid, self.end_fid, self.tlx + tlx2, self.tly + tly2, self.tlx + brx2, self.tly + bry2)
            list_of_objs.append(label_obj)
#             util.showimages([label_obj.img], "segment_cc new image %i" %i)
        return list_of_objs
        
        
    @staticmethod
    def avg_height(list_of_objs):
        hsize = 0.0
        for obj in list_of_objs:
            hsize = hsize + (obj.bry - obj.tly)
        avg_hsize = hsize/len(list_of_objs)
        return avg_hsize
    
    @staticmethod
    def avg_duration(list_of_objs):
        dur = 0.0    
        for obj in list_of_objs:
            dur = dur + (obj.end_fid - obj.start_fid)
        avg_dur = dur/len(list_of_objs)
        return avg_dur
        
if __name__ == "__main__":
    objdirpath = sys.argv[1]
    objs_in_panorama = VisualObject.objs_from_file(None, objdirpath)
    VisualObject.group(objs_in_panorama)
    
    