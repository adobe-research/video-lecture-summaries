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
from numpy import obj2sctype


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
        self.video = None
        
    def write_to_html(self, html):
        html.breakline()
        html.image(self.imgpath)
        html.breakline()

                   
    @classmethod
    def fromtext(cls, text, start_fid, end_fid):        
        (textsize, baseline) = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
        img = np.ones((textsize[1]+baseline, textsize[0], 3), dtype=np.uint8) * 255
        cv2.putText(img, text, (0, textsize[1]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0))    
        return cls(img, None, start_fid, end_fid, 0, 0, textsize[0], textsize[1]+baseline, True, text)                        
        
    def getheight(self):
        h, w = self.img.shape[:2]
        return h
    
    def getwidth(self):
        h, w = self.img.shape[:2]
        return w
    
    def area(self):
        return (self.brx - self.tlx + 1.0) * (self.bry - self.tly + 1.0)
    
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
    
    def numfgpixel(self, bgthres = 225):
        grayobj = util.grayimage(self.img)
        numcount = np.count_nonzero(grayobj < bgthres)
        return numcount
    
    def fgarray(self, bgthres = 225):
        grayobj = util.grayimage(self.img)
        fg = (grayobj < bgthres)
        return fg
    
    @staticmethod
    def fg_y_projection_function(obj):
        fg = obj.fgarray()
        h, w = fg.shape[0:2]
        y_count = np.empty(h, dtype=np.uint8) 
        for i in range(0, h):
            y_count[i] = np.count_nonzero(fg[i,:])
        return y_count    
    
    @staticmethod
    def fg_x_projection_function(obj):
        fg = obj.fgarray()
        h, w = fg.shape[0:2]
        x_count = np.empty(w, dtype=np.uint8) 
        for i in range(0, w):
            x_count[i] = np.count_nonzero(fg[:,i])
        return x_count   
    
    @staticmethod
    def fg_y_projection_function_list(list_of_objs):
        minx, miny, maxx, maxy = VisualObject.bbox(list_of_objs)
        y_sum_count = np.zeros(maxy - miny + 1, dtype=np.uint8)
        for obj in list_of_objs:
            tlx, tly, brx, bry = VisualObject.bbox([obj])
            y_count = VisualObject.fg_y_projection_function(obj)
            for i in range(0, len(y_count)):
                y_sum_count[i + (tly - miny)] += y_count[i]
        plt.ylim((0, max(y_sum_count)+1))
        plt.plot(y_sum_count)
        plt.title("y projection function")
        plt.show()
        return y_sum_count
    
    @staticmethod
    def vertical_compact(list_of_objs):
        sum_height = 0.0
        minx, miny, maxx, maxy = VisualObject.bbox(list_of_objs)
        for obj in list_of_objs:
            sum_height += (obj.getheight())
        vertical_compact = sum_height/(maxy - miny + 1.0)
        return vertical_compact
    
    
    @staticmethod
    def fg_x_projection_function_list(list_of_objs):
        minx, miny, maxx, maxy = VisualObject.bbox(list_of_objs)
        x_sum_count = np.zeros(maxx - minx + 1, dtype=np.uint8)
        for obj in list_of_objs:
            tlx, tly, brx, bry = VisualObject.bbox([obj])
            x_count = VisualObject.fg_x_projection_function(obj)
            for i in range(0, len(x_count)):
                x_sum_count[i + (tlx - minx)] += x_count[i]
        plt.ylim((0, max(x_sum_count)+1))
        plt.plot(x_sum_count)
        plt.title("x projection function")
        plt.show()
        return x_sum_count
        
    @staticmethod
    def compactness(list_of_objs):
        if len(list_of_objs) == 0:
            return 0
        tlx, tly, brx, bry =  VisualObject.bbox(list_of_objs)
        bbox_area = (brx - tlx + 1.0) * (bry - tly + 1.0)
        sum_area  = 0.0
        for obj in list_of_objs:
            sum_area += obj.area()
#         print 'compactness', sum_area/bbox_area
        return sum_area/bbox_area
    
    
    @classmethod
    def group(cls, list_of_imgobjs, objdir="temp", imgname=None, debug=False):    
        if len(list_of_imgobjs) <= 0:
            return None
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
        
        if (imgname is None):
            groupimgname = "obj_%06i_%06i_group.png" %(min_start_fid, max_end_fid)
        else:
            groupimgname = imgname

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
#         print 'objfile', objfile
        obj_list = []
        obj_info = util.list_of_vecs_from_txt(objfile)
        obj_info.pop(0)
        obj_endts = [obj[1] for obj in obj_info]
        obj_endts = util.strings2ints(obj_endts)
