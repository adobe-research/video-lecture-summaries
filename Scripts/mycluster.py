'''
Created on Oct 14, 2014

@author: hijungshin
'''

import meanshift
import numpy as np
from visualobjects import VisualObject
import sys
import util
import panorama_object
import cv2

def meanshift_visobjs(list_of_visobjs, ctlx, cbrx, ctly, cbry, cstart, cend, w, h, nframes, bandwidth=None):
    data = []
    for visobj in list_of_visobjs:
        x = ctlx * visobj.tlx + cbrx * visobj.brx
        y = ctly * visobj.tly + cbry * visobj.bry
        fid = cstart*visobj.start_fid + cend*visobj.end_fid
        
        data.append((x*w, y*h, fid*nframes))
        
    labels, cluster_centers = meanshift.cluster(np.array(data), bandwidth=bandwidth)
        
    return labels, cluster_centers
        
def cluster_by_line(list_of_objs, hbandwidth):   
    labels, cluster_centers = meanshift_visobjs(list_of_objs, 0, 0, 0, 1.0, 0, 0.0, 1.0, 1.0, 1.0, bandwidth=hbandwidth) 
    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)
    
    print '# lines:', n_clusters    
    lineobjs = [[] for i in range(0, n_clusters)]
    for i in range(0, len(list_of_objs)):
        lineobjs[labels[i]].append(list_of_objs[i])
    
    return lineobjs

def cluster_by_time(list_of_objs, tbandwidth):
    labels, cluster_centers = meanshift_visobjs(list_of_objs, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, tbandwidth) 
    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)
    print '# time clusters:', n_clusters    
    timeobjs = [[] for i in range(0, n_clusters)]
    for i in range(0, len(list_of_objs)):
        timeobjs[labels[i]].append(list_of_objs[i])
    
    return timeobjs

def get_labeled_objs(list_of_clusters):
    label = 0
    labels = []
    list_of_objs = []
    nclusters = len(list_of_clusters)
    for i in range(0, nclusters):
        cluster = list_of_clusters[i]
        for c in cluster:
            list_of_objs.append(c)
            labels.append(label)
        label += 1
    return list_of_objs, labels


if __name__ == "__main__":
    objdir = sys.argv[1]
    panoramapath = sys.argv[2]
    img_objs = VisualObject.objs_from_file(None, objdir)
    panorama = cv2.imread(panoramapath)
   
    lineobjs = cluster_by_line(img_objs, 3*VisualObject.avg_height(img_objs))
    nlines = len(lineobjs)
    
    list_of_objs, labels = get_labeled_objs(lineobjs)
    line_cluster = panorama_object.draw_clusters(panorama, list_of_objs, labels)
    util.showimages([line_cluster], "line cluster")
    
    
#     timed_line_objs = []
#     for i in range(0, nlines):
#         time_objs = cluster_by_time(lineobjs[i], 3*VisualObject.avg_duration(lineobjs[i]))
#         timed_line_objs.append(time_objs)
#         
#     label = 0
#     labels = []
#     list_of_objs = []
#     for i in range(0, nlines):
#         time_clusters = timed_line_objs[i]
#         for c in time_clusters:
#             list_of_objs = list_of_objs + c
#             for numitmes in c:
#                 labels.append(label)
#             label += 1
#         
#    
#     panorama_cluster = panorama_object.draw_clusters(panorama, list_of_objs, labels)
#     util.showimages([panorama_cluster], "line time cluster")
    
    