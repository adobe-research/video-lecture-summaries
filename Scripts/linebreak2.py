'''
Created on Nov 14, 2014

@author: hijungshin
'''

from visualobjects import VisualObject
import sys
import numpy as np
import cv2
from lecture import Lecture
from writehtml import WriteHtml
import util
import os
import processframe as pf
import operator
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
        self.linedir = self.objdir + "/lines2"
 
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
            html.paragraph_list_of_words(paragraph)
            html.figure(list_of_objs[obj_idx].imgpath, "Merged Figure %i" % nfig)
            
            nfig += 1    

    def computecost(self):        
        n = self.numobjs
        print 'totalcost[0]'
        self.totalcost[0] = linecost(self.list_of_objs[0:1]) # initial cost
        self.bestid[0][0] = 0
        
        for i in range(1, n):
            print '---------------computing totalcost[',i,']---------------------'
            min_cost = float("inf")
         
            add_to = [-1 for x in range(0, i)] # best line to add-to, at cut_j
            for j in range(max(0, i-1), i):
                print 'j = ' , j
                j_min_add_cost = float("inf")
                totalcost_j = self.totalcost[j] # j inclusive
                prevlines_j = get_opt_lines(self.list_of_objs, self.bestid, j) # lines cut upto j
                prevline_idx = 0
                for  prevline in prevlines_j:                    
#                     if j == (i-1):
#                         line_cost = 0
#                     else:
                    line_cost = linecost(self.list_of_objs[j+1:i+1])
                    add_cost =  addcost(prevline, self.list_of_objs[j+1:i+1]) # cost of adding items [j+1, i] inclusive to prevline
                    print 'linecost', line_cost, 'addcost', add_cost, 'linecost + addcost', line_cost + add_cost
                    add_cost = line_cost + add_cost 
                    if (add_cost < j_min_add_cost):
                        j_min_add_cost = add_cost
                        add_to[j] = prevline_idx
                    prevline_idx += 1
                print 'for j=', j, 'best add to is', add_to[j], 'with cost', j_min_add_cost
                
                newlinecost = linecost(self.list_of_objs[j+1:i+1]) # list_of_objs[j+1:i] inclusive on separate line
                if len(prevlines_j) > 0:
                    newlinecost += 0.0
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
            print 'best_add_to', best_add_to, 'previous_totalcost', self.totalcost[bestj]
            for k in range(bestj+1, i+1):
                self.bestid[i][k] = best_add_to 
            print 'bestid', self.bestid[i][0:i+1]
            util.showimages([self.list_of_objs[i].img])
            self.totalcost[i] = min_cost
        
    

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
    cost = 0
    for i in range(1, len(list_of_objs)):
        cost += addcost(list_of_objs[0:i], list_of_objs[i:i+1])
    return cost


def addcost(list_of_prev_objs, list_of_new_objs):
        if (len(list_of_prev_objs) == 0):
            print 'first object cost 1.0'
            return 1.0
        if len(list_of_new_objs) is None:
            return 0.0
        
        xgap2 = VisualObject.xgap_distance_new(list_of_prev_objs, list_of_new_objs)
        ygap2 = VisualObject.ygap_distance_list(list_of_prev_objs, list_of_new_objs)
        
        return xgap2 + ygap2
            
if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    stcdir = objdir + "/sentences"
    
    if not os.path.exists(os.path.abspath(stcdir)):
        os.makedirs(os.path.abspath(stcdir))
    
    lec = Lecture(videopath, scriptpath)
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
    breaker = LineBreaker(lec, img_objs, objdir, debug=False)
    line_objs = breaker.dynamic_lines()
    
    # for each stc assign object that belongs to them
#     stc_objs = [[] for i in range(0, len(lec.list_of_stcs))]
#     stc_obj_ids = [[] for i in range(0, len(lec.list_of_stcs))]
#     
#     obj_id = 0
#     for obj in img_objs:
#         max_score = -1.0*float("inf")
#         best_stc = 0
#         for i in range(0, len(lec.list_of_stcs)):
#             stc = lec.list_of_stcs[i]
#             score = obj_stc_distance(obj, stc, lec.video)
#             if score > max_score:
#                 max_score = score
#                 best_stc = i
#         stc_objs[best_stc].append(obj)
#         stc_obj_ids[best_stc].append(obj_id)
#         obj_id += 1
    
    html = WriteHtml(breaker.linedir + "/dynamic_linebreak_xgap_ygap.html", title="Linebreak2 with sentences", stylesheet="../Mainpage/summaries.css")
    html.opendiv(idstring="summary-container")
    breaker.write_to_html(html, objdir, list_of_objs=line_objs)
    html.closediv()
    html.closehtml()
    
#     new_objs = []
#     stc_figure_ids = []
#     for i in range(0, len(lec.list_of_stcs)):
#         stc = lec.list_of_stcs[i]
#         obj_ids_in_stc = stc_obj_ids[i]
# 
#         # get figure numbers that contain this object
#         figure_ids = []
#         max_end_fid = -1
#         for obj_id in obj_ids_in_stc:
#             figure_id = breaker.bestid[len(img_objs)-1][obj_id]
#             figure_ids.append(figure_id)
#             max_end_fid = max(max_end_fid, img_objs[obj_id].end_fid)
#         figure_ids = set(figure_ids)
#         stc_figure_ids.append(figure_ids)
#         #get figures
#         figure_lineobjs = []
#         for fid in figure_ids:
#             lineobj = line_objs[fid]
#             for member in lineobj.members:
#                 if member.end_fid <= max_end_fid:
#                     figure_lineobjs.append(member)
#         
#         stcobj = VisualObject.group(figure_lineobjs, stcdir)    
#         new_objs.append(stcobj)
#         
#     paragraph = []
#     for i in range(0, len(lec.list_of_stcs)):
#         stc = lec.list_of_stcs[i]
#         fig_ids = stc_figure_ids[i]
#         paragraph = paragraph + stc
#         if (i < len(lec.list_of_stcs) -1):
#             next_fig_ids = stc_figure_ids[i+1]
#             if (fig_ids != next_fig_ids):
#                 html.paragraph_list_of_words(paragraph)
#                 if (new_objs[i] is not None):
#                     html.image(new_objs[i].imgpath)
#                 paragraph = []
#         else:
#             html.paragraph_list_of_words(paragraph)
#             if (new_objs[i] is not None):
#                 html.image(new_objs[i].imgpath)
#             paragraph = []
# 
#     html.closehtml()
    
    
