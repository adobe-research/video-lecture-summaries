'''
Created on Nov 10, 2014

@author: hijungshin
'''

import fgpixel_segmentation as fgpixel
import sys
from video import Video
import numpy as np
import util

if __name__ == "__main__":    
    video = Video(sys.argv[1])
    print 'video', video.fps
    fgpixel_txt = sys.argv[2]
    numfg = fgpixel.read_fgpixel(fgpixel_txt)
    
    numfg = np.array(numfg)
    numfg = util.smooth(numfg, window_len=5)
    
    fgpixel.get_object_start_end_frames(numfg, video)