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
from video import Video
from visualobjects import VisualObject

collapsed_icon = "../../../../../../../Mainpage/figures/arrow_collapsed_icon.png"
expanded_icon = "../../../../../../../Mainpage/figures/arrow_expanded_icon.png"

def write_showsection_script(html, lineid, subid):
    html.writestring("function showline%i_sub%i(){\n\t \
    var cap  = document.getElementById(\"line%i_sub%i_c2\");\n \
    cap.style.display == \"inline-block\" ? cap.style.display = \"none\" : cap.style.display = \"inline-block\";\n \
    }\n"%(lineid, subid, lineid, subid))

def write_arrowtoggle_script(html, lineid, subid):
    html.writestring("$('#arrow%i_sub%i').on({\n \
    \t'click': function() {\n \
     \t\t var src = ($(this).attr('src') === \"%s\")\n \
            ? \"%s\"\n \
            : \"%s\";\n \
         $(this).attr('src', src);\n \
        }\n \
    });\n"%(lineid, subid, collapsed_icon, expanded_icon, collapsed_icon))
    
def write_plustoggle_script(html, lineid, subid):
    html.writestring("$('#arrow%i_sub%i').on({\n \
    \t'click': function() {\n \
    if ($(\"#arrow%i_sub%i\").text() == \"-\") {\
    $(\"#arrow%i_sub%i\").text(\"+\" ); } \
    else { $(\"#arrow%i_sub%i\").text(\"-\" );\
    } \
    } \
    });\n"%(lineid, subid, lineid, subid, lineid, subid, lineid, subid))
     
def write_stc(html, sentence):
    html.opendiv(idstring="c0")
    html.write_list_of_words(sentence.list_of_words)
    html.closediv()
    
def write_subline(html, subline, figdir):
    html.opendiv(idstring="c1c2wrapper")
    write_subline_img(html, subline, figdir)
    write_subline_stc(html, subline, figdir)
    html.closediv() #c1c2wrapper
        
        
