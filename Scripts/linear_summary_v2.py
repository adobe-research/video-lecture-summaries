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
    
     
    html = WriteHtml(objdir + "/linear_summary_v3.html", "Linear Summary with Context", stylesheet ="../Mainpage/summaries_v3.css")
    html.writestring("<h1>%s</h1><br>"%title)
    html.figure(panoramapath, width = "98%")
    
    figdir = objdir + "/linear_summary_v3_figures"
    if not os.path.exists(os.path.abspath(figdir)):
        os.makedirs(os.path.abspath(figdir))
    
    cur_stc_id = 0
    
    for subline in list_of_sublines:
        if (len(subline.list_of_stcstrokes) > 0):
            start_stc_id = subline.list_of_stcstrokes[0].stc_id
            if (start_stc_id > cur_stc_id):
                html.opendiv(idstring="wrapper")
                html.opendiv(idstring="c0")
                for i in range(cur_stc_id, start_stc_id):
                    html.write_stc(list_of_stcs[i])
                html.closediv()
                html.closediv()
        
        html.opendiv(idstring="wrapper")
        
        pline = lecturevisual.panorama_lines(panorama, [subline.linegroup])
        pline_filename = "panorama_line_%i_%i.png"%(subline.line_id, subline.sub_line_id)
        util.saveimage(pline, figdir, pline_filename)
        
        html.opendiv(idstring="c1")
        html.image(figdir + "/" + pline_filename)
        html.closediv()
        
        html.opendiv(idstring="c2")
        html.image(subline.obj_in_line.imgpath)
        html.closediv()
        
        html.opendiv(idstring="c3")
        if (len(subline.list_of_stcstrokes) > 0):
            start_stc_id = subline.list_of_stcstrokes[0].stc_id
            end_stc_id = subline.list_of_stcstrokes[-1].stc_id
            for i in range(start_stc_id, (end_stc_id+1)):
                html.write_stc(list_of_stcs[i])
            html.closediv()
            cur_stc_id = subline.list_of_stcstrokes[-1].stc_id
        html.closediv()
    
    if (cur_stc_id < len(list_of_stcs) -1):
        html.opendiv(idstring="wrapper")
        html.opendiv(idstring="c0")
        for i in range(cur_stc_id, len(list_of_stcs)):
            html.write_stc(list_of_stcs[i])
        html.closediv()
        html.closediv()
        
    
    html.closehtml()