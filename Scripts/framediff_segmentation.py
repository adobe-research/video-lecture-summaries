#!/usr/bin/env python
import util
import sys
from video import Video

if __name__ == "__main__":
    videopath = sys.argv[1]
    video = Video(videopath)
    framediffpath = sys.argv[2]
    thres=200
    keyframe_ids = util.get_keyframe_ids_framediff(framediffpath, thres)
    video.captureframes_fid(keyframe_ids, video.videoname + "_framediff_" + ("%i" % thres) )
    