'''
Created on Nov 21, 2014

@author: hijungshin
'''
from visualobjects import VisualObject
import sys
import processframe as pf
import util
import cv2
import numpy as np

if __name__ == "__main__":
    panoramapath = sys.argv[1]
    objdirpath = sys.argv[2]
    panorama = cv2.imread(panoramapath)
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    curcol = (255,0,0)
    prevcol = (0, 0, 255)
    
    for i in range(0, len(list_of_objs)):
        curobj = list_of_objs[i]
        panorama_copy = np.ones(panorama.shape)*255
        if (curobj.img is None):
            continue
        for j in range(i+1, len(list_of_objs)):
            prevobj = list_of_objs[j]
            overlap = VisualObject.overlap(curobj, prevobj)
            if (overlap > 0.8):
                curmask = pf.fgmask(curobj.img, 50, 255, True)
                fitmask = pf.fit_mask_to_img(panorama_copy, curmask, curobj.tlx, curobj.tly)
                idx = (fitmask != 0 )
#         temp = panorama_copy.copy()
                panorama_copy[idx] = curcol
                
                prevmask =  pf.fgmask(prevobj.img, 50, 255, True)
                fitmask = pf.fit_mask_to_img(panorama_copy, prevmask, prevobj.tlx, prevobj.tly)
                idx = (fitmask != 0 )
                panorama_copy[idx] = prevcol
                util.showimages([panorama_copy], "overlap")