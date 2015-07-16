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
from moviepy.editor import *
import moviepy.video.fx.all as vfx

collapsed_icon = ""
expanded_icon =""
zoomin_icon = ""
zoomout_icon =""
stopwords = []

def write_showsection_script(html, lineid, subid):
    html.writestring("function showline%i_sub%i(){\n"
    "\tvar cap  = document.getElementById(\"line%i_sub%i_c2\");\n"
    "\tcap.style.display == \"inline-block\" ? cap.style.display = \"none\" : cap.style.display = \"inline-block\";\n"
    "}\n\n"%(lineid, subid, lineid, subid))
    
def write_zoomvideo_script(html, lineid, sublineid, clipdir, figdir):
    filename = "line%i_sub%i"%(lineid, sublineid)
    clipsrc = clipdir + "/" + filename + ".mp4"
    cropsrc = clipdir + "/" + filename + "_crop.mp4"
    clipposter = figdir + "/" + filename+"_poster.png"
    cropposter = figdir + "/" + filename +"_crop_poster.png"
    
    html.writestring("function zoomvideo%i_sub%i(){\n"
    "\tvar cap  = document.getElementById(\"video%i_sub%i\");\n"
    "\tvar ctime = cap.currentTime;\n"
    "\tvar cplay = false;\n"
    "\tif (!cap.paused) {\n"
    "\t\tcplay = true;\n"
    "\t}\n"
    "\tif(cap.zoomed != \"false\") {\n"
    "\t\tcap.zoomed = \"false\"; cap.src = \"%s\"; cap.poster = \"%s\"; cap.style.width=\"90%%\";}\n"
    "\telse { \n"
    "\t\tcap.zoomed = \"true\"; cap.src=\"%s\"; cap.poster = \"%s\"; cap.style.width=\"\"}\n"
    "\tif (cplay) {\n"
    "\t\tcap.currentTime = ctime;\n"
    "\t\tcap.play();\n"
    "\t}\n"
    "}\n\n"%(lineid, sublineid, lineid, sublineid, clipsrc, clipposter, cropsrc, cropposter))

def write_videocontrol_script(html, lineid, subid):
    html.writestring("$('#video%i_sub%i').hover(function toggleControls() {\n"
    "\tvar video = document.getElementById(\"video%i_sub%i\")\n"
    "\tif (video.hasAttribute(\"controls\")) {\n"
    "\t\tvideo.removeAttribute(\"controls\")\n"
    "\t} else {\n"
    "\t\tvideo.setAttribute(\"controls\", \"controls\")\n"
    "\t}\n"
    "})\n\n" %(lineid, subid, lineid, subid))    


def write_arrowtoggle_script(html, lineid, subid):
    html.writestring("$('#arrow%i_sub%i').on({\n"
    "\t'click': function() {\n "
    "\t\t var src = ($(this).attr('src') === \"%s\")\n"
    "\t\t? \"%s\"\n"
    "\t\t: \"%s\";\n"
    "\t\t$(this).attr('src', src);\n"
    "\t}\n"
    "});\n\n"%(lineid, subid, collapsed_icon, expanded_icon, collapsed_icon))
    
def write_zoomtoggle_script(html, lineid, subid):
    html.writestring("$('#zoom%i_sub%i').on({\n"
    "\t'click': function() {\n "
    "\t\t var src = ($(this).attr('src') === \"%s\")\n"
    "\t\t? \"%s\"\n"
    "\t\t: \"%s\";\n"
    "\t\t$(this).attr('src', src);\n"
    "\t}\n"
    "});\n\n"%(lineid, subid, zoomout_icon, zoomin_icon, zoomout_icon))


def write_playvideo_script(html, lineid, subid):
    html.writestring("function play_video%i_sub%i_at(sec){\n"
    "\tvar video = document.getElementById('video%i_sub%i');\n"
    "\tvideo.currentTime = sec;\n"
    "\tvideo.play();\n"
    "}\n\n" %(lineid, subid, lineid, subid))

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
    
def write_subline(html, subline, figdir, clipdir, outdir, video):
    html.opendiv(class_string="c1c2wrapper")
    write_subline_img(html, subline, figdir, clipdir, video)
    write_subline_stc(html, subline, figdir, video)
    html.closediv() #c1c2wrapper
        
        