def write_subline_img(html, subline, figdir):
    lineid = subline.line_id
    subid = subline.sub_line_id
    
    html.opendiv(idstring="line%i_sub%i_c1"%(lineid, subid))
    upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
    subline_obj = VisualObject.group(upto_subline_objs, figdir, "line%i_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id))
    if len(subline.list_of_sentences) > 0:
#         html.writestring("<img src=\"%s\" border=\"1px\" height=\"20px\" id=\"arrow%i_sub%i\" \
#                                     onclick=\"showline%i_sub%i()\">\n"%(collapsed_icon, lineid, subid, lineid, subid))
        html.writestring("<div class=\"plus\" border=\"1px\" height=\"20px\" id=\"arrow%i_sub%i\" \
                                    onclick=\"showline%i_sub%i()\"> + </div>\n"%(lineid, subid, lineid, subid))
    html.image(subline_obj.imgpath)
    html.closediv() #line%i_sub%i
        
def write_subline_stc(html, subline, figdir):
    lineid = subline.line_id
    subid = subline.sub_line_id
    print 'lineid, subid', lineid, subid
    
    nstc = len(subline.list_of_sentences)
    if nstc == 1:
        html.opendiv(idstring="line%i_sub%i_c2"%(lineid, subid), class_string="c2")
        html.opendiv(idstring="c2_3")
        html.paragraph_list_of_words(subline.list_of_sentences[0].list_of_words)
        html.closediv() #c2_3
        html.closediv() #line%i_sub%i_c2
        return
    
    html.opendiv(idstring="line%i_sub%i_c2"%(lineid, subid), class_string="c2")
    written = 0
    for i in range(0, nstc):
        sentence = subline.list_of_sentences[i]
        if (sentence.stcstroke is None):
            #draw previous
            if written < i:
                html.opendiv(idstring="c2_12wrapper")
                html.opendiv(idstring="c2_1")
                for j in range(written, i):
                    html.paragraph_list_of_words(subline.list_of_sentences[j].list_of_words)

                html.closediv() #c2_1
                html.opendiv(idstring="c2_2")
                if (i > 0):
                    prevsentence = subline.list_of_sentences[i-1]
                    if (prevsentence.stcstroke is not None):
                        obj = prevsentence.stcstroke.obj_inline_range(figdir, written, i-1)
                        html.image(obj.imgpath)
                html.closediv() #c2_2
                html.closediv() #c2_12wrapper
                written = i                
            # write current sentence
            html.opendiv(idstring="c2_3")
            html.paragraph_list_of_words(subline.list_of_sentences[i].list_of_words)
            html.closediv() #c2_3
            written = i+1
        i += 1
    
    #write rest of stc, figure
    if (written <= nstc - 1):
        if written == 0:
            html.opendiv(idstring="c2_3")
            for j in range(written, nstc):
                html.paragraph_list_of_words(subline.list_of_sentences[j].list_of_words)
            html.closediv() #c2_3
        else:     
            html.opendiv(idstring="c2_12wrapper")
            html.opendiv(idstring="c2_1")
            for j in range(written, nstc):
                html.paragraph_list_of_words(subline.list_of_sentences[j].list_of_words)
            html.closediv() #c2_1
            html.opendiv(idstring="c2_2")
            prevsentence = subline.list_of_sentences[nstc-1]
            if (prevsentence.stcstroke is not None):
                obj = prevsentence.stcstroke.obj_inline_range(figdir, written, nstc-1)
                html.image(obj.imgpath)
            html.closediv() #c2_2
            html.closediv() #c2_12wrapper
  
    html.closediv() #line%i_sub%i_c2
    return
    

if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    figdir = objdir + "/subline_merge_subfigure"
    stopwords = []
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    video = Video(videopath)
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
     
    html = WriteHtml(objdir + "/subline_merge_subfigure.html", "Subline Merge SubFigure", stylesheet ="../Mainpage/subline_merge_subfigure.css")
    html.writestring("<h1>%s</h1><br>\n"%title)
    html.writestring("<h3>The following is a summary of a lecture video. You may click on the '+' buttons next to the figures in order to expand further details.</h3>")

      
    cur_stc_id = 0
    for sublinei in range(0, len(list_of_sublines)):
        subline = list_of_sublines[sublinei]
        
        if (len(subline.list_of_sentences) > 0):
            start_stc_id = subline.list_of_sentences[0].id
            if (start_stc_id > cur_stc_id):
                for i in range(cur_stc_id, start_stc_id):
                    write_stc(html, list_of_sentences[i])
                cur_stc_id = start_stc_id
        
        else: #subline.list_of_sentences == 0
            stc = list_of_sentences[cur_stc_id]
            while(stc.end_fid < subline.obj.start_fid):
                write_stc(html, stc)
                cur_stc_id += 1
                stc = list_of_sentences[cur_stc_id]
        
        #write subline
        write_subline(html, subline, figdir)
        if (len(subline.list_of_sentences) > 0):
            cur_stc_id = subline.list_of_sentences[-1].id+1
    
    if (cur_stc_id < len(list_of_sentences) -1):
        for i in range(cur_stc_id, len(list_of_sentences)):
            write_stc(html, list_of_sentences[i])
    
    html.opendiv()
    html.writestring("<iframe src=\"https://docs.google.com/forms/d/1Gdd7oNVeJm4-gEOG3dNTSocNp77nkgd9ELsDNELPP2Y/viewform?embedded=true\" width=\"780\" height=\"1280\" frameborder=\"0\" marginheight=\"0\" marginwidth=\"0\">Loading...</iframe>")
    html.closediv()
            
    html.openscript()
    for i in range(0, len(list_of_sublines)):
        lineid = list_of_sublines[i].line_id
        subid = list_of_sublines[i].sub_line_id
        write_plustoggle_script(html, lineid, subid)
        write_showsection_script(html, lineid, subid)
    html.closescript()
    html.closehtml()