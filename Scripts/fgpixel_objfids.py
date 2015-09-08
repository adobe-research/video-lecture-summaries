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
    t = np.linspace(0, len(diff_numfg), len(diff_numfg))
#     plt.plot(t, diff_numfg)
#     plt.title("Difference of Num FG pixels")
#     plt.xlabel("frames")
#     plt.ylabel("pixels")
#     plt.xlim(0, len(numfg))
#     plt.savefig(video.videoname + "numfg_diffs.pdf")
#     plt.show()
#     plt.close()
    index = []
    for i in xrange(0, len(diff_numfg)-win):
        windata = diff_numfg[i:i+win]
        avg = np.average(windata)
        if avg < thres:
            index.append(i)
    
    return index

def end_of_plateaus(numfg, plateaus, thres):
    obj_fids = []
    prev_i = -1
    prev_fg = -1
    start_fid = [prev_fg]
    end_fid = []
    
    for i in range(0, len(plateaus)):
        cur_i=plateaus[i]
        cur_fg = numfg[cur_i]
        if (abs(cur_fg - prev_fg) > thres):
            """beginning of a plateau = end of drawing"""
            end_fid.append(cur_i)
            if (prev_i >= 0):
                start_fid.append(prev_i)
            prev_fg = cur_fg
        prev_i = cur_i
    
    for i in range(0, len(start_fid)):
        obj_fids.append((start_fid[i], end_fid[i]))
    return obj_fids

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
    plt.savefig(video.videoname + "_end_of_plateau_indices.pdf")
    plt.show()
    plt.close()
    
def plot_obj_indices(numfg, indexpairs, video=None):
    t = np.linspace(1, len(numfg), len(numfg))        
    plt.plot(t, numfg)
    begin = [pair[0] for pair in indexpairs]
    end = [pair[1] for pair in indexpairs]
    plt.scatter(begin, numfg[begin], c='red')
    plt.scatter(end, numfg[end], c='blue') 
    plt.title("Object Begin and End Indices")
    plt.xlabel("Frames")
    plt.ylabel("Pixels")
    plt.xlim(0, len(numfg))
    plt.savefig(video.videoname + "_obj_indices.pdf")
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
    
    """get index of end of plateaus"""  
    winsize =  int(video.fps) #1sec
    flat_thres = 5 
    p_index = plateaus(numfg, int(video.fps), flat_thres)
    sec_thres = 200
    obj_fids = end_of_plateaus(numfg, p_index, sec_thres)  
    plot_obj_indices(numfg, obj_fids, video)

    """write object times"""
    outfile = video.videoname + "_fgpixel_obj_fids.txt"
    frameids = open(outfile, "w")
    for fids in obj_fids:
        frameids.write("%i\t%i\n" %(fids[0], fids[1]))
    frameids.close() 
    
    tempdir = video.videoname+"_temp"
    for i in range(0, len(obj_fids)):
        video.capture_keyframes_fid(obj_fids[i], tempdir)


        
        
        
        