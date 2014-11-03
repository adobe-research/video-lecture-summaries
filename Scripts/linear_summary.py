'''
Created on Nov 2, 2014

@author: hijungshin
'''

import sys
from lecture import Lecture
from visualobjects import VisualObject
import operator
from writehtml import WriteHtml
import layout

if __name__ == "__main__":
    
    """Separate individual Objects, layout linearly by start time"""
    
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    
    lec = Lecture(videopath, scriptpath)
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
    txt_objs = VisualObject.objs_from_transcript(lec)
    
    vis_objs = img_objs + txt_objs
    sorted_vis_objs = sorted(vis_objs, key=operator.attrgetter('start_fid'))
        
    objs_in_frame = layout.layout_line_by_line(sorted_vis_objs)
    html = WriteHtml(lec.video.videoname + "_obj_stc_linear.html", "Object Sentence Linear Layout", stylesheet="../Mainpage/summaries.css")
    html.openbody()
    html.writestring(lec.video.videoname)
    layout.layout_objects_html(objs_in_frame, html)
    html.closebody()
    html.closehtml()
    