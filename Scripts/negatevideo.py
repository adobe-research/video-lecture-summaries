#!/usr/bin/env python
import numpy as np
import cv2
import sys
from video import Video
import os

if __name__ == "__main__":
    
    videopath = sys.argv[1]
    video = Video(videopath)
    video.negate()
        
    