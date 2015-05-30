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

collapsed_icon ="../../../../../../../Mainpage/figures/arrow_collapsed_icon_2.png"#"../Mainpage/figures/arrow_collapsed_icon_2.png" # ##
expanded_icon ="../../../../../../../Mainpage/figures/arrow_collapsed_icon_2.png"#"../Mainpage/figures/arrow_collapsed_icon_2.png"#

stopwords = []

def write_showsection_script(html, lineid, subid):
    html.writestring("function showline%i_sub%i(){\n"
    "\tvar cap  = document.getElementById(\"line%i_sub%i_c2\");\n"
    "\tcap.style.display == \"inline-block\" ? cap.style.display = \"none\" : cap.style.display = \"inline-block\";\n"
    "}\n\n"%(lineid, subid, lineid, subid))

def write_arrowtoggle_script(html, lineid, subid):
    html.writestring("$('#arrow%i_sub%i').on({\n"
    "\t'click': function() {\n "
    "\t\t var src = ($(this).attr('src') === \"%s\")\n"
    "\t\t? \"%s\"\n"
    "\t\t: \"%s\";\n"
    "\t\t$(this).attr('src', src);\n"
    "\t}\n"
    "});\n\n"%(lineid, subid, collapsed_icon, expanded_icon, collapsed_icon))
    
def write_plustoggle_script(html, lineid, subid):
    html.writestring("$('#arrow%i_sub%i').on({\n \
    \t'click': function() {\n \
    if ($(\"#arrow%i_sub%i\").text() == \"-\") {\
    $(\"#arrow%i_sub%i\").text(\"+\" ); } \
    else { $(\"#arrow%i_sub%i\").text(\"-\" );\
    } \
    } \
    });\n\n"%(lineid, subid, lineid, subid, lineid, subid, lineid, subid))

def write_playvideo_script(html, url):
    html.writestring("function playvideo_at(sec){\n"
    "\tplayer.seekTo(sec, true);\n"
    "\tplayer.playVideo();\n"
    "}\n\n")

def write_expandall_script(html):
    html.writestring("function expandall(){\n"
         "\tvar c2s = document.getElementsByClassName(\"c2\");\n"
         "\tfor (var i = 0; i < c2s.length; i++) {\n"
        "\t\tc2s[i].style.display = \"inline-block\";\n"
        "\t}\n"
        "\tvar arrows = document.getElementsByClassName(\"arrow\");\n"
        "\tfor (var i = 0; i < arrows.length; i++) {\n"
        "\t\tvar src = \"%s\";\n"
        "\t\t$(arrows[i]).attr('src', src);\n"
        "\t}\n"
        "}\n"%(expanded_icon))
     
def write_collapseall_script(html):
    html.writestring("function collapseall(){\n"
         "\tvar c2s = document.getElementsByClassName(\"c2\");\n"
         "\tfor (var i = 0; i < c2s.length; i++) {\n"
         "\t\tc2s[i].style.display = \"none\";\n"
         "\t}\n"
        "\tvar arrows = document.getElementsByClassName(\"arrow\");\n"
        "\tfor (var i = 0; i < arrows.length; i++) {\n"
        "\t\tvar src = \"%s\";\n"
        "\t\t$(arrows[i]).attr('src', src);\n"
        "\t}\n"
        "}\n"%(collapsed_icon))
 
 
def write_stc(html, sentence):
    sentence.write_to_html(html)
    
def write_subline(html, subline, figdir, video):
    html.opendiv(idstring="c1c2wrapper")
    write_subline_img(html, subline, figdir, video)
    write_subline_stc(html, subline, figdir, video)
    html.closediv() #c1c2wrapper
        
        
