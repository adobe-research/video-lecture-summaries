'''
Created on Dec 1, 2014

@author: hijungshin
'''

from lecture import Lecture
from writehtml import WriteHtml
import sys


if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    outdir = sys.argv[3]
    
    
    lec = Lecture(videopath, scriptpath)
    
    html = WriteHtml(outdir + "/transcript.html", title="Sentence Timing", stylesheet="../Mainpage/summaries.css")
    for stc in lec.list_of_stcs:
        start_fid = lec.video.ms2fid(stc[0].startt)
        end_fid = lec.video.ms2fid(stc[-1].endt)
        html.writestring(str(start_fid))
        html.paragraph_list_of_words(stc)
        html.writestring(str(end_fid))
        html.breakline()
        
        