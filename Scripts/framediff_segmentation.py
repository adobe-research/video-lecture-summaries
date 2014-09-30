#!/usr/bin/env python
import util
import sys
from lecture import Lecture, LectureSegment 

if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    lecture = Lecture(videopath, scriptpath)

    framediffpath = sys.argv[3]
    keyframe_ts = util.get_keyframe_ts_framediff(framediffpath, lecture.video.fps)
    lecture.video.captureframes_ms(keyframe_ts, lecture.video.videoname + "_framediff")    