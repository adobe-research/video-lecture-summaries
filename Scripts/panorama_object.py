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
from video import Video

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
        
        
def cluster_objects_xypos(panorama, list_of_objs, outfile, video):
 
    data = []
    objs_in_panorama = []
    tls = []
    w = video.width
    h = video.height
    
    for visobj in list_of_objs:
        tl = (visobj.tlx, visobj.tly)
        if tl is None:
            continue
        else:
            data.append(((tl[0]+visobj.width/2)/w, 3*(tl[1] + visobj.height/2)/h))
            objs_in_panorama.append(visobj)
            tls.append(tl)
     
    ydata = np.array(data)
    labels, cluster_center = meanshift.cluster(ydata)
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)
    print("number of estimated clusters : %d" % n_clusters_)
     
    panorama_copy = np.ones(panorama.shape)*255
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
    
def cluster_objects_xyt(panorama, list_of_objs, outfile, video):
 
    data = []
    objs_in_panorama = []
    tls = []
    
    w = video.width
    h = video.height
    nframes = video.numframes
    
    for visobj in list_of_objs:
        tl = (visobj.tlx, visobj.tly)
        if tl is None:
            continue
        else:
            data.append((2*(tl[0]+visobj.width/2)/w, 3*(tl[1] + visobj.height/2)/h, (visobj.start_fid + visobj.end_fid)/nframes))
            objs_in_panorama.append(visobj)
            tls.append(tl)
     
    ydata = np.array(data)
    labels, cluster_center = meanshift.cluster(ydata)
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)
    print("number of estimated clusters : %d" % n_clusters_)
     
    panorama_copy = np.ones(panorama.shape)*255
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

        

def cluster_objects_ypos(panorama, list_of_objs, outfile):
 
    data = []
    objs_in_panorama = []
    tls = []
    for visobj in list_of_objs:
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
     
    panorama_copy = np.ones(panorama.shape)*255
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
        
        
def cluster_pixels_ypos():
    panoramapath = sys.argv[1]
    objdirpath = sys.argv[2]
    outfile = sys.argv[3]
    panorama = cv2.imread(panoramapath)
    
    mask = pf.fgmask(panorama)
    obj_pxl_coords = np.where(mask != 0)
    data = zip(obj_pxl_coords[1], obj_pxl_coords[0])

    ydata = zip(np.zeros(len(obj_pxl_coords[0])), obj_pxl_coords[0])    
    labels, cluster_center = meanshift.cluster(np.array(ydata))
    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)
    meanshift.write(labels, outfile + "_labels.txt")
    
    panorama_copy = np.ones(panorama.shape)*255
    ndata = np.array(data)
    colors = [(0,255,0),(255,0,0),(0,0,255),(255,0,255),(100,255,255),(255,255,0),(255, 100, 100), (255, 200, 200), (0,100,0), (100,0,0), (51, 255, 255)]
    for k in range(0, n_clusters):
        my_members = labels == k
        color = colors[k%len(colors)]
        for xy in my_members:
            print xy
            panorama_copy[ndata[xy, 1], ndata[xy, 0]] = color        
    cv2.imwrite(outfile+".png", panorama_copy)
    
    
#     plt = meanshift.plot(np.array(data), labels, cluster_center)
#     plt.savefig(outfile)
#     plt.close()

def objs():
    panoramapath = sys.argv[1]
    objdirpath = sys.argv[2]
    outfile = sys.argv[3]
    panorama = cv2.imread(panoramapath)
    objs_in_panorama = VisualObject.objs_from_file(None, objdirpath)
    print 'num objects', len(objs_in_panorama)
    panorama_copy = np.ones(panorama.shape)*255
    colors = [(0,255,0),(255,0,0),(0,0,255),(255,0,255),(100,255,255),(255,255,0),(255, 100, 100), (255, 200, 200), (0,100,0), (100,0,0), (51, 255, 255)]
    for i in range(0, len(objs_in_panorama)):
        obj = objs_in_panorama[i]
        if (obj.img is None):
            continue
        col = colors[i%len(colors)]
        mask = pf.fgmask(obj.img, 50, 255, True)
        fitmask = pf.fit_mask_to_img(panorama_copy, mask, obj.tlx, obj.tly)
        idx = (fitmask != 0 )
#         temp = panorama_copy.copy()
        panorama_copy[idx] = col
#         panorama_copy = cv2.min(temp, panorama_copy)
    cv2.imwrite(outfile, panorama_copy)
    util.showimages([panorama_copy], outfile)

def draw_clusters(panorama, list_of_objs, labels):
    panorama_copy = np.ones(panorama.shape)*255
    colors = [(0,255,0),(255,0,0),(0,0,255),(255,0,255),(100,255,255),(255,255,0),(255, 100, 100), (255, 200, 200), (0,100,0), (100,0,0), (51, 255, 255)] 
    for i in range(0, len(list_of_objs)):
        obj = list_of_objs[i]
        k = labels[i]
        col = colors[k%len(colors)]
        tl = (obj.tlx, obj.tly)
        mask = pf.fgmask(obj.img)
        fitmask = pf.fit_mask_to_img(panorama_copy, mask, tl[0], tl[1])
        idx = fitmask != 0
        panorama_copy[idx] = col
    return panorama_copy

    
if __name__ == "__main__":
    objs()
#     panoramapath = sys.argv[1]
#     objdirpath = sys.argv[2]
#     outfile = sys.argv[3]
#     videopath = sys.argv[4]
#     panorama = cv2.imread(panoramapath)
#     objs_in_panorama = VisualObject.objs_from_file(None, objdirpath)
#     video = Video(videopath)
#     cluster_objects_xyt(panorama, objs_in_panorama, outfile, video)
  

       
    