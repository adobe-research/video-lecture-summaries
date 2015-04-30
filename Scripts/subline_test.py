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

def write_playvideo_script(html, url):
    html.writestring("function playvideo_at(sec){\n \
         var video  = document.getElementById(\"thevideo\");\n \
         var starturl = \"https://www.youtube.com/embed/%s?autoplay=1&amp;start=\"+sec +\"&amp\"; \n \
         video.src= starturl\n \
         }\n" %(url))

 
def write_stc(html, sentence):
    sec = int(sentence.startt/1000.0)
    html.writestring("<object id=\"textlink\" onclick=\"playvideo_at(%i)\">"%(sec))
    html.write_sentence(sentence, stopwords)
    html.writestring("</object>")
    
def write_subline(html, subline, figdir, video):
    html.opendiv(idstring="c1c2wrapper")
#     html.writestring("%i - %i"%(subline.list_of_strokes[0].obj.start_fid, subline.list_of_strokes[-1].obj.end_fid))
    write_subline_img(html, subline, figdir, video)
    write_subline_stc(html, subline, figdir)
    html.closediv() #c1c2wrapper
        
        
def write_subline_img(html, subline, figdir, video):
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
        html.writestring("<img src=\"%s\" height=\"20px\" id=\"arrow%i_sub%i\" \
                                    onclick=\"showline%i_sub%i()\">\n"%(collapsed_icon, lineid, subid, lineid, subid))
#         html.writestring("<div class=\"plus\" border=\"1px\" height=\"20px\" id=\"arrow%i_sub%i\" \
#                                     onclick=\"showline%i_sub%i()\"> + </div>\n"%(lineid, subid, lineid, subid))
    startt = subline.obj.start_fid
    sec = video.fid2sec(startt)
    html.writestring("<object id=\"textlink\" onclick=\"playvideo_at(%i)\">"%(sec))
    html.image(figdir + "/" + label_imgpath)
    html.writestring("</object>")

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
        html.openp()
        for stc in subline.list_of_sentences:
            write_stc(html, stc)
        html.closep()
        html.closediv() #line%i_sub%i_c2
        return
   

    list_of_prevobjs = []
    linegroup = subline.linegroup
    sub_id = subline.sub_line_id
    for i in range(0, sub_id): #all previous sublines
        list_of_prevobjs.append(linegroup.list_of_sublines[i].obj)
    
    subsubid = 0
    list_of_sublineobjs = subline.list_of_sentences[:]
    for list_of_stcstrokes in subline.list_of_subsublines:
        list_of_objs = []
        for obj in list_of_prevobjs:
            grayobj = obj.copy()
            grayobj.img = util.fg2gray(grayobj.img, 175)
            list_of_objs.append(grayobj)
        for stcstroke in list_of_stcstrokes:
            list_of_objs.append(stcstroke.obj)
        obj = VisualObject.group(list_of_objs, figdir, "line%i_upto_sub%i_subsub%i.png"%(subline.line_id, subline.sub_line_id, subsubid))
        obj.start_fid = list_of_stcstrokes[0].obj.start_fid
        subsubid += 1
        list_of_sublineobjs.append(obj)
        list_of_prevobjs += list_of_objs
    
    html.opendiv(idstring="line%i_sub%i_c2"%(lineid, subid), class_string="c2")
    write_by_time(list_of_sublineobjs, html)
    html.closediv()
    return

def insertvideo(html, url):
    html.opendiv(idstring="vid")
    html.opendiv(idstring="ytplayer")
    html.writestring("<iframe id=\"thevideo\" width=\"600px\" height=\"500px\" frameborder=\"0\" allowfullscreen=\"1\" title=\"YouTube video player\" src=\"http://www.youtube.com/embed/%s?enablejsapi=1&amp;autoplay=0\"></iframe>"%(url))
    html.closediv()
    html.closediv()


def write_by_time(list_of_objs, html):
    list_of_objs.sort(key=lambda x: x.start_fid)
    for obj in list_of_objs:
        obj.write_to_html(html)
    return
        
if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    author = sys.argv[6]
    url = sys.argv[7]
    
    video = Video(videopath)
    figdir = objdir + "/subline_linebreak_test"
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)

#     resolve_reference(list_of_sentences, list_of_sublines, framepos, cursorpos)
     
    html = WriteHtml(objdir + "/subline_line_break_test.html",title, stylesheet ="../Mainpage/subline_test_video.css")
#     html.writestring("<h3>The following is a summary of a lecture video. You may click on the '+' buttons next to the figures in order to expand further details.</h3>")
    html.writestring("<h1>%s</h1>\n"%title)
    html.writestring("<h3>%s</h3>\n"%author)

    insertvideo(html, url)
    
    html.opendiv(idstring="summary")
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
        write_subline(html, subline, figdir, video)
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
    html.closediv() #summary
            
    html.openscript()
    for i in range(0, len(list_of_sublines)):
        lineid = list_of_sublines[i].line_id
        subid = list_of_sublines[i].sub_line_id
        write_arrowtoggle_script(html, lineid, subid)
        write_showsection_script(html, lineid, subid)
    write_playvideo_script(html, url)
    html.closescript()
    html.closehtml()