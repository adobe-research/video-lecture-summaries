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
import math
from video import Video
from scipy.signal import argrelextrema



class VisualObject:
    def __init__(self, img, imgpath, start_fid, end_fid, tlx, tly, brx, bry, istext=False, text=None, isgroup=False, members=None):
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
        self.isgroup = isgroup
        if (self.isgroup):
            self.members = members
        else:
            self.members = [self]
                   
    @classmethod
    def fromtext(cls, text, start_fid, end_fid):        
        (textsize, baseline) = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
        img = np.ones((textsize[1]+baseline, textsize[0], 3), dtype=np.uint8) * 255
        cv2.putText(img, text, (0, textsize[1]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0))    
        return cls(img, None, start_fid, end_fid, 0, 0, textsize[0], textsize[1]+baseline, True, text)                        
        
    def size(self):
        return (self.width, self.height)
    
    def copy(self):
        return VisualObject(self.img, self.imgpath, self.start_fid, self.end_fid, self.tlx, self.tly, self.brx, self.bry, self.istext, self.text, self.isgroup, self.members)
    
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
        
    def color(self):
        # Assume white (255) background
        mask = pf.fgmask(self.img, 254)
        fgimg = self.img[mask != 0]
        b = self.img[:,:,0]
        g = self.img[:,:,1]
        r = self.img[:,:,2]
        mean_b = np.mean(b[mask!=0])
        mean_g = np.mean(g[mask!=0])
        mean_r = np.mean(r[mask!=0])
        return (mean_b, mean_g, mean_r)
              
        
    @classmethod
    def group(cls, list_of_imgobjs, objdir="temp", debug=False):    
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
        debug_i = 0
        for obj in list_of_imgobjs:
            """Assume images are white background"""
            resize_img = np.ones((h,w,3), dtype=np.uint8)*255
            new_tlx = obj.tlx - min_tlx
            new_tly = obj.tly - min_tly
            objh, objw = obj.img.shape[:2]
            resize_img[new_tly:new_tly + objh, new_tlx:new_tlx + objw] = obj.img
            mask = pf.fgmask(resize_img, threshold=225, var_threshold=100)
            idx = mask != 0
            groupimg[idx] = resize_img[idx]
            if (debug and (debug_i == 0)):
                cv2.rectangle(groupimg, (new_tlx, new_tly), (new_tlx + objw, new_tly+objh), (0,0,255), 2)
            if (debug and (debug_i == len(list_of_imgobjs)-1)):
                cv2.rectangle(groupimg, (new_tlx, new_tly), (new_tlx + objw, new_tly+objh), (100,100,0), 2)
                
            debug_i += 1
        groupimgname = "obj_%06i_%06i_group.png" %(min_start_fid, max_end_fid)

        util.saveimage(groupimg, objdir, groupimgname)
        imgpath = objdir + "/" + groupimgname
        return cls(groupimg, imgpath, min_start_fid, max_end_fid, min_tlx, min_tly, max_brx, max_bry, isgroup=True, members=list_of_imgobjs)    
            
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
        return [self]
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
    def ygap_distance(obj_i, obj_j):
        # obj i above obj j
        if (obj_i.bry < obj_j.tly):
            return (obj_j.tly - obj_i.bry)
        # obj i below obj j
        if (obj_i.tly > obj_j.bry):
            return (obj_i.tly - obj_j.bry) 
        # partial overlap
        return 0
    
    @staticmethod
    def xgap_distance(obj_i, obj_j):
        i_right = obj_i.brx
        j_left = obj_j.tlx
        return j_left - i_right
        
    @staticmethod
    def colorgap_distance(obj_i, obj_j):
        (b1,g1,r1) = obj_i.color()
        (b2,g2,r2) = obj_j.color()
        dist = ((b1-b2)*(b1-b2) + (g1-g2)*(g1-g2) + (r1-r2)*(r1-r2))/(3.0*255.0*255.0)
        return dist
        
    @staticmethod    
    def duration_frames(obj_i, obj_j):
        """number of frames inbetween start of object i and end of object j"""
        nframes = obj_j.end_fid - obj_i.start_fid
        return nframes

    @staticmethod
    def gap_frames(obj_i, obj_j):
        """number of frames elapsed between end of object i to start of object j"""
        nframes = obj_j.start_fid - obj_i.end_fid
        return nframes
        
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
    
    @staticmethod
    def plot_time_gap(list_of_objs, objdir, video):
        time_gaps = []
        binsize = 0.5
        for i in range(0, len(list_of_objs)-1):
            curobj = list_of_objs[i]
            nextobj = list_of_objs[i+1]
            time_gap = (nextobj.start_fid - curobj.end_fid)/video.fps
            time_gaps.append(time_gap)    
        max_gap = math.ceil(max(time_gaps))
        bins = np.linspace(0, max_gap, max_gap/binsize+1)
        rprobs, rbins, rpatches = plt.hist(time_gaps, bins, normed=False)
        plt.savefig(objdir + "/obj_tgap_hist.png")
        plt.close()      
        plt.plot(time_gaps)
        plt.savefig(objdir + "/obj_tgap.png")
        plt.close()      
        
    @staticmethod
    def plot_xgap(list_of_objs, objdir):
        x_gaps = []
        binsize = 10
        for i in range(0, len(list_of_objs)-1):
            curobj = list_of_objs[i]
            nextobj = list_of_objs[i+1]
            xgap = VisualObject.xgap_distance(curobj, nextobj)
            x_gaps.append(xgap)
        max_gap = math.ceil(max(x_gaps))
        bins = np.linspace(0, max_gap, max_gap/binsize+1)
        rprobs, rbins, rpatches = plt.hist(x_gaps, bins, normed=False)
        plt.savefig(objdir + "/obj_xgap_hist.png")
        plt.close()        
        plt.plot(x_gaps)
        plt.savefig(objdir + "obj_xgap.png")
        plt.close()
        
    @staticmethod
    def plot_ygap(list_of_objs, objdir):
        y_gaps = []
        binsize = 10
        for i in range(0, len(list_of_objs)-1):
            curobj = list_of_objs[i]
            nextobj = list_of_objs[i+1]
            ygap = VisualObject.ygap_distance(curobj, nextobj)
            y_gaps.append(ygap)
        max_gap = math.ceil(max(y_gaps))
        bins = np.linspace(0, max_gap, max_gap/binsize+1)
        rprobs, rbins, rpatches = plt.hist(y_gaps, bins, normed=False)
        plt.savefig(objdir + "/obj_ygap_hist.png")
        plt.close()     
        plt.plot(y_gaps)
        plt.savefig(objdir + "/obj_ygap.png")
        plt.close()
    
    @staticmethod
    def overlap(obj1, obj2):
        area1 = (obj1.brx + 1 - obj1.tlx) * (obj1.bry + 1 - obj1.tly)
        area2 = (obj2.brx + 1 - obj2.tlx ) * (obj2.bry + 1 - obj2.tly)
        areai = max(0, min(obj1.brx + 1, obj2.brx + 1) - max(obj1.tlx, obj2.tlx)) * max(0, min(obj1.bry + 1, obj2.bry + 1) - max(obj1.tly, obj2.tly))
        return 1.0 * areai / min(area1, area2)
    
    @staticmethod
    def plot_color_gap(list_of_objs, objdir):
        color_gaps = []
        binsize = 0.01
        for i in range(0, len(list_of_objs)-1):
            curobj = list_of_objs[i]
            nextobj = list_of_objs[i+1]
            colordist = VisualObject.colorgap_distance(curobj, nextobj)
            color_gaps.append(colordist)
        max_gap = math.ceil(max(color_gaps))
        bins = np.linspace(0, max_gap, max_gap/binsize+1)
        rprobs, rbins, rpatches = plt.hist(color_gaps, bins, normed=False)
        plt.savefig(objdir + "/obj_colorgap_hist.png")
        plt.close()     
        plt.plot(color_gaps)
        plt.savefig(objdir + "/obj_colorgap.png")
        plt.close()
        
    @staticmethod
    def area_projection_function(list_of_objs, objdir, panorama, w1, w2):
        h, w = panorama.shape[:2]
        y = np.empty(h, dtype=np.uint8)
        for i in range(0, h):
            count = 0
            for obj in list_of_objs:
                if obj.tly <= i and i <= obj.bry and obj.tlx > w1 and obj.tlx <=w2:
                    count += 1#obj.width * obj.height
            y[i] = count
        ysmooth = util.smooth(y, window_len = 100)
        plt.plot(ysmooth)
        plt.savefig(objdir + "/area_projection_function.png")
