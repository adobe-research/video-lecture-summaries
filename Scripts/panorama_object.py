'''
Created on Oct 14, 2014

@author: hijungshin
'''
import processframe as pf
import util
import sys
import cv2
from visualobjects import VisualObject
import meanshift
import numpy as np
from itertools import cycle

def find_objects(panorama, list_of_objects):
    
    for obj in list_of_objects:
        tl = (obj.tlx, obj.tly)
        if tl is None:
            util.showimages([obj.img])
            continue
        panorama_copy = panorama.copy()
        cv2.rectangle(panorama_copy, (tl[0], tl[1]), (tl[0]+obj.width, tl[1]+obj.height), (0, 255, 0), 1)
        util.showimages([obj.img, panorama_copy])
    return panorama_copy
        
def cluster_objects_ypos(panorama, list_of_objs, outfile):
 
    data = []
    objs_in_panorama = []
    tls = []
    for visobj in visobjs:
        tl = (visobj.tlx, visobj.tly)
        if tl is None:
            continue
        else:
            data.append((0, tl[1] + visobj.height/2))
            objs_in_panorama.append(visobj)
            tls.append(tl)
     
    ydata = np.array(data)
    labels, cluster_center = meanshift.cluster(ydata)
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)
    print("number of estimated clusters : %d" % n_clusters_)
     
    panorama_copy = panorama.copy()
    colors = [(0,255,0),(255,0,0),(0,0,255),(255,0,255),(100,255,255),(255,255,0),(255, 100, 100)]
     
    for i in range(0, len(objs_in_panorama)):
        obj = objs_in_panorama[i]
        k = labels[i]
        col = colors[k%len(colors)]
        tl = tls[i]
#         cv2.rectangle(panorama_copy, (tl[0], tl[1]), (tl[0]+obj.width, tl[1]+obj.height), col, 3)
        mask = pf.fgmask(obj.img)
        fitmask = pf.fit_mask_to_img(panorama_copy, mask, tl[0], tl[1])
        idx = fitmask != 0
        panorama_copy[idx] = col
#         panorama_copy = pf.highlight(panorama_copy, fitmask, (col[0], col[1], col[2], 100))
#         util.showimages([panorama_copy, fitmask, obj.img])
    cv2.imwrite(outfile, panorama_copy)
        
if __name__ == "__main__":
    panoramapath = sys.argv[1]
    objdirpath = sys.argv[2]
    outfile = sys.argv[3]
    panorama = cv2.imread(panoramapath)
#     visobjs = VisualObject.objs_from_file(None, objdirpath)
    
    mask = pf.fgmask(panorama)
    obj_pxl_coords = np.where(mask != 0)
    data = zip(obj_pxl_coords[1], obj_pxl_coords[0])
    ydata = zip(np.zeros(len(obj_pxl_coords[0])), obj_pxl_coords[0])
    
    labels, cluster_center = meanshift.cluster(np.array(ydata))
    plt = meanshift.plot(np.array(data), labels, cluster_center)
    plt.savefig(outfile)
    plt.close()
    
     

       
    