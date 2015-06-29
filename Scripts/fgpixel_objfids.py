'''
Created on Nov 10, 2014

@author: hijungshin
'''

import fgpixel_segmentation as fgpixel
import sys
from video import Video
import numpy as np
import util
import matplotlib.pyplot as plt
import processframe as pf

def plateaus(numfg, win, thres):
    diff_numfg = util.diff(numfg)
    index = []
    for i in xrange(0, len(diff_numfg)-win):
        windata = diff_numfg[i:i+win]
        avg = np.average(windata)
        if avg < thres:
            index.append(i)
    
    return index

def end_of_plateaus(plateaus):
    index = []
    for i in range(0, len(plateaus)-1):
        cur=plateaus[i]
        next = plateaus[i+1]
        if (next - cur != 0):
            index.append(cur)
    index.append(plateaus[-1])
    return index

def plot_plateaus(numfg, index):
    t = np.linspace(0, len(numfg), len(numfg))
    plt.plot(t, numfg)
    plt.scatter(index, numfg[index], c='red')
    plt.title("Number of Foreground Pixels")
    plt.xlabel("frames")
    plt.ylabel("pixels")
    plt.xlim(0, len(numfg))
    plt.savefig(video.videoname + "_plateaus.png")
    plt.close()

def get_object_images(tempdir, obj_fids):
    objimages = []
    for fids in obj_fids:
        print 'prev', fids[0], 'cur', fids[1]
        prev_img, x = util.get_images(tempdir, [fids[0]])
        cur_img, x = util.get_images(tempdir, [fids[1]])
        img = pf.get_diff_objimg(prev_img[0], cur_img[0])
        objimages.append(img)
#         util.showimages([prev_img[0], cur_img[0]], "prev vs cur image")
#         if img is not None:
#             util.showimages([img], "object")
    return objimages

def read_obj_fids(txt):
    list_obj_fids = util.list_of_vecs_from_txt(txt)
    obj_fids = []
    for fid in list_obj_fids:
        obj_fids.append((int(fid[0]), int(fid[1])))
    return obj_fids    
    
    
if __name__ == "__main__":    
    tempdir = sys.argv[1] 
    obj_fids_txt = sys.argv[2]
    obj_fids = read_obj_fids(obj_fids_txt)
    get_object_images(tempdir, obj_fids)
    
#     video = Video(sys.argv[1])
#     fgpixel_txt = sys.argv[2]
#     tempdir = video.videoname + "_temp"
#     print 'video.fps', video.fps
# 
#     numfg = fgpixel.read_fgpixel(fgpixel_txt)
#     numfg = np.array(numfg)
#     index = plateaus(numfg, int(video.fps/4), 1)
#     util.write_ints(index, video.videoname + "_frameids_w_zero_slope.txt")
#     
#     index = end_of_plateaus(index)
#     
#     obj_fids = []
#     cap_fids = []
#     prev_fg = 0
#     prev_id = -1
#     for i in index:
#         cur_fg = numfg[i]
#         fg_diff = cur_fg - prev_fg
#         if (fg_diff > 100):
#             obj_fids.append((prev_id, i))
#             cap_fids.append(prev_id)
#             cap_fids.append(i)
#         prev_id = i
#         prev_fg = cur_fg
#     video.capture_keyframes_fid(cap_fids, tempdir)
#     
#     """write object times"""
#     outfile = video.videoname + "_fgpixel_obj_fids.txt"
#     frameids = open(outfile, "w")
#     for fids in obj_fids:
#         frameids.write("%i\t%i\n" %(fids[0], fids[1]))
#     frameids.close()
    
#     get_object_images(tempdir, obj_fids)
    
#     start_fids = []
#     end_fids = []
#     for fids in obj_fids:
#         start_fids.append(fids[0]+video.fps/2)
#         end_fids.append(fids[1]+video.fps/2)    
#     start_keyframes = video.capture_keyframes_fid(start_fids, video.videoname + "_temp")
#     end_keyframes = video.capture_keyframes_fid(end_fids, video.videoname + "temp")
#     for i in range(0, len(start_keyframes)):
#         pf.get_diff_objimg(start_keyframes[i].frame, end_keyframes[i].frame)
        
        
        
        
        