def write_subline_img(html, subline, figdir, clipdir, myvideo):
    lineid = subline.line_id
    subid = subline.sub_line_id
    filename = "line%i_sub%i"%(lineid, subid)
    
    upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
    subline_obj = VisualObject.group(upto_subline_objs, figdir, filename+".png")
    
    clippath =  filename +"_poster.png"
    clipposter = myvideo.capture_frame(subline.obj.end_fid)
    util.saveimage(clipposter, figdir, clippath)
    
    croppath = filename + "_crop_poster.png"
    util.saveimage(subline_obj.img, figdir, croppath )
    
    html.opendiv(idstring="line%i_sub%i_c1"%(lineid, subid), class_string="c1")
    if len(subline.list_of_sentences) > 0:
        html.writestring("<img class=\"arrow\" src=\"%s\" height=\"30px\" id=\"arrow%i_sub%i\" \
                                    onclick=\"showline%i_sub%i()\">\n"%(collapsed_icon, lineid, subid, lineid, subid))
    
    html.writestring("<img class=\"zoom\" src=\"%s\" height=\"27px\" id=\"zoom%i_sub%i\" \
                                onclick=\"zoomvideo%i_sub%i()\">\n"%(zoomout_icon, lineid, subid, lineid, subid))
    
    cropsrc = clipdir + "/" + filename + "_crop.mp4"
    html.writestring("<video id=\"video%i_sub%i\" startt=\"%i\" poster=\"%s\" zoomed=\"true\" >\n \
                                <source src = \"%s\" type=\"video/mp4\">\n \
                                </video>\n"%(lineid, subid, subline.video_startt, os.path.relpath(figdir + "/" + croppath, html.filedir), os.path.relpath(cropsrc, html.filedir)))
        
    html.closediv() #line%i_sub%i
    
#     """make subclip and cropped subclip""" 
#     img_startt = subline.obj.start_fid
#     img_endt = subline.obj.end_fid
#     if len(subline.list_of_video_sentences) > 0:
#         stc_startt = subline.list_of_video_sentences[0].start_fid
#         stc_endt = subline.list_of_video_sentences[-1].end_fid
#     else:
#         stc_startt = float("inf")
#         stc_endt = -1
#     startt = myvideo.fid2sec(min(stc_startt, img_startt))
#     endt = myvideo.fid2sec(max(stc_endt, img_endt))
#     
#     print myvideo.filepath
#     subclip = VideoFileClip(myvideo.filepath).subclip(startt, endt)
# #     audioclip = AudioFileClip(audiopath).subclip(startt, endt)
# #     subclip.set_audio(audioclip)
# #     subclip.volumex(1.5)
# #     subclip.preview()
#     subclip_crop = vfx.crop(subclip, subline.linegroup.obj.tlx, subline.linegroup.obj.tly, subline.linegroup.obj.brx, subline.linegroup.obj.bry)
#     
#     
#     clipsrc = clipdir + "/" + filename + ".mp4"
#     cropsrc = clipdir + "/" + filename + "_crop.mp4"
#     subclip = CompositeVideoClip([subclip, audioclip]) 
#     subclip_crop = CompositeVideoClip([subclip_crop, audioclip])
#     subclip_crop.write_videofile(cropsrc, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...
#     subclip.write_videofile(clipsrc, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...
    
   
        
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
    write_update_time_script(html)
    write_highlight_current_script(html)
    html.writestring("$(document).ready(setInterval(updateTime, 1000)) ; \n" )

def write_update_time_script(html):
    html.writestring("function updateTime() {\n"
        "\tvar vtimes = []\n"
        "\tvar vids = document.getElementsByTagName(\"video\");\n"
        "\tfor (var i = 0; i < vids.length; i++) {\n"
        "\t\tvar vid = vids[i]\n"
        "\t\tif (!vid.paused) {\n"
        "\t\tvar startt = parseInt(vid.getAttribute(\"startt\"));\n"
        "\t\t\tvtimes.push(startt + vid.currentTime);\n"
        "\t\t}\n"
        "\t}\n"
        "\thighlightCurrent(vtimes);\n"
        "}\n")    
    