def write_subline_img(html, subline, figdir, video):
    lineid = subline.line_id
    subid = subline.sub_line_id
    
    html.opendiv(idstring="line%i_sub%i_c1"%(lineid, subid), class_string="c1")
    upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
    subline_obj = VisualObject.group(upto_subline_objs, figdir, "line%i_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id))
    
    for lb in subline.list_of_labels:
        print lb.pos
    
    label_img = label.label_objs([subline_obj], subline.list_of_labels)
    label_imgpath = "labelline_%i_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id) 
    util.saveimage(label_img, figdir, label_imgpath)
    
    if len(subline.list_of_sentences) > 0:
        html.writestring("<img class=\"arrow\" src=\"%s\" height=\"10px\" id=\"arrow%i_sub%i\" \
                                    onclick=\"showline%i_sub%i()\">\n"%(collapsed_icon, lineid, subid, lineid, subid))
    startt = video.fid2sec(subline.obj.start_fid)
    endt = video.fid2sec(subline.obj.end_fid)
    html.writestring("<object onclick=\"playvideo_at(%i);showline%i_sub%i();\">"%(startt, lineid, subid))
    h,w = label_img.shape[0:2]
    imgpath = html.relpath(figdir +"/" + label_imgpath)
    html.writestring("<img src= \"%s\" width=\"%s\" height=\"%s\" class=\"textlink\" startt=\"%s\" endt=\"%s\" />\n" % (imgpath, 0.75*w, 0.75*h, startt, endt))
    html.writestring("</object>\n")
#     html.image(figdir + "/" + label_imgpath, width=0.75*w, height=0.75*h, class_string="textlink")
#     html.writestring("</div>")

#     html.writestring("<br>%.2f - %.2f<br>\n"%(start_fid, end_fid))
    html.closediv() #line%i_sub%i
        
def write_subline_stc(html, subline, figdir, video):  
    lineid = subline.line_id
    subid = subline.sub_line_id
    nlines = len(subline.list_of_subsublines)    
    print 'lineid, subid, nlines', lineid, subid, nlines
    """no sentence"""
    if nlines == 0 or len(subline.list_of_sentences) == 0:
        return

    """single segment"""        
    if (nlines == 1 and len(subline.list_of_sentences) > 0):
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
    write_by_time(list_of_sublineobjs, html, video)
    html.closediv()
    return

def write_insertvideo_script(html, url):
    html.writestring("var tag = document.createElement('script');\n"
    "tag.src = \"https://www.youtube.com/iframe_api\";\n"
    "var firstScriptTag = document.getElementsByTagName('script')[0];\n"
    "firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);\n\n"
    "var player;\n"
    "var videotime;\n"
    "function onYouTubeIframeAPIReady() {\n"
    "\t\tplayer = new YT.Player('player', {\n"
    "\t\theight: '320',\n"
    "\t\twidth: '570',\n"
    "\t\tvideoId: '%s',\n"
    "\t\tevents: {\n"
    "\t\t\t'onReady': onPlayerReady,\n"
#     "\t\t\t'onStateChange': onPlayerStateChange\n"
    "\t\t}\n"
    "\t});\n"
    "}\n\n" % (url))
    
    write_onready_script(html)
    

def write_onready_script(html):
    html.writestring("function onPlayerReady(event) {\n"
    "\tfunction updateTime() {\n"
    "\t\tvideotime = player.getCurrentTime();\n"
    "\t\thighlightCurrent();\n"
    "\t}\n"
    "\ttimeupdate = setInterval(updateTime, 1000);\n"
    "}\n\n")
    
    write_highlight_current_script(html)
    
def write_highlight_current_script(html):
    html.writestring("function highlightCurrent(){\n"
    "\tvar links = document.getElementsByClassName(\"textlink\");\n"
    "\tfor (var i = 0; i < links.length; i++) {\n"
    "\t\tvar startt = links[i].getAttribute(\"startt\");\n"
    "\t\tvar endt = links[i].getAttribute(\"endt\");\n"
    "\t\tif (startt < videotime && videotime < endt) {\n"
    "\t\t\tlinks[i].style.backgroundColor = \"#ff72b0\";\n"
    "\t\t} else {\n"
    "\t\t\tlinks[i].style.backgroundColor = '#ffffff';\n"
    "\t\t}\n"
    "\t}\n"
    "};\n\n");

    
    
def write_by_time(list_of_objs, html, video):
    list_of_objs.sort(key=lambda x: x.start_fid)
    for obj in list_of_objs:
        obj.video = video
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
    outdir = sys.argv[8]#objdir #
    
    if not os.path.exists(os.path.abspath(outdir)):
        os.makedirs(os.path.abspath(outdir))
    video = Video(videopath)
    figdir = outdir + "/subline_linebreak_test"
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
     
    html = WriteHtml(outdir + "/find_example.html",title, stylesheet =outdir+"../../../../../../../Mainpage/subline_test_video.css")

    html.writestring("<h1>%s</h1>\n"%title)
    html.writestring("<h3>%s</h3>\n"%author)

    videostring="player"
    html.opendiv(idstring="vid")
    html.opendiv(idstring="ytplayer")
    html.writestring("\t")
    html.opendiv(idstring=videostring)
    html.closediv() #player
    html.closediv() #ytplayer
    html.closediv() #vid

    
    html.opendiv(idstring="summary")
    
    html.opendiv(idstring="transcriptbutton")
    html.writestring("<button id=\"expand\" onclick=\"expandall()\">Expand all transcript</button>")
    html.writestring("<button id=\"expand\" onclick=\"collapseall()\">Collapse all transcript</button><br>")
    html.closediv()
    
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
            if (stc.stcstroke is None and stc.end_fid < subline.obj.end_fid):
                html.opendiv(idstring="c0")
                html.openp()
                while(stc.stcstroke is None and stc.end_fid < subline.obj.end_fid):
                    write_stc(html, stc)
    #                 start_fid = stc.start_fid
    #                 end_fid = stc.end_fid
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
    print 'cur_stc_id', cur_stc_id, 'len(list_of_sentences)', len(list_of_sentences)
    if (cur_stc_id < len(list_of_sentences)):
        html.opendiv(idstring="c0")
        html.openp()
        for i in range(cur_stc_id, len(list_of_sentences)):
            write_stc(html, list_of_sentences[i])
            start_fid = list_of_sentences[i].start_fid
            end_fid = list_of_sentences[i].end_fid
        html.closep()
        html.closediv() #c0
    html.closediv() #summary
            
    html.openscript()
    write_insertvideo_script(html, url)
    for i in range(0, len(list_of_sublines)):
        lineid = list_of_sublines[i].line_id
        subid = list_of_sublines[i].sub_line_id
        write_arrowtoggle_script(html, lineid, subid)
        write_showsection_script(html, lineid, subid)
    write_playvideo_script(html, url)
    write_expandall_script(html)
    write_collapseall_script(html)
    html.closescript()
    html.closehtml()