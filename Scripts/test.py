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

def frame_num(filename):
    number = re.findall(r'\d+', filename)
    return int(number[len(number)-1])


if __name__ == "__main__":
    """arguments:
        script file path
        video file path
        keyframes path"""
                
    scriptpath = sys.argv[1]
    scriptfile = os.path.basename(scriptpath)   
    
   
    videopath = sys.argv[2]
    pv = processvideo.ProcessVideo(videopath)
    framerate = pv.framerate
    
    framepath = sys.argv[3]
    keyframes = []
    filelist = os.listdir(framepath)
    
    for filename in filelist:
        if "capture" in filename and ".png" in filename:
            keyframes.append(filename)            
    
    # segment script into timed sentences
    sentences = ps.get_timed_segments(scriptpath, pv.endt)
    
    # get segment time associated with keyframes
    endts = []
    for filename in keyframes:
        endframe = frame_num(filename)
        endts.append(endframe/framerate)
        
    notes = ps.sentences_to_slides(sentences, endts)    
    txtfile = open(scriptpath + "_slide", "w")
    for i in range(len(notes)):        
        txtfile.write("case " + str(i) + ":\n")
        txtfile.write("\t")
        txtfile.write("$('#hwt1text').text(\"")
        
        for n in notes[i]:            
            txtfile.write(n.content + " ")
        txtfile.write("\");\n")
        txtfile.write("\tbreak;\n")
    txtfile.close()    
        
