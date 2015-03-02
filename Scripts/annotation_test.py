'''
Created on Jan 21, 2015

@author: hijungshin
'''

from figure import Figure
import sys
import cv2
import util
from visualobjects import VisualObject
import numpy as np
from writehtml import WriteHtml

if __name__ == "__main__":
    objdir = sys.argv[1]
    list_of_objs = VisualObject.objs_from_file("None", objdir)
    
    linetxt = sys.argv[2]
    line_ids = util.stringlist_from_txt(linetxt)
    line_ids = util.strings2ints(line_ids)
    
    panorama = sys.argv[3]
    
    n_figures = len(np.unique(np.array(line_ids)))
    figuredir = objdir + "/figure_test"
    list_of_figures = Figure.getfigures(list_of_objs, line_ids, figuredir)
    
    html = WriteHtml(objdir + "/figures_test.html", "Figures")
    html.figure(panorama, width="800", caption="panorama view")
    html.opentable(border = 1)
    for i in range(0, n_figures):
        html.opentablerow()
        figure_i = []
        for fig in list_of_figures:
            if fig.main_id == i:
                figure_i.append(fig)
                
        j = 0
        for fig in figure_i:
            html.opentablecell()
            html.figure(fig.newobjpath, width="300", caption="Figure%i-%i"%(i, j))
            j += 1
            html.closetablecell()
        html.closetablecell()
    html.closetable()
    html.closehtml()
            