#         print len(obj_info)
        for i in range(0, len(obj_info)):
            info = obj_info[i]
            imgpath = os.path.basename(str(info[6]))
#             print objdir + "/" + imgpath
            objimg = cv2.imread(objdir + "/" + imgpath)
#             print objdir + "/" + imgpath
            objh, objw = objimg.shape[:2]
            startt = int(info[0])
            endt = int(info[1])
            if (objh <= 1 and objw <= 1):
#                 print 'ignoring', imgpath
                continue;
            obj = VisualObject(objimg, imgpath, int(info[0]), int(info[1]), int(info[2]), int(info[3]), int(info[4]), int(info[5]))
            obj.video = video
            obj_list.append(obj)
        return obj_list      
    
    @staticmethod
    def obj_stc_distance(obj, stc, video= None):
        if (video is None):
            video = obj.video
        stc_start = video.ms2fid(stc[0].startt)
        stc_end = video.ms2fid(stc[-1].endt)
        if (obj.end_fid <= stc_start):
            dist = 1.0 * (stc_start - obj.end_fid)
        elif (obj.start_fid >= stc_end):
            dist = 1.0 * (obj.start_fid - stc_end)
        else:
            dist = max(obj.start_fid, stc_start) - min(obj.end_fid, stc_end) 
        return dist
        
    
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
        # overlap
        return 0
    
    @staticmethod
    def signed_ygap_distance(obj_i, obj_j):
        # obj i above obj j
        if (obj_i.bry <= obj_j.tly):
            return (obj_j.tly - obj_i.bry)
        # obj i below obj j
        if (obj_i.tly >= obj_j.bry):
            return (obj_i.tly - obj_j.bry) 
        else:
            return -(min(obj_i.bry, obj_j.bry) - max(obj_i.tly, obj_j.tly))
    
    @staticmethod
    def xgap_distance(obj_i, obj_j):
        if obj_i.brx < obj_j.tlx: # obj_i left of obj_j
            return obj_j.tlx - obj_i.brx
        elif obj_i.tlx >= obj_j.brx: #obj1 right of obj1
            return obj_i.tlx - obj_j.brx
        #overlap
        return 0 
    
    @staticmethod
    def signed_xgap_distance(obj_i, obj_j):
        if obj_i.brx <= obj_j.tlx: # obj_i left of obj_j
            return obj_j.tlx - obj_i.brx
        elif obj_i.tlx >= obj_j.brx: #obj1 right of obj1
            return obj_i.tlx - obj_j.brx
        else:
            return -(min(obj_i.brx, obj_j.brx) - max(obj_i.tlx, obj_j.tlx))

    @staticmethod
    def xgap_distance_list(list_of_objs1, list_of_objs2):
        tlx1, tly1, brx1, bry1 = VisualObject.bbox(list_of_objs1)
        tlx2, tly2, brx2, bry2 = VisualObject.bbox(list_of_objs2)
        if (brx1 < tlx2):
            return (False, tlx2 - brx1)
        if (tlx1 > brx2):
            return (False, tlx1 - brx2)
        return (True, -(brx2 - tlx1)) # overlap
    
        
    @staticmethod
    def ygap_distance_list(list_of_objs1, list_of_objs2):
        """measures how much center-aligned"""
        tlx, tly, brx, bry = VisualObject.bbox(list_of_objs1)
        tlx2, tly2, brx2, bry2 = VisualObject.bbox(list_of_objs2)
        line_ctry = tly + (bry + 1 - tly) / 2.0
        obj_ctry = tly2 + (bry2 + 1 - tly2) / 2.0
        line_h = (bry + 1 - tly)
        obj_h = (bry2 + 1 - tly2)
        y_dist = abs(obj_ctry - line_ctry) - (obj_h/2.0 + line_h/2.0)
        return y_dist
        
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
    def overlap_list(list_of_objs1, list_of_objs2):
        tlx1, tly1, brx1, bry1 = VisualObject.bbox(list_of_objs1)
        tlx2, tly2, brx2, bry2 = VisualObject.bbox(list_of_objs2)
        area1 = (brx1 + 1 - tlx1) * (bry1 + 1 - tly1)
        area2 = (brx2 + 1 - tlx2) * (bry2 + 1 - tly2)
        areai = max(0, min(brx1 + 1, brx2 + 1) - max(tlx1, tlx2)) * max(0, min(bry1 + 1, bry2 + 1) - max(tly1, tly2))
        return 1.0 * areai / min(area1, area2)
        
    
    @staticmethod
    def side_by_side(obj1, obj2):
        #center of object must lie in line horizontally
        h1 = obj1.getheight()
        h2 = obj2.getheight()
        if (h1 > h2):
            taller = obj1
            shorter = obj2
        else:
            taller = obj2
            shorter = obj1
        
        shorter_cy = (shorter.tly + shorter.bry)/2.0
        if (taller.tly <= shorter_cy and shorter_cy <= taller.bry):
            if obj1.brx < obj2.tlx: # obj1 left of obj2 :
                gap = VisualObject.xgap_distance(obj1, obj2)
            elif obj1.tlx >= obj2.brx: #obj1 right of obj1
                gap = VisualObject.xgap_distance(obj2, obj1)
            else:
                gap = 0
            if (gap < 100):
                return True
        return False
    
    @staticmethod
    def above_and_below(obj1, obj2):
        #center of object must be in line vertically
        w1 = obj1.getwidth()
        w2 = obj2.getwidth()
        if (w1 > w2):
            wider = obj1
            narrower = obj2
        else:
            wider = obj2
            narrower = obj1
            
        narrower_cx = (narrower.tlx + narrower.brx)/2.0
        if (wider.tlx <= narrower_cx and narrower_cx <= wider.brx): 
            gap = VisualObject.ygap_distance(obj1, obj2)
            if (gap < 10):
                return True
        return False
    
    @staticmethod
    def inline_score(obj, line, next_objs):
        if VisualObject.overlap(obj, line) > 0.5:
