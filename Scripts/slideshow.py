'''
Created on Nov 29, 2014

@author: hijungshin
'''

import sys
import numpy as np
import cv2
import util
from visualobjects import VisualObject
from writehtml import WriteHtml
from lecture import Lecture

def slide(obj, w, h):
    slide = np.ones((h,w,3), dtype=np.uint8) * 255
    objh, objw = obj.img.shape[:2]
    slide[obj.tly:obj.tly+objh, obj.tlx:obj.tlx+objw, :] = obj.img
    return slide

def make_slides(list_of_objs, w, h, slidedir):
   
    slides = []
    slidenames = []
    numslides = len(list_of_objs)
    prevobj = None
    numslide = 0
    for i in range(0, numslides):
        if prevobj is None:
            curobj = VisualObject.group([list_of_objs[i]], slidedir)
        else:
            curobj = VisualObject.group([list_of_objs[i], prevobj], slidedir)
        curslide = slide(curobj, w, h,)
        slides.append(curslide)
        slidename =  "/slide_"+str(numslide)+".png"
        util.saveimage(curslide, slidedir,  slidename)
        numslide += 1
        slidenames.append(slidedir + "/" + slidename)
        prevobj = curobj       
    return slides, slidenames

def make_notes(lec, list_of_ts):
    stc_idx = 0
    notes = []
    print 'num sentences', len(lec.list_of_stcs)
    for t in list_of_ts:
        paragraph = []
        while(lec.list_of_stcs[stc_idx][-1].endt < t):
            #write sentence
            paragraph = paragraph + lec.list_of_stcs[stc_idx]
            stc_idx += 1
            if (stc_idx >= len(lec.list_of_stcs)):
                break
        notes.append(paragraph)
    return notes
    
def write_notes_to_html(list_of_notes, html):
    html.writestring("<script>")
    html.writestring("""$(document).ready(function(){
                        var slide = $('#slide').bxSlider({
                            slideWidth: 1200,                
                            mode: 'fade', 
                            pagerCustom: '#slide-pager',
                            onSlideAfter: function(){
                            var current = slide.getCurrentSlide();\n""")
    html.writestring("switch(current){\n")
    for i in range(0, len(list_of_notes)):
        html.writestring("case %i:\n" %i)
        html.writestring("$('#slidetext').text(\"")
        for word in list_of_notes[i]:
            if not word.issilent:
                html.writestring(word.original_word + " ")
        html.writestring("\");break;\n")
    html.writestring("}\n}\n});\n});\n")
    html.writestring("</script>")
    
def write_slides_to_html(list_of_slidenames, html):
    html.writestring("<table border=3 align=center>")
    html.writestring("<tr><td width=1300 align=center>")
    html.writestring("<ul id = \"slide\">\n")
    for i in range(0, len(list_of_slidenames)):
        html.writestring("<li>")
        html.image(list_of_slidenames[i])
        html.writestring("</li>\n")
    html.writestring("</ul>\n")
    html.writestring("<p id = \"slidetext\" align=left>")
    html.writestring("</td></tr></table>")

def write_slideshow_script(html):
    html.writestring("""
        <!-- jQuery library (served from Google) -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
        <!-- bxSlider Javascript file -->
        <script src="../../../../../../../../Mainpage/js/bxslider/jquery.bxslider.min.js"></script>
        <!-- bxSlider CSS file -->
        <link href="../../../../../../../../Mainpage/js/bxslider/jquery.bxslider.css" rel="stylesheet" />\n""" )
    
def write_to_html(list_of_slidenames, list_of_notes, slidedir):
    html = WriteHtml(slidedir + "/slideshow.html", title="Slideshow", script=True)
    write_slideshow_script(html)
    write_notes_to_html(list_of_notes, html)
    html.openbody()
    write_slides_to_html(list_of_slidenames, html)
    html.closehtml()
            
        
if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    lec = Lecture(videopath, scriptpath)
    
    objdir = sys.argv[3]
    list_of_objs = VisualObject.objs_from_file(None, objdir)
    
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    h, w = panorama.shape[:2]
    
    slidedir = objdir + "/slides"
    slides, slidenames = make_slides(list_of_objs, w, h, slidedir)
    list_of_ts = [lec.video.fid2ms(obj.end_fid) for obj in list_of_objs]
    notes = make_notes(lec, list_of_ts) 
    
    write_to_html(slidenames, notes, slidedir)
    

            
        