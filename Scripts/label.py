'''
Created on Mar 22, 2015

@author: hijungshin
'''

import cv2
import numpy as np
import util

def label_objs(list_of_objs, list_of_labels):    
    list_of_imgobjs = list_of_objs + list_of_labels
    img = util.groupimages(list_of_imgobjs)
#     util.showimages([img])
    return img

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


class Label:
    def __init__(self, img, pos):
        self.img = img
        self.pos = pos
        h, w = img.shape[0:2]
        self.tlx = pos[0] - w/2
        self.tly = pos[1] - h/2
        self.brx = self.tlx + w
        self.bry = self.tly + h       
        
    def changepos(self, pos):
        self.pos = pos
        h, w = self.img.shape[0:2]
        self.tlx = pos[0] - w/2
        self.tly = pos[1] - h/2
        self.brx = self.tlx + w
        self.bry = self.tly + h    