#             print 'overlap'
#             util.showimages([obj.img, line.img], "inline score")
            return -1.0 * float("inf")
        if VisualObject.side_by_side(obj, line):
#             print 'side by side', 0.2 * VisualObject.xgap_distance(obj, line)
#             util.showimages([obj.img, line.img], "inline score")
#             return 0.2 * VisualObject.xgap_distance(obj, line)
            return 0.2
        fill = VisualObject.inline_to_be_filled(line, obj, next_objs)
        if (fill[0]):
#             print 'inline_to_be_fillled', 0.2 * VisualObject.xgap_distance(obj, fill[1])
#             util.showimages([obj.img, line.img], "inline score")
            return 0.4
#             return 0.1 * VisualObject.xgap_distance(obj, fill[1])
        if VisualObject.above_and_below(obj, line):
#             print 'above and below', VisualObject.ygap_distance(obj, line)
#             util.showimages([obj.img, line.img], "inline score")
#             return 0.5*VisualObject.ygap_distance(obj, line)
            return 0.6
        return float("inf")
    
    @staticmethod
    def inline_to_be_filled(curobj, prevobj, list_of_objs):
        for obj in list_of_objs:
            if VisualObject.side_by_side(prevobj, obj):
                if VisualObject.side_by_side(obj, curobj):
                    return True, obj
        return False, None
        
            
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
    def y_projection_function(list_of_objs):
        tlx, miny, brx, maxy = VisualObject.bbox(list_of_objs)
        y_count = np.empty(maxy + 1- miny, dtype=np.uint8)
        for i in range(0, maxy+1-miny):
            count = 0
            for obj in list_of_objs:
                if obj.tly <= i+miny and i+miny <= obj.bry:
                    count += 1
            y_count[i] = count
#         plt.ylim((0, max(y_count)+1))
#         plt.plot(y_count)
#         plt.title("y projection function")
#         plt.show()
        return y_count

    @staticmethod
    def x_projection_function(list_of_objs):
        minx, tly, maxx, bry = VisualObject.bbox(list_of_objs)
        x_count = np.empty(maxx + 1 - minx, dtype= np.uint8)
        for i in range(0, maxx + 1 - minx):
            count = 0
            for obj in list_of_objs:
                if obj.tlx <= i + minx and i + minx <= obj.brx:
                    count += 1
            x_count[i] = count