def write_highlight_current_script(html):

    html.writestring("function highlightCurrent(vtimes){\n"
        "\tvar links = document.getElementsByClassName(\"textlink\");\n"
        "\tvar colored = []\n"
        "\tfor (var i = 0; i < links.length; i++) {\n"
        "\t\tvar startt = links[i].getAttribute(\"startt\");\n"
        "\t\tvar endt = links[i].getAttribute(\"endt\");\n"
        "\t\tfor (var j = 0; j < vtimes.length; j++) {\n"
        "\t\t\tvideotime = vtimes[j];\n"
        "\t\t\tif (startt < videotime && videotime < endt) {\n"
        "\t\t\t\tcolored.push(i);\n"
        "\t\t}\n"
        "\t\t}\n"
        "\t}"
        "\tfor (var i = 0; i < links.length; i++) {\n"
        "\t\tlinks[i].style.backgroundColor = '#ffffff';\n"
        "\t}\n"
        "\tfor (var i = 0; i < colored.length; i++) {\n"
        "\t\tlinks[colored[i]].style.backgroundColor = '#72a8ff'\n"
        "\t}\n"
        "};\n");

    
    
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
    outdir = objdir #sys.argv[7] #objdir
    maindir = sys.argv[7] 
    
    maindir = os.path.relpath(maindir, outdir)
    print maindir
    
    collapsed_icon = maindir + "/figures/" + "arrow_collapsed_icon.png"
    expanded_icon = maindir + "/figures/" + "arrow_expanded_icon.png"
    zoomin_icon =  maindir + "/figures/" + "zoom_in.png"
    zoomout_icon =  maindir + "/figures/" + "zoom_out.png"
    
    if not os.path.exists(os.path.abspath(outdir)):
        os.makedirs(os.path.abspath(outdir))
    video = Video(videopath)
    figdir = outdir + "/figs"
    clipdir = outdir + "/clips"
     
    if not os.path.exists(os.path.abspath(figdir)):
        os.makedirs(os.path.abspath(figdir))
    
    if not os.path.exists(os.path.abspath(clipdir)):
        os.makedirs(os.path.abspath(clipdir))
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
     
    for subline in list_of_sublines:
        subline.write_video(clipdir, video)
     
    stylepath = maindir + "/visual_transcript.css"
    html = WriteHtml(outdir + "/visual_transcript.html",title, stylesheet =stylepath)

    html.writestring("<h1>%s</h1>\n"%title)
    html.writestring("<h3>%s</h3>\n"%author)

    html.opendiv(idstring="transcriptbutton")
    html.writestring("<button id=\"expand\" onclick=\"expandall()\">Expand all transcript</button>")
    html.writestring("<button id=\"expand\" onclick=\"collapseall()\">Collapse all transcript</button><br>")
    html.closediv()

    html.opendiv(idstring="summary")
    cur_stc_id = 0
    for sublinei in range(0, len(list_of_sublines)):
        subline = list_of_sublines[sublinei]
        
        if (len(subline.list_of_sentences) > 0):
            start_stc_id = subline.list_of_sentences[0].id
            """stand-alone sentences"""
            if (start_stc_id > cur_stc_id):
                html.opendiv(class_string = "c0")
                html.openp()
                for i in range(cur_stc_id, start_stc_id):
                    write_stc(html, list_of_sentences[i])
                    start_fid = list_of_sentences[i].start_fid
                    end_fid = list_of_sentences[i].end_fid
                html.closep()
                html.closediv()
                cur_stc_id = start_stc_id
        
        else: #subline.list_of_sentences == 0
            stc = list_of_sentences[cur_stc_id]
            """stand-alone sentences"""
            if (stc.subline is None and stc.end_fid < subline.obj.end_fid):
                html.opendiv(class_string="c0")
                html.openp()
                while(stc.subline is None and stc.end_fid < subline.obj.end_fid and cur_stc_id < len(list_of_sentences)-1):
                    write_stc(html, stc)
                    cur_stc_id += 1
                    stc = list_of_sentences[cur_stc_id]
                html.closep()
                html.closediv()
        
        """write subline"""
        write_subline(html, subline, figdir, clipdir, outdir, video)
        if (len(subline.list_of_sentences) > 0):
            cur_stc_id = subline.list_of_sentences[-1].id+1
    
    """stand-alone sentences"""
    if (cur_stc_id < len(list_of_sentences)):
        html.opendiv(class_string="c0")
        html.openp()
        for i in range(cur_stc_id, len(list_of_sentences)):
            write_stc(html, list_of_sentences[i])
            start_fid = list_of_sentences[i].start_fid
            end_fid = list_of_sentences[i].end_fid
        html.closep()
        html.closediv() #c0
        
    html.closediv() #summary
    
    """Writing Scripts"""        
    html.openscript()
    write_onready_script(html)
    for i in range(0, len(list_of_sublines)):
        lineid = list_of_sublines[i].line_id
        subid = list_of_sublines[i].sub_line_id
        write_arrowtoggle_script(html, lineid, subid)
        write_zoomtoggle_script(html, lineid, subid)
        write_showsection_script(html, lineid, subid)
        write_zoomvideo_script(html, lineid, subid, os.path.relpath(clipdir,outdir), os.path.relpath(figdir,outdir))
        write_videocontrol_script(html, lineid, subid)
        write_playvideo_script(html, lineid, subid)
    write_expandall_script(html)
    write_collapseall_script(html)
    html.closescript()
    
    html.closehtml()