'''
Created on Jan 14, 2015

@author: hijungshin
'''

import sys
import lecturevisual
import util
from writehtml import WriteHtml
import os
import process_aligned_json as pjson

if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
     
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
     
    html = WriteHtml(objdir + "/test_lecturevisual.html", "Linear Summary without Context", stylesheet ="../Mainpage/summaries_v3.css")
    
    html.writestring("<iframe src=\"https://docs.google.com/forms/d/1rK79iFrErHIx-0jZHZQaIvOP_kwCZs4oaloe3WPX0xI/viewform?embedded=true\" width=\"780\" height=\"900\" frameborder=\"0\" marginheight=\"0\" marginwidth=\"0\">Loading...</iframe>")
    
    html.writestring("<h3>The first figure following the title shows a panoramic view of the entire lecture board. The following note presents figures and transcript in the order they appear in the lecture.</h3>")
    html.writestring("<h1>%s</h1><br>"%title)
    html.figure(panoramapath, width = "98%")
    
    cur_stc_id = 0
    
    for subline in list_of_sublines:
        if (len(subline.list_of_stcstrokes) > 0):
            start_stc_id = subline.list_of_stcstrokes[0].stc_id
            if (start_stc_id > cur_stc_id):
                html.opendiv(idstring="wrapper")
                html.opendiv(idstring="c0")
                for i in range(cur_stc_id, start_stc_id):
                    html.write_list_of_words(list_of_stcs[i])
#                     print 'c00 stc', i
                cur_stc_id = start_stc_id
                html.closediv()
                html.closediv()
        
        html.opendiv(idstring="wrapper")
        
        html.opendiv(idstring="c1")
        html.image(subline.obj_in_line.imgpath)
        html.closediv()
        
        html.opendiv(idstring="c2")
        if (len(subline.list_of_stcstrokes) > 0):
            start_stc_id = cur_stc_id
            end_stc_id = subline.list_of_stcstrokes[-1].stc_id
#             print 'here', cur_stc_id, end_stc_id+1
            for i in range(cur_stc_id, (end_stc_id+1)):
#                 print 'c2 stc', i
                html.write_list_of_words(list_of_stcs[i])
#             cur_stc_id = end_stc_id + 1
            html.closediv()
            cur_stc_id = subline.list_of_stcstrokes[-1].stc_id +1
        html.closediv()
    
    if (cur_stc_id < len(list_of_stcs) -1):
        html.opendiv(idstring="wrapper")
        html.opendiv(idstring="c0")
        for i in range(cur_stc_id, len(list_of_stcs)):
            html.write_list_of_words(list_of_stcs[i])
#             print 'c0 stc', i
        html.closediv()
        html.closediv()
    
    html.writestring("<p><!-- pagebreak --></p> ")
    html.writestring("<iframe src=\"https://docs.google.com/forms/d/1tWKK9LXFuqx3-dyu26wBOLD_m9EVoWMu8braJ2vEBA0/viewform?embedded=true\" width=\"780\" height=\"1280\" frameborder=\"0\" marginheight=\"0\" marginwidth=\"0\">Loading...</iframe>")
    
    html.closehtml()