#         plt.ylim((0, max(x_count)+1))
#         plt.title("x projection function")
#         plt.plot(x_count)
#         plt.show()
        return x_count
    
    @staticmethod
    def y_cut_at_gap(visobj, outdir):
        """assumption: white background"""
        img2 = visobj.img
        mask = pf.fgmask(img2, 225, 255, False)
        ysum = np.sum(mask, 1)
        ysum0 = np.where(ysum == 0)[0]
        
        objimgname = visobj.imgpath.split('.')[0]
        cut_objs = []
        count = 0
        tlx = visobj.tlx
        tly = visobj.tly
        
        while (len(ysum0) > 0):
            minysum0 = min(ysum0)
            images = pf.ycut(img2, minysum0)
            if minysum0 > 0:
                img1 = images[0]
                mask1 = pf.fgmask(img1, 225, 255, False)
                tlx1, tly1, brx1, bry1 = pf.fgbbox(mask1)
                tlx1 = tlx + tlx1
                tly1 = tly + tly1
                brx1 = tlx + brx1
                bry1 = tly + bry1
                img1, temp = pf.croptofg(img1, mask1)
                objimgname1 = objimgname +"_%02i"%(count)+".png"
                util.saveimage(img1, outdir, objimgname1)
                obj1 = VisualObject(img1, outdir + "/" + objimgname1, visobj.start_fid, visobj.end_fid, tlx1, tly1, brx1, bry1)
                cut_objs.append(obj1)
                count += 1
            
            img2 = images[1]
            if (img2.shape[1] == 0 ):
                return cut_objs
            mask2 = pf.fgmask(img2, 200, 255, False)
            tlx2, tly2, brx2, bry2 = pf.fgbbox(mask2)
            if (tlx2 < 0 or tlx2 == brx2 or tly2 == bry2):
                """if img2 is empty"""
                return cut_objs
            
            img2, mask2 = pf.croptofg(img2, mask2)
            tlx = tlx + tlx2
            tly = tly + minysum0 + tly2 + 1
            
            ysum = np.sum(mask2, 1)
            ysum0 = np.where(ysum == 0)[0]
                            
        objimgname2 = objimgname +"_%02i"%(count)+".png"
        util.saveimage(img2, outdir, objimgname2)
        h2, w2 = img2.shape[:2]
        obj2 = VisualObject(img2, outdir + "/" + objimgname2, visobj.start_fid, visobj.end_fid, tlx, tly, tlx + w2 - 1, tly + h2 - 1)
        cut_objs.append(obj2)
        return cut_objs
    
    @staticmethod
    def x_cut_at_gap(visobj, outdir):
        """assumption: white background"""
        img2 = visobj.img
        mask = pf.fgmask(img2, 225, 255, False)
        xsum = np.sum(mask, 0)
        xsum0 = np.where(xsum == 0)[0]
        
        objimgname = visobj.imgpath.split('.')[0]
        cut_objs = []
        count = 0
        tlx = visobj.tlx
        tly = visobj.tly
        
        while (len(xsum0) > 0):
#             util.showimages([img2], "img2")
            minxsum0 = min(xsum0)
            images = pf.xcut(img2, minxsum0)
            if minxsum0 > 0:
                img1 = images[0]
                mask1 = pf.fgmask(img1, 225, 255, False)
                tlx1, tly1, brx1, bry1 = pf.fgbbox(mask1)
                tlx1 = tlx + tlx1
                tly1 = tly + tly1
                brx1 = tlx + brx1
                bry1 = tly + bry1
                img1, temp = pf.croptofg(img1, mask1)
                objimgname1 = objimgname +"_%02i"%(count)+".png"
                util.saveimage(img1, outdir, objimgname1)
                obj1 = VisualObject(img1, outdir + "/" + objimgname1, visobj.start_fid, visobj.end_fid, tlx1, tly1, brx1, bry1)
                cut_objs.append(obj1)
                count += 1
            
            img2 = images[1]
            if (img2.shape[1] == 0 ):
                return cut_objs
            mask2 = pf.fgmask(img2, 225, 255, False)
            tlx2, tly2, brx2, bry2 = pf.fgbbox(mask2)
            if (tlx2 < 0 or tlx2 == brx2 or tly2 == bry2):
                return cut_objs
            
            img2, mask2 = pf.croptofg(img2, mask2)
            tlx = tlx + minxsum0 + tlx2 + 1
            tly = tly + tly2
            
            xsum = np.sum(mask2, 0)
            xsum0 = np.where(xsum == 0)[0]
            
            
