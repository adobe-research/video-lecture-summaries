'''
Created on Jan 14, 2015

@author: hijungshin
'''

import sys
import lecturevisual
import util
from writehtml import WriteHtml
import process_aligned_json as pjson
from video import Video

def write_playvideo_script(html, url):
    html.writestring("function playvideo_at(sec){\n \
         var video  = document.getElementById(\"thevideo\");\n \
         var starturl = \"https://www.youtube.com/embed/%s?autoplay=1&amp;start=\"+sec +\"&amp\"; \n \
         video.src= starturl\n \
         }\n" %(url))
 
def write_stc(html, sentence):
    sec = int(sentence.startt/1000.0)
    html.writestring("<object id=\"textlink\" onclick=\"playvideo_at(%i)\">"%(sec))
    html.write_sentence(sentence)
    html.writestring("</object>")
    

def insertvideo(html, url):
    html.opendiv(idstring="vid")
    html.opendiv(idstring="ytplayer")
    html.writestring("<iframe id=\"thevideo\" width=\"600px\" height=\"500px\" frameborder=\"0\" allowfullscreen=\"1\" title=\"YouTube video player\" src=\"http://www.youtube.com/embed/%s?enablejsapi=1&amp;autoplay=0\"></iframe>"%(url))
    html.closediv()
    html.closediv()


if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    title = sys.argv[3]
    author = sys.argv[4]
    url = sys.argv[5]
    
    video = Video(videopath)
    
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
    outdir = video.videoname
    html = WriteHtml(outdir + "_youtube_test.html",title, stylesheet ="../Mainpage/youtube_test_video.css")
#     html.writestring("<h3>The following is a summary of a lecture video. You may click on the '+' buttons next to the figures in order to expand further details.</h3>")
    html.writestring("<h1>%s</h1>\n"%title)
    html.writestring("<h3>%s</h3>\n"%author)

    insertvideo(html, url)
    
    html.opendiv(idstring="summary")
    for stc in list_of_stcs:
        sec = int(stc[0].startt/1000.0)
        html.writestring("<object id=\"textlink\" onclick=\"playvideo_at(%i)\">"%(sec))
        html.write_list_of_words(stc)
        html.breakline()
        html.writestring("</object>")
        
    html.closediv() #summary
            
    html.openscript()
    write_playvideo_script(html, url)
    html.closescript()
    html.closehtml()