'''
Created on Oct 8, 2014

@author: hijungshin
'''

import matplotlib.pyplot as plt
import util
import sys
from visualobjects import VisualObject
from lecture import Lecture
import numpy as np

def plot_visual_objects(ax, visual_objects):    
    for obj in visual_objects:
        start_fid = obj.start_fid
        end_fid = obj.end_fid
        dur = end_fid - start_fid
        objw, objh = obj.size()
        area = objw * objh
            
        ax.broken_barh([(start_fid, dur)], (25, area/dur), facecolor=np.random.rand(3,1))
        ax.set_xlabel('Frames')
        ax.set_ylabel('Visual objects')
 
if __name__ == "__main__":    
    objfile = sys.argv[1]
    vecs = util.list_of_vecs_from_txt(objfile)
    vecs.pop(0)
    objs = []
    for i in range(0, len(vecs)):    
        objs.append(VisualObject(int(vecs[i][0]), int(vecs[i][1]), int(vecs[i][2]), int(vecs[i][3]), int(vecs[i][4]), int(vecs[i][5])))
    fig, ax = plt.subplots()    
    plot_visual_objects(ax, objs)
    
    videopath = sys.argv[2]
    transcript = sys.argv[3]
    lecture = Lecture(videopath, transcript)  
    for stc in lecture.list_of_stcs:
        start_fid = lecture.video.ms2fid(stc[0].startt)
        end_fid = lecture.video.ms2fid(stc[-1].endt)
        ax.broken_barh([(start_fid, end_fid - start_fid)], (1, 20), facecolor=np.random.rand(3,1))
        
    ax.set_yticks([10,50])
    ax.set_yticklabels(['Stc', 'Figs'])
    ax.set_xlim(0, lecture.video.numframes)
    plt.show()
    