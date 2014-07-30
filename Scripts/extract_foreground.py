#!/usr/bin/env python
import os
import sys
import numpy as np
import cv2
import processframe as pf
import re
from writehtml import WriteHtml


if __name__ == "__main__":
    
    
    dirname = sys.argv[1]
    filelist = os.listdir(dirname)
    
    keyframes = []
    for filename in filelist:
        if "capture" in filename and ".png" in filename:
            keyframes.append(filename)

    extractdir = "extract_foreground"
    if not os.path.exists(dirname + "\\" + extractdir):
        os.makedirs(dirname + "\\" + extractdir)

    html = WriteHtml(dirname + "\\" + extractdir + "\\extract_foreground.html")
    html.writestring("<head><title>Foregound Thresholds</title></head>")
    html.openbody()
    html.opentable()
    percentile = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    html.opentablerow()
    html.cellstring("Original Image")
    for p in percentile:
        html.cellstring(str(p))
    html.closetablerow()
    
    mean = 0    
    for keyframe in keyframes:
        img = cv2.imread(dirname + "\\" + keyframe)        
        mean += np.mean(img)
    mean /= len(keyframes)
    print 'mean', mean

    for keyframe in keyframes:
        html.opentablerow()
        img = cv2.imread(dirname + "\\" + keyframe)
        html.cellimagelink("..\\" + keyframe, 500)
        for p in percentile:
            threshold = p * mean            
            print 'threshold', threshold
            mask = pf.fgmask(img, threshold)
            fgimg = pf.maskimage(img, mask)
            extension = ".png"
            basename = re.sub(extension, '', keyframe)
            cv2.imwrite(dirname + "\\" + extractdir + "\\" + basename +"_" + ("%3f" %p) + ".png", fgimg)
            html.cellimagelink(basename +"_" + ("%3f" %p) + ".png", 500)
        html.closetablerow()
    html.closetable()
    html.closebody()
    html.closehtml()
            
    
                
            
    