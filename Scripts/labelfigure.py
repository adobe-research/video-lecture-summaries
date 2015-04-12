'''
Created on Mar 22, 2015

@author: hijungshin
'''

import cv2
import numpy as np
import util
from label import Label
import math
import random
import sys
import lecturevisual



def getlabelimg(text):
    """put text in image and return image"""
    fontface = cv2.FONT_HERSHEY_COMPLEX
    fontscale = 0.7
    thickness = 1
    fontcolor=(0,0,0)
    size, baseline = cv2.getTextSize(text, fontface, fontscale, thickness)
    img = np.ones((size[1]+2*baseline, size[0], 3), dtype=np.uint8)*255
    cv2.putText(img, text, (0, 2*baseline + size[1]/2), fontface, fontscale, fontcolor, thickness=thickness)
#     util.showimages([img], text)
    return img
    
def getlabels(start_i, nlabels):
    list_of_labels = []
    for i in range(0, nlabels):
        ltxt = '(' + chr(ord('a') + start_i+i) + ')'
        img = getlabelimg(ltxt)
        label = Label(img, (0,0))
        list_of_labels.append(label)
    return list_of_labels


def score_overlap(list_of_objs, list_of_labels):
    overlap_area = 0.0
    for obj in list_of_objs:
        obj_box = (obj.tlx, obj.tly, obj.brx, obj.bry)
        for label in list_of_labels:
            label_box = (label.tlx, label.tly, label.brx, label.bry)
            (tlx, tly, brx, bry) = util.bbox_overlap(obj_box, label_box)
            if (tlx < brx and tly < bry): 
                overlap_area += ((brx - tlx)*(bry - tly))
            
    nlabels = len(list_of_labels)
    for i in range(0, nlabels):
        l1 = list_of_labels[i]
        l1box = (l1.tlx, l1.tly, l1.brx, l1.bry)
        for j in range(0, nlabels):
            if i == j:
                continue
            l2 = list_of_labels[j]
            l2box = (l2.tlx, l2.tly, l2.brx, l2.bry)
            (tlx, tly, brx, bry) = util.bbox_overlap(l1box, l2box)
            if (tlx < brx and tly < bry):
                overlap_area += ((brx - tlx)*(bry - tly))
            
    return overlap_area

def score_dist_match(list_of_objs, list_of_labels):
    nobjs = len(list_of_objs)
    ss_dist = 0.0
    for i in range(0, nobjs):
        obj = list_of_objs[i]
        label = list_of_labels[i]
        obj_ctr = ((obj.tlx + obj.brx)/2.0, (obj.tly + obj.bry)/2.0)
        label_ctr = ((label.tlx + label.brx)/2.0, (label.tly + label.bry)/2.0)
        dist = math.pow((obj_ctr[0] - label_ctr[0]),2.0) + math.pow((obj_ctr[1]- label_ctr[1]),2.0)
        ss_dist += math.sqrt(dist)
    return ss_dist

def score_dist_separate(list_of_objs, list_of_labels):
    nobjs = len(list_of_objs)
    ss_dist = 0.0
    for i in range(0, nobjs):
        obj = list_of_objs[i]
        for j in range(0, nobjs):
            if i == j:
                continue
            label = list_of_labels[j]
            obj_ctr = ((obj.tlx + obj.brx)/2.0, (obj.tly + obj.bry)/2.0)
            label_ctr = ((label.tlx + label.brx)/2.0, (label.tly + label.bry)/2.0)
            dist = math.pow((obj_ctr[0] - label_ctr[0]),2.0) + math.pow((obj_ctr[1]- label_ctr[1]),2.0)
            ss_dist += math.sqrt(dist)
    return ss_dist

def score_layout(list_of_objs, list_of_labels):
    s1 = score_overlap(list_of_objs, list_of_labels)
    s2 = score_dist_match(list_of_objs, list_of_labels)
    s3 = score_dist_separate(list_of_objs, list_of_labels)
    score = s1 + s2 - s3
    return score

def randpos(obj, label, margin=5):
    objh = obj.height
    objw = obj.width
    labelh = label.bry - label.tly + 1
    labelw = label.brx - label.tlx + 1
    
    left_right_area = 2*margin + objh + labelh
    top_bottom_area = objw + labelw
    n = random.randint(1, 2*(left_right_area + top_bottom_area))
    
    if 1 <= n <= left_right_area:
        """left"""
        posx = obj.tlx - labelw/2 - random.randint(0, margin)
        posy = obj.tly - margin - labelh/2 + random.randint(0, objh + 2*margin + labelh)
    elif left_right_area+1 <= n <= 2* left_right_area:
        """right"""
        posx = obj.brx + labelw/2 + random.randint(0, margin)
        posy = obj.tly - margin - labelh/2 + random.randint(0, objh + 2*margin + labelh)
    elif 2*left_right_area+1 <= n <= 2*left_right_area + top_bottom_area:
        """top"""
        posx = obj.tlx - labelw/2 + random.randint(0,objw + labelw)
        posy = obj.bry + labelh/2+random.randint(0,margin)
    else:
        """bottom"""
        posx = obj.tlx - labelw/2 + random.randint(0,objw + labelw)
        posy = obj.tly - labelh/2 - random.randint(0, margin)
    
    return (posx, posy)

def init_layout(list_of_objs, list_of_labels):
    nlabels = len(list_of_objs)
    for i in range(0, nlabels):
        label = list_of_labels[i]
        obj = list_of_objs[i] 
        label.changepos(randpos(obj, label))
    return
    
def perturb_layout(list_of_objs, list_of_labels):
    """choose a label"""
    nlabels = len(list_of_labels)
    n = random.randint(0, nlabels-1)
    label = list_of_labels[n]
    obj = list_of_objs[n]
    newpos = randpos(obj, label)
    return (n, newpos)


def label_objs(list_of_objs, list_of_labels):    
    list_of_imgobjs = list_of_objs + list_of_labels
    img = util.groupimages(list_of_imgobjs)
    return img

def sim_anneal(list_of_objs, list_of_labels, maxiter=250):
    init_layout(list_of_objs, list_of_labels)
    img = label_objs(list_of_objs, list_of_labels)
#     util.showimages([img])
    
    score = score_layout(list_of_objs, list_of_labels)
    iter = 0
    T = 1000.0
    while(iter < maxiter):
        iter+=1
        n, newpos = perturb_layout(list_of_objs, list_of_labels)
        oldpos = list_of_labels[n].pos
        list_of_labels[n].changepos(newpos)
        new_score = score_layout(list_of_objs, list_of_labels)
        ds = 1.0*(new_score - score)
        prob = 1.0-math.exp(-ds/T)
        r = random.random()
        if (new_score > score and r < prob):
            list_of_labels[n].changepos(oldpos)
        else:
            score = new_score
        img = label_objs(list_of_objs, list_of_labels)
#         util.showimages([img])
        T *= 0.98
        

if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    figdir = objdir + "/subline_test"
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
     
    line = list_of_linegroups[0]
    list_of_objs = []
    for subline in line.list_of_sublines:
        if len(subline.list_of_stcstrokes)==0:
            list_of_objs.append(subline.obj)
        else:
            list_of_objs += [stcstroke.obj for stcstroke in subline.list_of_stcstrokes]
            
    nlabels = len(list_of_objs)
    print 'n labels', nlabels
    list_of_labels = getlabels(0, nlabels)
    sim_anneal(list_of_objs, list_of_labels)

    

        
          
