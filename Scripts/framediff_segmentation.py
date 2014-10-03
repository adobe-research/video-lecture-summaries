#!/usr/bin/env python
import util
import sys
from video import Video
import numpy as np

def read_framediff(framediff_txt):
    framediff = util.stringlist_from_txt(framediff_txt)
    framediff = util.strings2ints(framediff)
    return framediff    

def get_object_frames(framediff, thres=100):
    """smooth"""
    smooth_framediff = util.smooth(np.array(framediff), window_len=3)
    object_fids = []
    drawing = False
    fid = 0
    start_t = -1
    end_t = -1
    for diff in smooth_framediff:
        if (diff > thres and not drawing):
            drawing = True
            start_t = fid
        if (diff < thres and drawing):
            drawing = False
            end_t = fid
            if (start_t >= 0 and end_t >= 0 and start_t < end_t):
                object_fids.append((start_t, end_t))
            start_t = -1
            end_t = -1
        fid += 1
    return object_fids
            


if __name__ == "__main__":
    videopath = sys.argv[1]
    video = Video(videopath)
    framediffpath = sys.argv[2]
    
    """read frame difference counts"""
    framediff = read_framediff(framediffpath)
    
    objects_fids = get_object_frames(framediff)
    keyframe_fids = [e for l in objects_fids for e in l]
    video.captureframes_fid(keyframe_fids, video.videoname + "_temp" )
    