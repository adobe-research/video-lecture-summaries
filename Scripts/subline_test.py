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
import label

collapsed_icon = "../../../../../../../Mainpage/figures/arrow_collapsed_icon.png"
expanded_icon = "../../../../../../../Mainpage/figures/arrow_expanded_icon.png"

stopwords = []

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
#     html.opendiv(idstring="c0")
#     start_fid = sentence.video.ms2fid(sentence.startt)
#     end_fid = sentence.video.ms2fid(sentence.endt)
#     html.writestring("<b>%i - %i</b><br>"%(start_fid, end_fid))
    html.write_sentence(sentence, stopwords)
#     html.closediv()
    
def write_subline(html, subline, figdir):
    html.opendiv(idstring="c1c2wrapper")
#     html.writestring("%i - %i"%(subline.list_of_strokes[0].obj.start_fid, subline.list_of_strokes[-1].obj.end_fid))
    write_subline_img(html, subline, figdir)
    write_subline_stc(html, subline, figdir)
    html.closediv() #c1c2wrapper
        
        
def write_subline_img(html, subline, figdir):
    lineid = subline.line_id
    subid = subline.sub_line_id
    
    html.opendiv(idstring="line%i_sub%i_c1"%(lineid, subid))
    upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
    subline_obj = VisualObject.group(upto_subline_objs, figdir, "line%i_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id))
    
    for lb in subline.list_of_labels:
        print lb.pos
    
    label_img = label.label_objs([subline_obj], subline.list_of_labels)
    label_imgpath = "labelline_%i_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id) 
    util.saveimage(label_img, figdir, label_imgpath)
    
    if len(subline.list_of_sentences) > 0:
        html.writestring("<img src=\"%s\" border=\"1px\" height=\"20px\" id=\"arrow%i_sub%i\" \
                                    onclick=\"showline%i_sub%i()\">\n"%(collapsed_icon, lineid, subid, lineid, subid))
#         html.writestring("<div class=\"plus\" border=\"1px\" height=\"20px\" id=\"arrow%i_sub%i\" \
#                                     onclick=\"showline%i_sub%i()\"> + </div>\n"%(lineid, subid, lineid, subid))
    html.image(figdir + "/" + label_imgpath)
    start_fid = subline.obj.start_fid
    end_fid  = subline.obj.end_fid
#     html.writestring("<br>%.2f - %.2f<br>\n"%(start_fid, end_fid))
    html.closediv() #line%i_sub%i
        
def write_subline_stc(html, subline, figdir):  
    lineid = subline.line_id
    subid = subline.sub_line_id
    nlines = len(subline.list_of_subsublines)
    
    print 'lineid, subid, nlines', lineid, subid, nlines

    """single segment"""        
    if (nlines < 2):
        html.opendiv(idstring="line%i_sub%i_c2"%(lineid, subid), class_string="c2")
        html.opendiv(idstring="c2_3")
        html.openp()
        for stc in subline.list_of_sentences:
            html.write_list_of_words(stc.list_of_words, stopwords)
        html.closep()
        html.closediv() #c2_3
        html.closediv() #line%i_sub%i_c2
        return
        
   
    html.opendiv(idstring="line%i_sub%i_c2"%(lineid, subid), class_string="c2")
    written = 0
    for i in range(0, nlines):
        list_of_stcstrokes = subline.list_of_subsublines[i]
        html.opendiv(idstring="c2_12wrapper")
        html.opendiv(idstring="c2_2")
        obj = list_of_stcstrokes[-1].obj_upto_inline(figdir)
        html.image(obj.imgpath)
        html.closediv()
        html.closediv()   
    html.closediv()     
    return


if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    author = sys.argv[6]
#     frametxt = sys.argv[6]
#     cursortxt = sys.argv[7]

    
#     fp = util.list_of_vecs_from_txt(frametxt)
#     framepos = []
#     for p in fp:
#         framepos.append((int(p[0]), int(p[1])))
#         
#     cp = util.list_of_vecs_from_txt(cursortxt)
#     cursorpos = []
#     for p in cp:
#         cursorpos.append((int(p[0]), int(p[1])))
    
    figdir = objdir + "/subline_linebreak_test"
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)

#     resolve_reference(list_of_sentences, list_of_sublines, framepos, cursorpos)
     
    html = WriteHtml(objdir + "/subline_line_break_test.html",title, stylesheet ="../Mainpage/subline_merge_subfigure.css")
#     html.writestring("<h3>The following is a summary of a lecture video. You may click on the '+' buttons next to the figures in order to expand further details.</h3>")
    html.writestring("<h1>%s</h1>\n"%title)
    html.writestring("<h3>%s</h3>\n"%author)

      
    cur_stc_id = 0
    for sublinei in range(0, len(list_of_sublines)):
        subline = list_of_sublines[sublinei]
        
        if (len(subline.list_of_sentences) > 0):
            start_stc_id = subline.list_of_sentences[0].id
            if (start_stc_id > cur_stc_id):
                html.opendiv(idstring="c0")
                html.openp()
                for i in range(cur_stc_id, start_stc_id):
                    write_stc(html, list_of_sentences[i])
                    start_fid = list_of_sentences[i].start_fid
                    end_fid = list_of_sentences[i].end_fid
#                     html.writestring("(%.2f - %.2f)"%(start_fid, end_fid))
                html.closep()
                html.closediv()
                cur_stc_id = start_stc_id
        
        else: #subline.list_of_sentences == 0
            stc = list_of_sentences[cur_stc_id]
            html.opendiv(idstring="c0")
            html.openp()
            while(stc.stcstroke is None and stc.start_fid < subline.obj.end_fid):
                write_stc(html, stc)
                start_fid = stc.start_fid
                end_fid = stc.end_fid
#                 html.writestring("(%.2f - %.2f)"%(start_fid, end_fid))
                cur_stc_id += 1
                if (cur_stc_id >= len(list_of_sentences)):
                    break
                stc = list_of_sentences[cur_stc_id]
            html.closep()
            html.closediv()
        
        #write subline
        write_subline(html, subline, figdir)
        if (len(subline.list_of_sentences) > 0):
            cur_stc_id = subline.list_of_sentences[-1].id+1
    
    if (cur_stc_id < len(list_of_sentences) -1):
        html.opendiv(idstring="c0")
        html.openp()
        for i in range(cur_stc_id, len(list_of_sentences)):
            write_stc(html, list_of_sentences[i])
            start_fid = list_of_sentences[i].start_fid
            end_fid = list_of_sentences[i].end_fid
#             html.writestring("(%.2f - %.2f) "%(start_fid, end_fid))
        html.closep()
        html.closediv() #c0
    
#     html.opendiv()
#     html.writestring("<iframe src=\"https://docs.google.com/forms/d/1Gdd7oNVeJm4-gEOG3dNTSocNp77nkgd9ELsDNELPP2Y/viewform?embedded=true\" width=\"780\" height=\"1280\" frameborder=\"0\" marginheight=\"0\" marginwidth=\"0\">Loading...</iframe>")
#     html.closediv()
            
    html.openscript()
    for i in range(0, len(list_of_sublines)):
        lineid = list_of_sublines[i].line_id
        subid = list_of_sublines[i].sub_line_id
        write_arrowtoggle_script(html, lineid, subid)
        write_showsection_script(html, lineid, subid)
    html.closescript()
    html.closehtml()