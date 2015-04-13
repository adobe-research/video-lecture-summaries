'''
Created on Apr 13, 2015

@author: Valentina
'''

from sentence import Sentence
import sys
import util
import lecturevisual
from writehtml import WriteHtml

if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[5]
    scriptpath = sys.argv[3]
    outhtml = sys.argv[4]

    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    
    html = WriteHtml(outhtml)
    
    for i in range(0, len(list_of_sentences)-1):
        stc1 = list_of_sentences[i]
        stc2 = list_of_sentences[i+1]
        dist = Sentence.levenshtein_dist(stc1, stc2)
        l1 = len(stc1.getstring())
        l2 = len(stc2.getstring())
        maxl = max(l1,l2)
        if (dist < maxl/2.0):
            html.writestring("<font color=red>")
            html.paragraph_list_of_words(stc1.list_of_words)
            html.writestring("(%i:%i)" %(dist, maxl))
            html.writestring("</font>")
        else:
            html.paragraph_list_of_words(stc1.list_of_words)
    html.paragraph_list_of_words(list_of_sentences[-1].list_of_words)
    
    html.closehtml()
            