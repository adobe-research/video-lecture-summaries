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
from lecture import Lecture
from writehtml import WriteHtml


if __name__ == "__main__":
    
    videopath = sys.argv[1]
    jsonpath = sys.argv[2]
    outdir = sys.argv[3]
    
    lecture = Lecture(videopath, jsonpath)
    lecture.assign_keyframe_to_words(outdir=outdir)
    
    
    html = WriteHtml(outdir + "/script_align.html", "Script Alignment")
    html.openbody()
    html.highlighted_script(lecture.list_of_words)
    html.closebody()
    html.closehtml()