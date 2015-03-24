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

def write_showsection_script(html, section_id):
    html.writestring("function showsection%i(){\n\t \
    var cap  = document.getElementById(\"section%i_c2\");\n \
    cap.style.display == \"inline-block\" ? cap.style.display = \"none\" : cap.style.display = \"inline-block\";\n \
    }\n"%(section_id, section_id))

def write_arrowtoggle_script(html, i):
    html.writestring("$('#arrow%i').on({\n \
    \t'click': function() {\n \
     \t\t var src = ($(this).attr('src') === \"%s\")\n \
            ? \"%s\"\n \
            : \"%s\";\n \
         $(this).attr('src', src);\n \
        }\n \
    });\n"%(i, collapsed_icon, expanded_icon, collapsed_icon))
    

if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    figdir = objdir + "/subline_test"
    
    stopwords = ['here', 'Here', 'here.', 'here,', 'this', 'This', 'this.', 'this,']
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    video = Video(videopath)
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
     
    html = WriteHtml(objdir + "/subline_test.html", "Subline Test", stylesheet ="../Mainpage/subline_test.css")
    html.writestring("<h1>%s</h1><br>\n"%title)
    
    cur_stc_id = 0 
    for sublinei in range(0, len(list_of_sublines)):
        subline = list_of_sublines[sublinei]
        if (len(subline.list_of_sentences) > 0):
            start_stc_id = subline.list_of_sentences[0].id
            if (start_stc_id > cur_stc_id):
                html.opendiv(idstring="c0_wrapper")
                html.opendiv(idstring="c0")
                for i in range(cur_stc_id, start_stc_id):
                    stc = list_of_sentences[i]
                    html.write_list_of_words(stc.list_of_words, stopwords)
#                     html.writestring("%.3f - %.3f"%(stc.startt, stc.endt))
                cur_stc_id = start_stc_id
                html.closediv()
                html.closediv()
        else: #subline.list_of_sentences == 0
            stc = list_of_sentences[cur_stc_id]
            while(stc.end_fid < subline.obj.start_fid):
                html.opendiv(idstring="c0_wrapper")
                html.opendiv(idstring="c0")
                html.write_list_of_words(stc.list_of_words, stopwords)
#                 html.writestring("%.3f - %.3f"%(stc.startt, stc.endt))
                html.closediv()
                html.closediv()
                cur_stc_id += 1
                stc = list_of_sentences[cur_stc_id]
        
        html.opendiv(idstring="c1c2wrapper")
        
        html.opendiv(idstring="section%i_c1"%(sublinei))
        upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
        subline_obj = VisualObject.group(upto_subline_objs, figdir, "line%i_upto_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id))
        if len(subline.list_of_sentences) > 0:
            html.writestring("<img src=\"%s\" border=\"1px\" height=\"20px\" id=\"arrow%i\" \
                                        onclick=\"showsection%i()\">\n"%(collapsed_icon, sublinei, sublinei))
        html.image(subline_obj.imgpath)
        subline_startt = video.fid2ms(subline.obj.start_fid)
        subline_endt  = video.fid2ms(subline.obj.end_fid)
#         html.writestring("<p>%.3f - %.3f</p>"%(subline_startt, subline_endt))
        html.closediv() #c1
        
        html.opendiv(idstring="section%i_c2"%(sublinei), class_string="c2")
        for sentence in subline.list_of_sentences:
            if len(subline.list_of_sentences) <= 1:
                html.opendiv(idstring="c2_1_lone")
                html.paragraph_list_of_words(sentence.list_of_words, stopwords)
                html.closediv()  #c2_1_lone
            else:
                html.opendiv(idstring="c2_1")    
                html.paragraph_list_of_words(sentence.list_of_words, stopwords)
    #             html.writestring("%.3f - %.3f"%(sentence.list_of_words[0].startt, sentence.list_of_words[-1].endt))
                html.closediv()  #c2_1
                
            html.opendiv(idstring="c2_2")
            if len(subline.list_of_sentences) > 1 and sentence.stcstroke is not None:
                stcobj = sentence.stcstroke.obj_upto_inline(figdir)
                html.image(stcobj.imgpath)
                stcstroke_startt = video.fid2ms(sentence.stcstroke.obj.start_fid)
                stcstroke_endt = video.fid2ms(sentence.stcstroke.obj.end_fid)
#                 html.writestring("<p>%.3f - %.3f</p>"%(stcstroke_startt, stcstroke_endt))
            html.closediv() #c2_2    
            cur_stc_id = sentence.id+1
        html.closediv() #c2
        html.closediv() #wrapper
        
    
    if (cur_stc_id < len(list_of_stcs) -1):
        html.opendiv(idstring="c0_wrapper")
        html.opendiv(idstring="c0")
        for i in range(cur_stc_id, len(list_of_stcs)):
            html.write_list_of_words(list_of_stcs[i], stopwords)
#             html.writestring("%.3f - %.3f"%(list_of_stcs[i][0].startt, list_of_stcs[i][-1].endt))
        html.closediv()
        html.closediv()
        
    html.openscript()
    for i in range(0, len(list_of_sublines)):
        write_arrowtoggle_script(html,i)
        write_showsection_script(html, i)
    html.closescript()
    html.closehtml()