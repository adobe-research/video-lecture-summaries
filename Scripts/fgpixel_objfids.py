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
from visualobjects import VisualObject
import scroll

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
        if (next - cur != 1):
            index.append(cur)
    index.append(plateaus[-1])
    return index

def plot_plateaus(numfg, index, video=None):
    t = np.linspace(0, len(numfg), len(numfg))        
#     if (video is None):
    plt.plot(t, numfg)
    plt.scatter(index, numfg[index], c='red')
#     else:
#         for i in index:
#             frame = video.capture_frame(i)      
#             plt.plot(t, numfg)
#             plt.scatter(i, numfg[i], c = 'red')
#             util.showimages([frame], "frame %i"%i)
#             plt.show()
    
    plt.title("Number of Foreground Pixels")
    plt.xlabel("frames")
    plt.ylabel("pixels")
    plt.xlim(0, len(numfg))
    plt.savefig(video.videoname + "_fid_indices.png")
    plt.show()
    plt.close()
    
def get_obj_fids(end_of_plateau_fids, nufg):
    obj_fids = []
    prev_fg = 0
    prev_id = -1
    for i in end_of_plateau_fids:
        cur_fg = numfg[i]
        fg_diff = cur_fg - prev_fg
        if (fg_diff > 100):
            obj_fids.append((prev_id, i))
        prev_id = i
        prev_fg = cur_fg
    return obj_fids

def get_objects(tempdir, obj_fids, scroll_coords, objdir):
    list_of_objs = []
    for fids in obj_fids:
        print 'start', fids[0], 'end', fids[1]
        start_img, x = util.get_images(tempdir, [fids[0]])
        end_img, x = util.get_images(tempdir, [fids[1]])
        x1, y1 = scroll_coords[fids[0]]
        x2, y2 = scroll_coords[fids[1]]
        img = pf.get_diff_objimg(start_img[0], end_img[0], x1, y1, x2, y2)
        
        obj_mask = pf.fgmask(img, pf.BLACK_BG_THRESHOLD, pf.BLACK_BG_VAR_THRESHOLD, True)
        obj_bbox = pf.fgbbox(obj_mask)
        if (obj_bbox[0] < 0 ):
            continue
        obj_crop = pf.cropimage(img, obj_bbox[0], obj_bbox[1], obj_bbox[2], obj_bbox[3])
        objimgname = "obj_%06i_%06i.png" % (fids[0], fids[1])
        util.saveimage(obj_crop, objdir, objimgname)
        visobj = VisualObject(obj_crop,  objdir + "\\" + objimgname, fids[0], fids[1], obj_bbox[0] + x2, obj_bbox[1] + y2)
        list_of_objs.append(visobj)
        #util.showimages([start_img[0], end_img[0]], "start & end frame")
        #util.showimages([obj_mask, obj_crop], "object")
    
    objinfopath = objdir + "/obj_info.txt"
    VisualObject.write_to_file(objinfopath, list_of_objs)
    return list_of_objs 

def read_obj_fids(txt):
    list_obj_fids = util.list_of_vecs_from_txt(txt)
    obj_fids = []
    for fid in list_obj_fids:
        obj_fids.append((int(fid[0]), int(fid[1])))
    return obj_fids    
    
    
if __name__ == "__main__":    
    video = Video(sys.argv[1])
    fgpixel_txt = sys.argv[2]
    tempdir = video.videoname + "_temp"
  
    numfg = fgpixel.read_fgpixel(fgpixel_txt)
    numfg = np.array(numfg)
    index = plateaus(numfg, int(video.fps), 1)
    plot_plateaus(numfg, index, video)
    index = end_of_plateaus(index)
   
    
    print 'numframes', video.numframes -1, 'numfg', len(numfg)  
    
    obj_fids = []
    cap_fids = []
    prev_fg = 0
    prev_id = -1
    last_id = video.numframes-1
    cap_fids.append(prev_id)
    for i in index:
        cur_fg = numfg[i]
        fg_diff = cur_fg - prev_fg
        if (fg_diff > 0):
            obj_fids.append((prev_id, i))
            cap_fids.append(i)
            prev_id = i
            prev_fg = cur_fg
    obj_fids.append((prev_id, last_id))
    cap_fids.append(last_id)
    plot_plateaus(numfg, cap_fids, video)

    """write object times"""
    outfile = video.videoname + "_fgpixel_obj_fids.txt"
    frameids = open(outfile, "w")
    for fids in obj_fids:
        frameids.write("%i\t%i\n" %(fids[0], fids[1]))
    frameids.close() 
    
    tempdir = video.videoname+"_temp"
    video.capture_keyframes_fid(cap_fids, tempdir)


        
        
        
        