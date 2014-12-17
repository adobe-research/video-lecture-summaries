'''
Created on Dec 11, 2014

@author: hijungshin

Cost function :Sum of bounding box areas
'''

from visualobjects import VisualObject
import sys
import numpy as np
import cv2
from lecture import Lecture
from writehtml import WriteHtml
import util
import os
from display_transcript import obj_stc_distance

class LineBreaker:
    def __init__(self, lec, list_of_objs, objdir="temp", debug=False):
        self.lec = lec
        self.list_of_objs = list_of_objs
        self.numobjs = len(list_of_objs)
        self.line_objs = []
        n = len(list_of_objs)
        self.totalcost = [float("inf") for x in range(n)]
        self.bestid = [[-1 for x in range(n)] for x in range(n)]
        self.cuts = [0 for x in range(n)]
        self.debug = debug
        self.objdir = objdir
        self.linedir = self.objdir + "/lines3"
 
    def dynamic_lines(self):
        self.computecost()
        bestlines = get_opt_lines(self.list_of_objs, self.bestid, self.numobjs-1)
        for line in bestlines:
            lineobj = VisualObject.group(line, self.linedir)
            self.line_objs.append(lineobj)
        VisualObject.write_to_file(self.linedir + "/obj_infot.xt", self.line_objs)
        return self.line_objs
      
    
    def write_to_html(self, html, objdir, list_of_objs=None):
        if (list_of_objs is None):
            list_of_objs = self.line_objs
        nfig = 1
        obj_idx = 0
        for obj_idx in range(0, len(list_of_objs)):
            paragraph = []
            obj = list_of_objs[obj_idx]
            html.paragraph_list_of_words(paragraph)
            cost = linecost(list_of_objs[obj_idx:obj_idx+1])
            width = obj.width
            height = obj.height
            html.figure(list_of_objs[obj_idx].imgpath, "Merged Figure %i, Cost %f, width %i, height %i" % (nfig, cost, width, height))
            nfig += 1    

    def computecost(self):        
        n = self.numobjs
        self.totalcost[0] = linecost(self.list_of_objs[0:1]) 
        self.bestid[0][0] = 0
        
        for i in range(1, n):

            print '---------------computing totalcost[',i,']---------------------'
            min_cost = float("inf")
            add_to = [-1 for x in range(0, i)] # best line to add-to, at cut_j
            for j in range(0, i):
                print 'j = ' , j
                j_min_add_cost = float("inf")
                totalcost_j = self.totalcost[j] # j inclusive
                prevlines_j = get_opt_lines(self.list_of_objs, self.bestid, j) # lines cut upto j
                prevline_idx = 0
                for  prevline in prevlines_j:          
                    add_cost = linecost(prevline + self.list_of_objs[j+1:i+1]) # cost of putting strokes  [j+1, i] with prevline
                    add_cost -= linecost(prevline)
                    
                    if (add_cost < j_min_add_cost):
                        j_min_add_cost = add_cost
                        add_to[j] = prevline_idx
                    prevline_idx += 1
                print 'for j=', j, 'best add to is', add_to[j], 'with cost', j_min_add_cost
                
                newlinecost = linecost(self.list_of_objs[j+1:i+1]) # list_of_objs[j+1:i] inclusive on separate line
                print 'newline cost', newlinecost
                if (newlinecost < j_min_add_cost):
                    j_min_add_cost = newlinecost
                    add_to[j] = prevline_idx 
                    print '-------------------separate line is actually the best--------- with cost', newlinecost
                   
                cost_j = totalcost_j + j_min_add_cost
                if (cost_j < min_cost):
                    min_cost = cost_j
                    bestj = j
                    best_add_to = add_to[j]
            
               
                    
            print 'best j is', bestj
#             print 'bestline' , bestline #j-th cut's best_add_to line
#             bestprevlines_atj = get_opt_lines(self.list_of_objs, self.bestid, bestj)
#             bestprevline = bestprevlines_atj[best_add_to]               
#             temp = VisualObject.group(bestprevline, "temp")
#             util.showimages([temp.img], "bestline")
                
            # update bestid
            self.bestid[i][0:bestj+1] = self.bestid[bestj][0:bestj+1] #up to bestj inclusive, retain segmentation of bestj
            print 'best_add_to', best_add_to
            for k in range(bestj+1, i+1):
                self.bestid[i][k] = best_add_to 
            print 'bestid', self.bestid[i][0:i+1]
#             util.showimages([self.list_of_objs[i].img])
            self.totalcost[i] = min_cost
#             print self.totalcost[i]
#             prevlines = get_opt_lines(self.list_of_objs, self.bestid, i)
#             lineid = 0
#             for prevline in prevlines:
#                 temp = VisualObject.group(prevline, "temp")
#                 util.showimages([temp.img], "line %i" %lineid)
#                 lineid += 1
            
        
    

def get_opt_lines(list_of_objs, bestid, j):
    # considering optimal segmentation up to and including item j, where do each item belong?
    line_ids = bestid[j][0:j+1]

    nlines = len(np.unique(line_ids))
    optlines = [[] for x in range(0, nlines)]
    objid = 0
    print 'num prev lines', len(optlines), 'line ids', line_ids
    for obj in list_of_objs[0:j+1]:
        optlines[line_ids[objid]].append(obj)
        objid += 1
    return optlines #list of list_of_objs

def linecost(list_of_objs):
    tlx, tly, brx, bry = VisualObject.bbox(list_of_objs)
    width = brx - tlx + 1
    height = bry - tly + 1
    return pow((width * height), 0.75)

   
if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    
    lec = Lecture(videopath, None)
    print lec.video.fps
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
    breaker = LineBreaker(lec, img_objs, objdir, debug=True)
    line_objs = breaker.dynamic_lines()
    html = WriteHtml(breaker.linedir + "/dynamic_linebreak3.html", title="Linebreak3.py", stylesheet="../Mainpage/summaries.css")
    html.opendiv(idstring="summary-container")
    breaker.write_to_html(html, objdir, list_of_objs=line_objs)
    html.closediv()
    html.closehtml()
    
