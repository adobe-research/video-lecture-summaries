'''
Created on Oct 14, 2014

@author: hijungshin
'''

import meanshift
import numpy as np

def meanshift_visobjs(list_of_visobjs, ctlx, cbrx, ctly, cbry, cstart, cend, w, h, nframes):
    data = []
    for visobj in list_of_visobjs:
        x = ctlx * visobj.tlx + cbrx * visobj.brx
        y = ctly * visobj.tly + cbry * visobj.bry
        fid = cstart*visobj.start_fid + cend*visobj.end_fid
        
        data.append((x*w, y*h, fid*nframes))
        
    labels, cluster_centers = meanshift.cluster(np.array(data))
        
    return labels, cluster_centers
        
