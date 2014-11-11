'''
Created on Nov 10, 2014

@author: hijungshin
'''

import fgpixel_segmentation as fgpixel
import sys
from video import Video

if __name__ == "__main__":    
    video = Video(sys.argv[1])
    fgpixel_txt = sys.argv[2]
    numfg = fgpixel.read_fgpixel(fgpixel_txt)
    fgpixel.get_object_start_end_frames(numfg, video)