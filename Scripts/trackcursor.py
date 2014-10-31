'''
Created on Sep 30, 2014

@author: Valentina
'''

import sys
import processvideo as pv
import cv2
import matplotlib.pyplot as plt
import numpy as np
import util

def track(video, cursorimg):
    pos = video.tracktemplate(cursorimg)
    return pos

def write(pos, cursorpostxt="cursorpos.txt"):
    print "Writing to", cursorpostxt
    cursorpos = open(cursorpostxt, "w")
    for p in pos:
        if (p == None):
            cursorpos.write("%i\t%i\n" % (-1, -1))            
        else:
            cursorpos.write("%i\t%i\n" % (int(p[0]), int(p[1])))
    cursorpos.close()
    
def read(cursorpostxt):
    pos = util.list_of_vecs_from_txt(cursorpostxt)   
    return pos
    
def main_track():
    videoname = sys.argv[1]
    cursorfile = sys.argv[2]
    video = pv.ProcessVideo(videoname)
    cursor = cv2.imread(cursorfile)
    pos = track(video, cursor)
#     cursorpostxt = video.videoname+"_cursorpos.txt"
#     write(pos, cursorpostxt)
#     
    
def plot_ty(pos, outfile="cursor_ty.png"):
    t = np.linspace(0, len(pos)-1, len(pos))
    y = [p[1] for p in pos]
    print 'len(t)', len(t)
    print 'len(pos)', len(pos)
    print 'len(y)', len(y)
    
    plt.plot(t, y,'b.')
    plt.xlabel("Frame Number")
    plt.ylabel("Cursor y-position")
    plt.xlim(0, len(pos))
    plt.savefig(outfile)
    plt.show()
    plt.close()           
    
    
if __name__ == "__main__":    
    main_track()