#             tlx2 = tlx + minxsum0
#             tly2 = tly
#             img2 = pf.croptofg(img2, mask2)
#             if (img2.shape[1] == 0):
#                 return cut_objs
#             
#             xsum = np.sum(mask, 0)
#             xfg = np.where(xsum!=0)[0]
#             if (len(xfg) == 0):
#                 print "Visobj.x_cut_at_gap: Should not enter here"
#                 return cut_objs
#             else:
#                 minxfg = min(xfg)
#                 images = pf.xcut(img2, minxfg-1)
#                 img2 = images[1]
#                 if (img2.shape[1] == 0):
#                     return cut_objs
#                 mask = pf.fgmask(img2, 225, 255, False)
#                 xsum = np.sum(mask, 0)
#                 xsum0 = np.where(xsum == 0)[0]
#                 tlx = tlx + w1 + minxfg
                
        objimgname2 = objimgname +"_%02i"%(count)+".png"
        util.saveimage(img2, outdir, objimgname2)
        h2, w2 = img2.shape[:2]
        obj2 = VisualObject(img2, outdir + "/" + objimgname2, visobj.start_fid, visobj.end_fid, tlx, tly, tlx + w2 - 1, tly + h2 - 1)
        cut_objs.append(obj2)
#         util.showimages([obj.img for obj in cut_objs], "cut images")
        return cut_objs
        
    
    @staticmethod
    def fgpixel_count(list_of_objs):
        count = 0
        for obj in list_of_objs:
            count += obj.numfgpixel()
        return count
    
    @staticmethod
    def ctr_distance(obj1, obj2):
        x1 = (obj1.tlx + obj1.brx) / 2.0
        y1 = (obj1.tly + obj1.bry) / 2.0
        x2 = (obj2.tlx + obj2.brx) / 2.0
        y2 = (obj2.tly + obj2.bry) / 2.0
        dist = math.sqrt((x1-x2)*(x1-x2) + (y1-y2) * (y1-y2))
        return dist
    
    @staticmethod
    def break_penalty(obj1, obj2):
        xdist = VisualObject.xgap_distance(obj1, obj2)
        ydist = VisualObject.ygap_distance(obj1, obj2)
        tdist = obj1.start_fid - obj2.end_fid
        if tdist < 0:
            tdist = obj2.start_fid - obj1.end_fid
#         print 'xdist', xdist, 'ydist', ydist, 'tdist', tdist
        return (xdist, ydist, tdist)
    
    @staticmethod
    def find_closest_obj(curobj, list_of_objs):
        closest_obj = None
        min_dist = 200
        for obj in list_of_objs:
            if obj == curobj:
                continue
            (xdist, ydist, tdist) = VisualObject.break_penalty(curobj, obj)
            dist = xdist + 2.0*ydist
            if (dist == 0): # overlap:
                dist = -1.0 * VisualObject.overlap(curobj, obj)
            if (dist < min_dist):
                min_dist = dist
                closest_obj = obj
        xdist, ydist, tdist = VisualObject.break_penalty(curobj, closest_obj)
        print 'xidst', xdist, 'ydist', ydist, 'tdist', tdist
        return closest_obj
            
        
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
    def inline(line_objs, curobj):
        ydist = VisualObject.ygap_distance_list(line_objs, [curobj])
        (overlap, xdist) = VisualObject.xgap_distance_list(line_objs, [curobj])
        if (ydist <= 10 and overlap == True):
            return 1.5
        elif (ydist <= 10 and xdist <= 100):
            return 1.0
        elif (ydist >= 50):
            return -1.0
        elif (ydist >= 0 and not overlap and xdist >= 200):
            return -1.0
        else: 
            return 0 #maybe
        
    
            
if __name__ == "__main__":
    objdirpath = sys.argv[1]
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    panoramapath = sys.argv[2]
    panorama = cv2.imread(panoramapath)
    panorama_copy = panorama.copy()
    prevobj = None
    for obj in list_of_objs:
        if prevobj is not None:
            print 'ydist = ', VisualObject.ygap_distance(prevobj, obj)
        cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0,0,255), 1)
        util.showimages([panorama_copy])
    

        prevobj = obj

    
    
    
    
    
    
    
    
    
    