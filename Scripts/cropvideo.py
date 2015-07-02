'''
Created on Jul 1, 2015

@author: hijungshin
'''

from video import Video
import sys
import lecturevisual as lv
import os
from visualobjects import VisualObject

if __name__ == "__main__":    
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lv.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    
    video = Video(videopath)
    for subline in list_of_sublines:
        subobj = subline.obj
        lineobj = subline.linegroup.obj
        filename, ext = os.path.splitext(subline.obj.imgpath)
        outvideo = filename + ".avi"
        video.crop(lineobj.tlx, lineobj.tly, lineobj.brx, lineobj.bry, subobj.start_fid, subobj.end_fid, outvideo)
        
    list_of_subline_objs = [subline.obj for subline in list_of_sublines]
    sublinedir = list_of_sublines[0].objdir
    VisualObject.write_to_file(sublinedir + "/obj_info.txt", list_of_sublines)