#         plt.show()
        return y
        
    @staticmethod
    def bbox(list_of_objs):
        tlx = float("inf")
        tly = float("inf")
        brx = -1.0
        bry = -1.0
        for obj in list_of_objs:
            tlx = min(tlx, obj.tlx)
            tly = min(tly, obj.tly)
            brx = max(brx, obj.brx)
            bry = max(bry, obj.bry)
        return (int(tlx), int(tly), int(brx), int(bry))
    
    @staticmethod
    def inline(curobj, prevobj):
        z1minx, z1miny, z1maxx, z1maxy = VisualObject.bbox([prevobj])
        z1width = z1maxx - z1minx + 1
        xpad = 30
        ypad = min(max(30, 2500.0/z1width), 50)
        z1minx -= xpad
        z1miny -= ypad
        z1maxx += xpad
        z1maxy += ypad
        cy = (curobj.tly + curobj.bry) / 2.0
        
          
        if z1miny <= cy and cy <= z1maxy:
            if curobj.brx >= z1minx and curobj.tlx <= z1maxx: # in bbox 
                return True
            elif curobj.brx < z1minx: # inline left:
                penalty = z1minx - curobj.brx + xpad
                if (penalty < 100): 
                    return True
            elif curobj.tlx > z1maxx: #inline right:
                penalty = curobj.tlx - z1maxx + xpad
                if (penalty < 100):
                    return True
        return False
        
        
            
        
if __name__ == "__main__":
    objdirpath = sys.argv[1]
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    
    panoramapath = sys.argv[2]
    panorama = cv2.imread(panoramapath)
    ph,pw = panorama.shape[0:2]    
    panorama_copy = panorama.copy()
    panorama_copy2 = panorama.copy()
    for i in range(0, 4):
        w1 = (i*0.25) * pw
        w2 = (i+1)*0.25 *pw
        y = VisualObject.area_projection_function(list_of_objs, objdirpath, panorama, w1, w2)
        ysmooth = util.smooth(y, window_len=100)
        maxys = argrelextrema(ysmooth, np.greater)
        minys = argrelextrema(ysmooth, np.less)
        for y in maxys[0]:
            cv2.line(panorama_copy, (int(w1), y), (int(w2), y), (255,255,255), 1)
        for y in minys[0]:
            cv2.line(panorama_copy2, (int(w1), y), (int(w2), y), (255,255,255), 1)
        util.showimages([panorama_copy2], "minlines")
#         util.showimages([panorama_copy], "maxlines")
    
    #util.saveimage(panorama_copy2, objdirpath, "projection_minys.png")
    #util.saveimage(panorama_copy, objdirpath, "projection_maxys.png")
    
   

    
    
    
    
    
    
    
    
    
    