'''
Created on Mar 17, 2015

@author: hijungshin
'''

import sys
import lecturevisual
if __name__ == "__main__":
    
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
     
     