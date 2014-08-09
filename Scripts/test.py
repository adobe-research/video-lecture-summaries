#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
from PIL import Image
import images2gif
import processvideo
from sentence import Sentence
import processscript as ps
import re
import process_aligned_json as pj
from video import Video

def frame_num(filename):
    number = re.findall(r'\d+', filename)
    return int(number[len(number)-1])


if __name__ == "__main__":
    
    videopath = sys.argv[1]
    startt = int(sys.argv[2])
    endt = int(sys.argv[3])
    myvideo = Video(videopath)
    cutvideo = myvideo.cut(startt, endt)
    print cutvideo

    