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


if __name__ == "__main__":
    
    videopath = sys.argv[1]
    jsonpath = sys.argv[2]
    
    video = Video(videopath)
    list_of_words = pj.get_words(jsonpath)
    pj.assign_frame_to_words(video, list_of_words)
    
    for word in list_of_words:
        cv2.imshow("word frame", word.frame)
        cv2.imshow("word mask", word.mask)
        print word.original_word
        cv2.waitKey()
    

    