'''
Created on Oct 8, 2014

@author: hijungshin
'''

import matplotlib.pyplot as plt

def plot_visual_objects(visual_objects):
    fig, ax = plt.subplots()    
    for obj in visual_objects:
        start_fid = obj.start_fid
        end_fid = obj.end_fid
        dur = end_fid - start_fid
        objw, objh = obj.size()
        area = objw * objh
            
        ax.broken_barh([(start_fid, dur)], (10, area / dur), facecolor='none')
        ax.set_xlabel('frames')
        ax.set_ylabel('visual objects')
    plt.show()
