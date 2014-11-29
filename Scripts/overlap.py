'''
Created on Nov 25, 2014

@author: hijungshin
'''

import sys
import os
from visualobjects import VisualObject
import util

def group_overlapping_objs(list_of_objs, overlapdir, threshold=0.2):
    num_objs = len(list_of_objs)
    
    list_of_groups = []
    for i in range(0, num_objs):
        curobj = list_of_objs[i]
        joined = False
        for group in list_of_groups:
            for obj in group:
                overlap = VisualObject.overlap(curobj, obj)
                if (overlap > threshold):
                    group.append(curobj)
                    joined = True
                    break
            if (joined):
                break
        if (not joined):
            list_of_groups.append([curobj])
        
    num_groups = len(list_of_groups)
    list_of_grouped_objs = []
    for group in list_of_groups:
        list_of_grouped_objs.append(VisualObject.group(group, overlapdir))
    return list_of_grouped_objs

if __name__ == "__main__":
    objdir = sys.argv[1]
    overlapdir = objdir + "/overlap"
    if not os.path.exists(overlapdir):
        os.makedirs(overlapdir)
        
    list_of_objs = VisualObject.objs_from_file(None, objdir)
    num_objs = len(list_of_objs)
    
    list_of_groups = []
    for i in range(0, num_objs):
        curobj = list_of_objs[i]
        joined = False
        for group in list_of_groups:
            for obj in group:
                overlap = VisualObject.overlap(curobj, obj)
                if (overlap > 0.20):
                    group.append(curobj)
                    joined = True
                    break
            if (joined):
                break
        if (not joined):
            list_of_groups.append([curobj])
        
    num_groups = len(list_of_groups)
    print 'num objects: ', num_objs
    print 'num groups:', num_groups
    
    for group in list_of_groups:
        grouped_objs = VisualObject.group(group, "temp")
        util.showimages([grouped_objs.img], "grouped object")
                
            