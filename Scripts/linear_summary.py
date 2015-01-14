'''
Created on Nov 2, 2014

@author: hijungshin
'''

import sys
from lecture import Lecture
from visualobjects import VisualObject
from writehtml import WriteHtml
import util
from figure import Figure


class Sentence:
    def __init__(self, list_of_words):
        self.list_of_words = list_of_words


class Summary:
    def __init__(self, lec):
        self.lec = lec
        



if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    linetxt = sys.argv[4]
    
    lec = Lecture(videopath, scriptpath)
    list_of_objs = VisualObject.objs_from_file(lec.video, objdir)
    line_ids = util.stringlist_from_txt(linetxt)
    line_ids = util.strings2ints(line_ids)
    
    figuredir = objdir + "/line_figures_v2"
    list_of_figures = Figure.getfigures(list_of_objs, line_ids, figuredir)
    
    
    lec.assign_figs_to_stcs(list_of_figures)
    
    html = WriteHtml(objdir + "/linear_summary_v2.html", "Linear Summary", stylesheet="../Mainpage/summaries.css")
    html.figure_script(list_of_figures, lec)
    html.closehtml()
    