'''
Created on Mar 2, 2015

@author: hijungshin
'''

import cv2
import sys
from lecture import Lecture
from writehtml import WriteHtml

if __name__ == "__main__":
    panoramapath = sys.argv[1]
    script =  sys.argv[2]
    outdir = sys.argv[3]
    
    lec = Lecture(None, script)
    html = WriteHtml(outdir + "/panorama_summary.html", "Panorama Summary", stylesheet="../Mainpage/summaries.css")
    html.figure(panoramapath, width="95%")
    for stc in lec.list_of_stcs:
        html.paragraph_list_of_words(stc)
    html.closehtml()