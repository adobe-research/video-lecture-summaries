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
    
    jsonpath = sys.argv[1]
    
    list_of_words = pj.get_words(jsonpath)
    
    prev_stc_idx = 0
    for word in list_of_words:
        if word.stc_idx > prev_stc_idx:
            print ' \n'
        print(word.original_word ),
        prev_stc_idx = word.stc_idx
        
    

    